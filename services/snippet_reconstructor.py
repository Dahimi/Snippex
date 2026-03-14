import logging
import regex as re
import string
from typing import Optional, Tuple
from models.response import SnippetAnchor

logger = logging.getLogger(__name__)

def _normalize_text(text: str) -> str:
    """
    Normalizes text for fuzzy matching by:
    1. Standardizing quotes.
    2. Collapsing all whitespace to single spaces.
    3. Stripping leading/trailing whitespace.
    """
    if not text:
        return ""
    # Standardize various curly/escaped quotes to standard double quote
    text = text.replace('“', '"').replace('”', '"').replace('\\"', '"').replace("'", '"')
    # Collapse whitespace
    return " ".join(text.split()).strip()

def _find_fuzzy(content: str, anchor: str, start_index: int = 0) -> Tuple[int, int]:
    """
    Attempts to find an anchor in the content using multiple stages of increasing fuzziness.
    Returns (start_index, end_index) or (-1, -1) if not found.
    """
    # Stage 1: Strict match
    idx = content.find(anchor, start_index)
    if idx != -1:
        return idx, idx + len(anchor)

    # Stage 2: Truly Fuzzy Match with 'regex' library
    # This is the "smart" stage. We allow a small number of errors (approx 15-20% of length)
    # This handles missing markdown markers, slight typos, and punctuation variations.
    print("Using fuzzy matching stage 2 for anchor: ", anchor)
    norm_anchor = _normalize_text(anchor)
    if not norm_anchor:
        return -1, -1
        
    # We use a distance of e<=min(8, 15% of length)
    max_errors = max(1, len(norm_anchor) // 6)
    # (?b) = best match (lowest error count)
    # We search for the anchor but allow some "errors" which include missing/extra symbols.
    fuzzy_pattern = f"(?b)(?:{re.escape(norm_anchor)}){{e<={max_errors}}}"
    
    match = re.search(fuzzy_pattern, content[start_index:])
    if match:
        start, end = start_index + match.start(), start_index + match.end()
        # Stage 4: Boundary Snapping (Rule-based cleanup)
        # If we found a fuzzy match, try to expand slightly to include adjacent symbols 
        # (like ** or quotes) that the LLM might have missed but are clearly part of the boundary.
        
        # Snap start backwards: include non-alphanumeric chars that aren't paragraph/sentence breaks
        while start > 0 and content[start-1] in "*_#~>\"'“‘" and content[start-1] not in ".!?":
            start -= 1
        # Snap end forwards: include non-alphanumeric chars
        while end < len(content) and content[end] in "*_#~>\"'”’" and content[end] not in ".!?":
            end += 1
            
        return start, end

    # Stage 3: Flexible word-based match (fallback)
    # Search for the anchor's words separated by any whitespace/punctuation variation.
    pattern_parts = [re.escape(word) for word in norm_anchor.split()]
    flexible_pattern = r"[\s\W]*".join(pattern_parts)
    print("Using fuzzy matching stage 3 for anchor: ", anchor)
    match = re.search(flexible_pattern, content[start_index:])
    if match:
        start, end = start_index + match.start(), start_index + match.end()
        # Snap here too
        while start > 0 and content[start-1] in "*_#~>\"'“‘" and content[start-1] not in ".!?":
            start -= 1
        while end < len(content) and content[end] in "*_#~>\"'”’" and content[end] not in ".!?":
            end += 1
        print("Got number of results : ", len(raw_results))
        return start, end

    return -1, -1

def reconstruct_snippet(content: str, anchor: SnippetAnchor) -> Optional[str]:
    """
    Locates the passage in source content using head and tail anchor strings.
    Uses multi-stage fuzzy matching to handle minor variations.
    Returns None if either anchor is truly not found.
    """
    head_start, head_end = _find_fuzzy(content, anchor.head)
    
    if head_start == -1:
        logger.error(f"Head anchor not found: {repr(anchor.head)}")
        return None
        
    # Find tail AT OR AFTER the start of the head
    # Use head_start instead of head_end to handle single-word snippets
    tail_start, tail_end = _find_fuzzy(content, anchor.tail, head_start)
    
    if tail_start == -1:
        logger.error(f"Tail anchor not found: {repr(anchor.tail)}")
        return None
        
    # Ensure the tail ends at or after the head starts
    if tail_end < head_start:
        logger.error(f"Tail {repr(anchor.tail)} found BEFORE head {repr(anchor.head)}")
        return None

    # The snippet is from start of head to end of tail
    snippet_text = content[head_start : tail_end]
    return snippet_text.strip()
