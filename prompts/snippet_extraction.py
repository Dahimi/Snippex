USER_PROMPT_TEMPLATE = """
QUERY: {query}

PAGE CONTENT:
{page_content}
"""

SHARED_EXAMPLE = """
## Example (all modes) — don't stop at the first relevant sentence

QUERY: "what is the transformer architecture"

PAGE CONTENT (excerpt):
"...The Transformer architecture was introduced in the 2017 paper 'Attention Is All You Need' by Vaswani et al. Unlike RNNs, Transformers process all tokens in parallel using a mechanism called self-attention, which allows each token to directly attend to every other token in the sequence. This makes training significantly faster and enables the model to capture long-range dependencies more effectively. The architecture consists of an encoder and a decoder, each built from stacked layers of multi-head attention and feed-forward networks. Layer normalization and residual connections are applied throughout to stabilize training..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "The Transformer architecture was introduced",
      "tail": "to stabilize training.",
      "relevance_score": 0.97
    }
  ]
}

WHY: The snippet runs from the definition through all the architectural details. Stopping after the first sentence ("...by Vaswani et al.") would be topically relevant but informationally thin — it names the paper but gives the reader nothing to work with about what the architecture actually is or how it works.

BAD OUTPUT (do not do this):
{
  "anchors": [
    {
      "head": "The Transformer architecture was",
      "tail": "Vaswani et al.",
      "relevance_score": 0.97
    }
  ]
}

WHY IT'S BAD: One sentence that only names the paper and year. The user asked what the architecture IS — this doesn't tell them.
"""

# ─── PRECISE MODE EXAMPLES ────────────────────────────────────────────────────

PRECISE_EXAMPLES = """
## Example P-1 — one fact, one sentence

QUERY: "what year was Python first released"

PAGE CONTENT (excerpt):
"...Python was first released in 1991 by Guido van Rossum. It was designed to emphasize code readability and simplicity. Since then, Python has grown into one of the most widely used programming languages in the world, with major versions including Python 2 (2000) and Python 3 (2008). Today it powers everything from web backends to machine learning pipelines..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "Python was first released",
      "tail": "Guido van Rossum.",
      "relevance_score": 0.99
    }
  ]
}

WHY: The query is a single specific fact (the year). The first sentence contains the complete, unambiguous answer. Everything after it — Python's growth, major versions, use cases — is interesting but does not answer the question. Precise mode stops at the exact fact.

---

## Example P-2 — definition query, return just the definition

QUERY: "what is gradient descent"

PAGE CONTENT (excerpt):
"...Before diving into optimization algorithms, it helps to understand the mathematical foundations of learning. Gradient descent is an iterative optimization algorithm used to minimize a function by moving in the direction of the steepest descent, as defined by the negative of the gradient. It is the backbone of training neural networks. There are three main variants: batch gradient descent, stochastic gradient descent (SGD), and mini-batch gradient descent. Each has different tradeoffs in terms of speed and stability..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "Gradient descent is an iterative",
      "tail": "of the gradient.",
      "relevance_score": 0.99
    }
  ]
}

WHY: The query asks for a definition. The definition is fully contained in one sentence. The intro before it ("Before diving into...") is navigational fluff. The content after it (variants, tradeoffs) goes beyond what was asked. Precise mode extracts exactly the definition and nothing more.

BAD OUTPUT (do not do this):
{
  "anchors": [
    {
      "head": "Before diving into optimization",
      "tail": "speed and stability...",
      "relevance_score": 0.92
    }
  ]
}

WHY IT'S BAD: Starts with an irrelevant intro sentence and drags in the variants section which wasn't asked for. Precise mode should be surgical.

---

## Example P-3 — numerical/factual query with a single answer buried mid-paragraph

QUERY: "what is the context window of Claude 3 Opus"

PAGE CONTENT (excerpt):
"...Anthropic has made significant strides in expanding context windows across its model family. Claude 3 Opus supports a context window of 200,000 tokens, making it one of the largest available in any commercial model. For comparison, GPT-4 Turbo offers 128,000 tokens. Researchers working with very long documents, codebases, or legal filings benefit most from these extended windows..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "Claude 3 Opus supports",
      "tail": "any commercial model.",
      "relevance_score": 0.99
    }
  ]
}

WHY: The answer is two sentences — the number itself plus the qualitative context ("one of the largest"). That second sentence is worth including because it gives the number meaning. The comparison to GPT-4 and the use-case sentence that follows are not needed to answer the specific question asked.
"""

