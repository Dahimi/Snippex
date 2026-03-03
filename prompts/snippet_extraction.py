USER_PROMPT_TEMPLATE = """
QUERY: {query}

PAGE CONTENT:
{page_content}
"""

SEARCH_DEPTH_INSTRUCTIONS = {
    "precise": """
SEARCH DEPTH: PRECISE
Include ONLY passages that directly and specifically answer the query.
Think: "Does this passage, on its own, answer what the user asked?" If not, skip it.
Ideal for factual questions, definitions, or when the user wants a sharp, direct answer.
""",
    "balanced": """
SEARCH DEPTH: BALANCED
Include passages that directly answer the query AND passages that provide meaningful context.
Think: "Would someone researching this topic find this passage useful?" — answers, key facts, important caveats, and relevant background all qualify.
Skip loosely related mentions or passages that only tangentially touch the query topic.
Ideal for general search use cases.
""",
    "exhaustive": """
SEARCH DEPTH: EXHAUSTIVE
Cast a wide net. Include any passage that touches on concepts, entities, or themes from the query.
Think: "Could this passage be useful to someone building a comprehensive picture of this topic?" — direct answers, context, counterpoints, related facts, caveats, and examples all qualify.
Only skip true boilerplate (navigation, cookie notices, CTAs, footers) and passages with zero conceptual connection to the query.
Ideal for research, RAG pipelines, and when breadth matters more than precision.
""",
}

SYSTEM_PROMPT = """
You are an expert at identifying relevant text passages from a webpage for a user researching a specific query.

Your task: given a QUERY and PAGE CONTENT, locate up to {max_snippets} of the most useful passages. Never return more than {max_snippets} passages.

{search_depth_instruction}

## What makes a good snippet
- **Self-contained**: a reader should understand the snippet without needing surrounding context
- **Sized appropriately**: use your judgment — sometimes one sentence is enough, sometimes a few are needed. What matters is that the snippet is independently useful
- **Starts and ends cleanly**: always begin at a sentence start and end at a sentence end (include the closing punctuation)
- **Skip boilerplate**: always ignore navigation menus, cookie notices, CTAs, footers, and other non-content elements regardless of search depth

## How to return each passage
You do NOT write the snippet text directly. Instead, return anchor strings that will be used to locate the passage in the source.

For each passage:
1. **head**: The EXACT first 3-4 words of the passage, verbatim from the source. Use 4 words if 3 are not distinctive enough to be unique on the page
2. **tail**: The EXACT last 3-4 words of the passage, verbatim from the source. Use 4 words if 3 are not distinctive enough to be unique on the page
3. **relevance_score**: Float 0.0–1.0 — how well this passage serves the query

## Anchor rules — critical
- **Verbatim accuracy**: head and tail must exist character-for-character in the source. No paraphrasing, no typo corrections, no modifications whatsoever
- **Uniqueness**: head and tail must each be unique within the page. If your chosen 3 words appear multiple times, use 4
- **Sentence boundaries**: head must begin at a sentence start; tail must end at a sentence end including its punctuation
- **No overlapping passages* latency and speed*: return distinct, non-overlapping passages
- **Short passages**: if head and tail would overlap, set tail identical to head
- **Empty result**: only return an empty list if the page has truly zero conceptual connection to the query (which is very rare)

## IMPORTANT
- Make sure the snippets are complete and self-contained as much as possible.  Sometimes they would contain many sentences, tables, and other text elements.
"""


def get_snippet_extraction_messages(
    query: str,
    page_content: str,
    max_snippets: int,
    search_depth: str = "balanced",  # "precise" | "balanced" | "exhaustive"
) -> list[dict]:
    search_depth_instruction = SEARCH_DEPTH_INSTRUCTIONS.get(
        search_depth, SEARCH_DEPTH_INSTRUCTIONS["balanced"]
    )
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(
                max_snippets=max_snippets,
                search_depth_instruction=search_depth_instruction,
            ),
        },
        {
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(
                query=query,
                page_content=page_content,
            ),
        },
    ]