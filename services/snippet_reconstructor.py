import logging
import regex as re
from typing import Optional, Tuple
from models.response import SnippetAnchor

logger = logging.getLogger(__name__)

# Maximum characters between head_start and tail_end before we consider it a false positive
_MAX_SNIPPET_CHARS = 1000

# Stage names returned by _find_fuzzy
STAGE_EXACT = "exact"
STAGE_LEVENSHTEIN = "levenshtein"
STAGE_JACCARD = "jaccard"


def _normalize_text(text: str) -> str:
    """Standardize quotes, collapse whitespace."""
    if not text:
        return ""
    text = text.replace('\u201c', '"').replace('\u201d', '"').replace('\\"', '"').replace('\u2018', '"').replace('\u2019', '"')
    return " ".join(text.split()).strip()


def _jaccard_token_similarity(a: str, b: str) -> float:
    """Word-level Jaccard similarity between two strings."""
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _snap_boundaries(content: str, start: int, end: int) -> Tuple[int, int]:
    """Expand match to include adjacent markdown/formatting characters."""
    fmt_chars = set('*_#~>\"\u201c\u201d\u2018\u2019')
    while start > 0 and content[start - 1] in fmt_chars:
        start -= 1
    while end < len(content) and content[end] in fmt_chars:
        end += 1
    return start, end


def _find_fuzzy(content: str, anchor: str, start_index: int = 0) -> Tuple[int, int, Optional[str]]:
    """
    Find anchor in content using three stages of increasing fuzziness.
    Returns (start, end, stage) where stage is STAGE_EXACT / STAGE_LEVENSHTEIN /
    STAGE_JACCARD, or (-1, -1, None) on failure.
    """
    # ------------------------------------------------------------------ #
    # Stage 1 — exact match on raw content
    # ------------------------------------------------------------------ #
    idx = content.find(anchor, start_index)
    if idx != -1:
        return idx, idx + len(anchor), STAGE_EXACT

    norm_anchor = _normalize_text(anchor)
    if not norm_anchor:
        return -1, -1, None

    # ------------------------------------------------------------------ #
    # Stage 2 — Levenshtein fuzzy match across the full remaining content.
    # ------------------------------------------------------------------ #
    max_errors = max(1, len(norm_anchor) // 6)
    fuzzy_pattern = f"(?b)(?:{re.escape(norm_anchor)}){{e<={max_errors}}}"

    match = re.search(fuzzy_pattern, content[start_index:])
    if match:
        start = start_index + match.start()
        end = start_index + match.end()
        start, end = _snap_boundaries(content, start, end)
        logger.info("Stage 2 (Levenshtein) matched anchor %r", anchor[:40])
        return start, end, STAGE_LEVENSHTEIN

    # ------------------------------------------------------------------ #
    # Stage 3 — Token Jaccard sliding window
    # ------------------------------------------------------------------ #
    anchor_words = norm_anchor.split()
    n_words = len(anchor_words)
    if n_words < 2:
        return -1, -1, None

    content_words = content[start_index:].split()
    best_score = 0.0
    best_word_offset = -1

    for i in range(len(content_words) - n_words + 1):
        window_words = content_words[i: i + n_words]
        score = _jaccard_token_similarity(" ".join(anchor_words), " ".join(window_words))
        if score > best_score:
            best_score = score
            best_word_offset = i

    if best_score >= 0.65 and best_word_offset != -1:
        matched_text = " ".join(content_words[best_word_offset: best_word_offset + n_words])
        char_idx = content.find(content_words[best_word_offset], start_index)
        if char_idx != -1:
            end = char_idx + len(matched_text)
            start, end = _snap_boundaries(content, char_idx, end)
            logger.info("Stage 3 (Jaccard %.2f) matched anchor %r", best_score, anchor[:40])
            return start, end, STAGE_JACCARD

    return -1, -1, None


class ReconstructionResult:
    """Outcome of a single anchor-pair reconstruction, including telemetry."""
    __slots__ = ("text", "head_stage", "tail_stage", "matched_head", "matched_tail")

    def __init__(
        self,
        text: Optional[str],
        head_stage: Optional[str],
        tail_stage: Optional[str],
        matched_head: Optional[str] = None,
        matched_tail: Optional[str] = None,
    ):
        self.text = text
        self.head_stage = head_stage
        self.tail_stage = tail_stage
        # The actual text found in the source — only differs from the LLM anchor
        # when a fuzzy stage was used (useful for measuring LLM anchor accuracy).
        self.matched_head = matched_head
        self.matched_tail = matched_tail

    @property
    def succeeded(self) -> bool:
        return self.text is not None


def reconstruct_snippet(content: str, anchor: SnippetAnchor) -> ReconstructionResult:
    """
    Locate and return the passage in source content bounded by head/tail anchors.
    Always returns a ReconstructionResult — check .succeeded or .text for None.
    """
    head_start, head_end, head_stage = _find_fuzzy(content, anchor.head)

    if head_start == -1:
        logger.warning("Head anchor not found: %r", anchor.head[:60])
        return ReconstructionResult(None, None, None)

    matched_head = content[head_start:head_end]

    tail_start, tail_end, tail_stage = _find_fuzzy(content, anchor.tail, head_start)

    if tail_start == -1:
        logger.warning("Tail anchor not found: %r", anchor.tail[:60])
        return ReconstructionResult(None, head_stage, None, matched_head=matched_head)

    matched_tail = content[tail_start:tail_end]

    if tail_end < head_start:
        logger.warning("Tail found before head — skipping anchor pair")
        return ReconstructionResult(None, head_stage, tail_stage, matched_head, matched_tail)

    # Span guard only applies to fuzzy matches
    if head_stage != STAGE_EXACT or tail_stage != STAGE_EXACT:
        span = tail_end - head_start
        if span > _MAX_SNIPPET_CHARS:
            logger.warning(
                "Fuzzy span too long (%d chars) for anchor head=%r — rejecting",
                span, anchor.head[:40]
            )
            return ReconstructionResult(None, head_stage, tail_stage, matched_head, matched_tail)

    return ReconstructionResult(
        content[head_start:tail_end].strip(),
        head_stage,
        tail_stage,
        matched_head,
        matched_tail,
    )