# ─── BALANCED MODE EXAMPLES ───────────────────────────────────────────────────

BALANCED_EXAMPLES = """
## Example B-1 — skip irrelevant intro, capture full explanation

QUERY: "how does self-attention work in transformers"

PAGE CONTENT (excerpt):
"...Transformers were introduced in 2017 and have since reshaped NLP. The key innovation is self-attention: for each token in the input, the model computes a weighted sum of all other tokens' representations, where the weights reflect how relevant each token is to the current one. These weights are derived from dot products between query, key, and value vectors, which are learned during training. This allows the model to capture dependencies regardless of distance in the sequence. In practice, multiple attention heads run in parallel, each learning to attend to different types of relationships..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "The key innovation is",
      "tail": "types of relationships...",
      "relevance_score": 0.95
    }
  ]
}

WHY: Balanced mode skips the intro sentence ("Transformers were introduced in 2017...") — it adds no value for this query. The snippet starts at the actual explanation and runs through the multi-head attention detail. That full paragraph is what someone needs to understand how self-attention works.

---

## Example B-2 — multiple distinct snippets from different sections

QUERY: "pros and cons of microservices architecture"

PAGE CONTENT (excerpt):
"...Microservices have become a dominant pattern in backend engineering. The benefits are significant: independent deployability means teams can release services without coordinating with others; fault isolation ensures one failing service doesn't bring down the whole system; and technology flexibility allows each service to use the best tool for its job.

However, microservices introduce real operational complexity. Service discovery, distributed tracing, and inter-service authentication all require dedicated infrastructure. Latency increases when a single user request fans out across five or six network calls. Teams new to distributed systems often underestimate this overhead..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "The benefits are significant:",
      "tail": "best tool for its job.",
      "relevance_score": 0.93
    },
    {
      "head": "However, microservices introduce real",
      "tail": "underestimate this overhead...",
      "relevance_score": 0.91
    }
  ]
}

WHY: The query explicitly asks for pros AND cons — two distinct sections cover them. Both are extracted as separate snippets. The opening sentence ("Microservices have become a dominant pattern...") is skipped because it is context-setting with no informational value for the query.

---

## Example B-3 — comparison query, capture the comparison table/breakdown

QUERY: "difference between RAG and fine-tuning"

PAGE CONTENT (excerpt):
"...There is ongoing debate in the ML community about when to use RAG versus fine-tuning. Both approaches adapt LLMs to specific use cases, but they do so differently. RAG (Retrieval-Augmented Generation) keeps the model weights frozen and instead retrieves relevant documents at inference time to provide context. This makes it easy to update the knowledge base without retraining. Fine-tuning, by contrast, updates the model weights directly on a domain-specific dataset, which can produce more fluent and stylistically consistent outputs but requires retraining whenever the underlying knowledge changes. RAG tends to be preferred when knowledge is dynamic or frequently updated; fine-tuning is better when the task requires a specific tone, format, or reasoning style the base model lacks..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "Both approaches adapt LLMs",
      "tail": "reasoning style the base model lacks...",
      "relevance_score": 0.97
    }
  ]
}

WHY: The query asks for the difference between two things. The entire comparison is one cohesive passage — splitting it would lose the contrast. The correct snippet captures the full comparison from "Both approaches..." to the final sentence that summarizes when to use each. The opening debate sentence is skipped as it's scene-setting without substance.
"""

# ─── EXHAUSTIVE MODE EXAMPLES ─────────────────────────────────────────────────

