import pytest
from services.snippet_reconstructor import reconstruct_snippet
from models.response import SnippetAnchor

def test_reconstruct_snippet_success():
    content = "This is a long document with some very interesting information about AI. It specifically discusses snippet extraction."
    anchor = SnippetAnchor(
        head="This is a long document",
        tail="about AI.",
        relevance_score=0.9
    )
    expected = "This is a long document with some very interesting information about AI."
    assert reconstruct_snippet(content, anchor) == expected

def test_reconstruct_snippet_short_passage():
    content = "Short passage here."
    # Head and tail identical
    anchor = SnippetAnchor(
        head="Short passage here.",
        tail="Short passage here.",
        relevance_score=1.0
    )
    assert reconstruct_snippet(content, anchor) == "Short passage here."

def test_reconstruct_snippet_head_not_found():
    content = "Some content here."
    anchor = SnippetAnchor(
        head="Non-existent head",
        tail="here.",
        relevance_score=0.5
    )
    assert reconstruct_snippet(content, anchor) is None

def test_reconstruct_snippet_tail_not_found():
    content = "Some content here."
    anchor = SnippetAnchor(
        head="Some content",
        tail="Non-existent tail",
        relevance_score=0.5
    )
    assert reconstruct_snippet(content, anchor) is None

def test_reconstruct_snippet_tail_before_head():
    content = "The tail comes first. Then the head."
    # The logic should look for tail AFTER head
    anchor = SnippetAnchor(
        head="Then the head.",
        tail="The tail comes first.",
        relevance_score=0.5
    )
    assert reconstruct_snippet(content, anchor) is None
