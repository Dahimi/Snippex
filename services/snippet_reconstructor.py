from typing import Optional
from models.response import SnippetAnchor

def reconstruct_snippet(content: str, anchor: SnippetAnchor) -> Optional[str]:
    """
    Locates the passage in source content using head and tail anchor strings.
    Returns None if either anchor is not found (LLM hallucinated).
    """
    # Character-for-character find
    start = content.find(anchor.head)
    if start == -1:
        return None
        
    # Find tail AFTER the start of the head
    # This allows for short passages where head and tail might overlap
    end = content.find(anchor.tail, start)
    if end == -1:
        return None
        
    # The snippet is from start of head to end of tail
    snippet_text = content[start : end + len(anchor.tail)]
    return snippet_text.strip()