EXHAUSTIVE_EXAMPLES = """
## Example E-1 — the intro trap: never stop at the heading

QUERY: "top AI companies 2024"

PAGE CONTENT (excerpt):
"...The AI industry has seen explosive growth in recent years, with both established tech giants and nimble startups competing for dominance. Here are the top AI companies shaping 2024:

1. OpenAI — Known for GPT-4 and ChatGPT, OpenAI leads in consumer and enterprise AI adoption with over 100 million users.
2. Anthropic — Founded by former OpenAI researchers, Anthropic focuses on AI safety and produces the Claude model family.
3. Google DeepMind — The combined AI research arm of Google, responsible for Gemini, AlphaFold, and fundamental RL research.
4. Mistral AI — A Paris-based startup offering high-performance open-weight models, gaining rapid traction in Europe.
5. xAI — Elon Musk's AI venture, developing the Grok model with a focus on real-time knowledge via X integration.

Beyond these leaders, companies like Cohere, AI21 Labs, and Inflection are carving out enterprise and vertical niches..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "The AI industry has",
      "tail": "vertical niches...",
      "relevance_score": 0.95
    }
  ]
}

WHY — THE INTRO TRAP: "Here are the top AI companies shaping 2024" is the most query-similar sentence but contains zero usable information. The correct snippet starts at the intro paragraph and runs through the last list item and closing sentence. In exhaustive mode, if a section is relevant, capture it fully.

BAD OUTPUT (do not do this):
{
  "anchors": [
    {
      "head": "Here are the top",
      "tail": "shaping 2024:",
      "relevance_score": 0.95
    }
  ]
}

WHY IT'S BAD: Reconstructs to one heading line. The user learns nothing. This is the most common failure mode.

---

## Example E-2 — capture multiple relevant sections across the page

QUERY: "Python vs JavaScript for backend development"

PAGE CONTENT (excerpt):
"...Python has long been a favourite for backend development, particularly in data-heavy and ML-adjacent applications. Its ecosystem — Django, FastAPI, Flask — provides mature tooling for building APIs and web services. Python's readability and strong typing support (via type hints) make large codebases easier to maintain.

JavaScript (via Node.js) brings a different set of strengths. Its non-blocking, event-driven architecture makes it exceptionally well-suited for I/O-heavy workloads like real-time applications, chat systems, and streaming APIs. The ability to share code between frontend and backend is a genuine productivity advantage for full-stack teams.

In terms of raw performance, Node.js generally outperforms Python for high-concurrency scenarios, while Python tends to win on CPU-bound tasks when paired with async frameworks or offloaded to C extensions. For teams already using JavaScript on the frontend, Node.js reduces context-switching. For data science or ML integration, Python is the clear choice..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "Python has long been",
      "tail": "easier to maintain.",
      "relevance_score": 0.92
    },
    {
      "head": "JavaScript (via Node.js) brings",
      "tail": "full-stack teams.",
      "relevance_score": 0.91
    },
    {
      "head": "In terms of raw performance,",
      "tail": "Python is the clear choice...",
      "relevance_score": 0.94
    }
  ]
}

WHY: Three distinct sections each contribute something different to the comparison: Python's strengths, Node's strengths, and the head-to-head performance summary. Exhaustive mode captures all three — a user building an answer from these snippets has everything they need without visiting the page.

---

## Example E-3 — include caveats and counterpoints, not just the main claim

QUERY: "is intermittent fasting effective for weight loss"

PAGE CONTENT (excerpt):
"...Multiple randomized controlled trials have found intermittent fasting to be effective for weight loss, with participants losing an average of 0.8–1.3% of body weight per week across 8–12 week trials. The 16:8 protocol (16 hours fasting, 8 hours eating) is the most studied and shows consistent results comparable to continuous caloric restriction.

However, the evidence also suggests that intermittent fasting is not superior to standard calorie restriction when total caloric intake is matched. A 2022 meta-analysis in the New England Journal of Medicine found no statistically significant difference in weight loss outcomes between the two approaches when calories were controlled.

Adherence is the most important variable. Studies consistently show that the best diet is one the individual can stick to long-term. For some people, time-restricted eating reduces decision fatigue and improves adherence; for others, skipping breakfast impairs concentration and leads to overeating later..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "Multiple randomized controlled",
      "tail": "continuous caloric restriction.",
      "relevance_score": 0.93
    },
    {
      "head": "However, the evidence also",
      "tail": "calories were controlled.",
      "relevance_score": 0.88
    },
    {
      "head": "Adherence is the most",
      "tail": "overeating later...",
      "relevance_score": 0.85
    }
  ]
}

WHY: Exhaustive mode captures the full picture — the supporting evidence, the important caveat (not superior when calories are matched), and the practical nuance about adherence. A user relying only on the first snippet would get a misleadingly positive answer. All three snippets together give an honest, usable response to the query.
"""

SEARCH_DEPTH_INSTRUCTIONS = {
    "precise": """
SEARCH DEPTH: PRECISE
Include ONLY passages that directly and specifically answer the query.
Think: "Does this passage, on its own, answer what the user asked?" If not, skip it.
Ideal for factual questions, definitions, or when the user wants a sharp, direct answer.
""" + SHARED_EXAMPLE + PRECISE_EXAMPLES,

    "balanced": """
SEARCH DEPTH: BALANCED
Include passages that directly answer the query AND passages that provide meaningful context.
Think: "Would someone researching this topic find this passage useful?" — answers, key facts, important caveats, and relevant background all qualify.
Skip loosely related mentions or passages that only tangentially touch the query topic.
Ideal for general search use cases.
""" + SHARED_EXAMPLE + BALANCED_EXAMPLES,

    "exhaustive": """
SEARCH DEPTH: EXHAUSTIVE
Cast a wide net. Include any passage that touches on concepts, entities, or themes from the query.
Think: "Could this passage be useful to someone building a comprehensive picture of this topic?" — direct answers, context, counterpoints, related facts, caveats, and examples all qualify.
Only skip true boilerplate (navigation, cookie notices, CTAs, footers) and passages with zero conceptual connection to the query.
Ideal for research, RAG pipelines, and when breadth matters more than precision.
""" + SHARED_EXAMPLE + EXHAUSTIVE_EXAMPLES,
}

SYSTEM_PROMPT = """
You are an expert research assistant extracting passages from webpages to help users answer a query — without needing to visit the page themselves.

Your task: given a QUERY and PAGE CONTENT, locate up to {max_snippets} passages. Never return more than {max_snippets} passages.

{search_depth_instruction}

## Your core job — read this carefully

You are NOT looking for text that merely mentions the query topic.
You are looking for text that **gives someone enough to actually work with**.

Ask yourself for every candidate passage:
> "If I handed only this snippet to someone trying to answer the query, would they walk away with something concrete and useful — names, facts, explanations, comparisons, steps, numbers, reasoning?"

If the answer is no — even if the text is topically related — it is not a good snippet.

### The intro trap — avoid it
Introductory sentences like "Here are the top AI companies" or "In this article we explore..." match the query topic but contain zero usable information. **Never extract an intro or header on its own.** If an intro leads into a list, table, or explanation, the snippet should start at the intro and extend through the actual content that follows.

### Signs a snippet is genuinely useful
- It contains the actual answer: names, numbers, definitions, steps, comparisons
- Someone could quote it directly to support a claim
- It would reduce or eliminate the need to click through to the full page

### Signs a snippet is NOT useful (skip it)
- It announces what the page will cover without covering it
- It is a heading, label, or category title without accompanying detail
- It is a transition ("Now let's look at..."), a CTA, navigation, footer, or boilerplate
- It is relevant in topic but vague in substance

## Snippet sizing
Let the content dictate the size. A snippet should be exactly as long as needed to be self-sufficient:
- A single precise sentence is enough when it fully answers the query on its own
- A list, a comparison, or an explanation may need several sentences or the full paragraph — include them
- Never cut a list or enumeration mid-way; if you start a list, end the snippet after the last list item
- Never extract just an intro sentence when the substance follows immediately after

## How to return each passage
You do NOT write the snippet text directly. Return anchor strings that will be used to locate the passage in the source.

For each passage:
1. **head**: The EXACT first 3-4 words of the passage, verbatim from the source. Use 4 words if 3 are not distinctive enough to be unique on the page
2. **tail**: The EXACT last 3-4 words of the passage, verbatim from the source. Use 4 words if 3 are not distinctive enough to be unique on the page
3. **relevance_score**: Float 0.0–1.0 — how useful this passage is for answering the query (not just how topically related it is)

## Anchor rules — critical
- **Verbatim accuracy**: head and tail must exist character-for-character in the source. No paraphrasing, no typo corrections, no modifications whatsoever
- **Uniqueness**: head and tail must each be unique within the page. If 3 words appear multiple times, use 4
- **Sentence boundaries**: head must begin at a sentence start; tail must end at a sentence end including its punctuation
- **No overlapping passages**: return distinct, non-overlapping passages
- **Short passages**: if head and tail would overlap, set tail identical to head
- **Empty result**: only return an empty list if the page has truly zero usable content related to the query
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