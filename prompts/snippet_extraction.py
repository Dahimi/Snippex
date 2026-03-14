USER_PROMPT_TEMPLATE = """
QUERY: {query}

PAGE CONTENT:
[PAGE_CONTENT_START]
{page_content}
[PAGE_CONTENT_END]
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
      "head": "The Transformer architecture was",
      "tail": "to stabilize training.",
      "relevance_score": 0.97
    }
  ]
}

WHY: The snippet runs from the definition through all the architectural details. Stopping after the first sentence ("...by Vaswani et al.") would be topically relevant but informationally thin.

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
      "tail": "van Rossum.",
      "relevance_score": 0.99
    }
  ]
}

WHY: The query is a single specific fact. The first sentence contains the complete answer.

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
"...Anthropic has made significant strides in expanding context windows across its model family. **Claude 3 Opus** supports a context window of 200,000 tokens, making it one of the largest available in any commercial model. For comparison, GPT-4 Turbo offers 128,000 tokens. Researchers working with very long documents, codebases, or legal filings benefit most from these extended windows..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "**Claude 3 Opus** supports",
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
      "tail": "types of relationships.",
      "relevance_score": 0.95
    }
  ]
}

WHY: Balanced mode skips the intro sentence. The snippet starts at the actual explanation and runs through the multi-head attention detail.

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
      "tail": "underestimate this overhead.",
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
      "tail": "base model lacks.",
      "relevance_score": 0.97
    }
  ]
}

WHY: The query asks for the difference between two things. The entire comparison is one cohesive passage — splitting it would lose the contrast. The correct snippet captures the full comparison from "Both approaches..." to the final sentence that summarizes when to use each. The opening debate sentence is skipped as it's scene-setting without substance.

---

## Example B-4 — table content: include the whole table with surrounding context

QUERY: "comparison of cloud providers pricing for compute instances"

PAGE CONTENT (excerpt):
"...Choosing the right cloud provider often comes down to pricing. The table below compares on-demand pricing for general-purpose compute instances across the three major providers as of Q1 2024.

| Provider | Instance Type | vCPUs | RAM (GB) | Price/hr (USD) |
|----------|--------------|-------|----------|----------------|
| AWS | m6i.xlarge | 4 | 16 | $0.192 |
| Azure | D4s v5 | 4 | 16 | $0.192 |
| GCP | n2-standard-4 | 4 | 16 | $0.194 |
| AWS | m6i.2xlarge | 8 | 32 | $0.384 |
| Azure | D8s v5 | 8 | 32 | $0.384 |
| GCP | n2-standard-8 | 8 | 32 | $0.388 |

Prices vary by region. All three providers offer significant discounts (30–60%) through reserved instances or committed use contracts. AWS and GCP also offer spot/preemptible instances at up to 90% discount for fault-tolerant workloads..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "Choosing the right cloud",
      "tail": "fault-tolerant workloads.",
      "relevance_score": 0.96
    }
  ]
}

WHY: The table is the core answer — it directly compares pricing across providers with exact numbers. But the intro sentence gives necessary framing ("on-demand", "general-purpose", "Q1 2024"), and the closing paragraph adds critical context about discounts. All three parts (intro → table → closing note) form a self-sufficient answer. A downstream LLM receiving only this snippet has everything it needs to answer the query fully.

BAD OUTPUT (do not do this):
{
  "anchors": [
    {
      "head": "Choosing the right cloud",
      "tail": "Q1 2024.",
      "relevance_score": 0.90
    }
  ]
}

WHY IT'S BAD: Captures only the intro sentence before the table. The actual data — the table with prices — is excluded entirely. This is the worst kind of snippet: it promises information but delivers none.
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
      "tail": "vertical niches.",
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
      "tail": "is the clear choice.",
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
      "tail": "leads to overeating later.",
      "relevance_score": 0.85
    }
  ]
}

WHY: Exhaustive mode captures the full picture — the supporting evidence, the important caveat (not superior when calories are matched), and the practical nuance about adherence. A user relying only on the first snippet would get a misleadingly positive answer. All three snippets together give an honest, usable response to the query.

---

## Example E-4 — table content: capture the whole table plus framing text

QUERY: "nutritional comparison of common grains"

PAGE CONTENT (excerpt):
"...Whole grains are a cornerstone of many dietary guidelines around the world. Understanding the nutritional profile of different grains can help consumers make informed choices. The following table summarizes the macronutrient content per 100g of cooked grain.

| Grain | Calories | Protein (g) | Fiber (g) | Iron (mg) | Gluten-Free |
|-------|----------|------------|-----------|-----------|-------------|
| Brown Rice | 123 | 2.7 | 1.6 | 0.4 | Yes |
| Quinoa | 120 | 4.4 | 2.8 | 1.5 | Yes |
| Oats | 71 | 2.5 | 1.7 | 0.6 | Varies |
| Barley | 123 | 2.3 | 3.8 | 1.3 | No |
| Farro | 170 | 7.0 | 3.5 | 1.5 | No |
| Millet | 119 | 3.5 | 1.3 | 0.6 | Yes |
| Bulgur | 83 | 3.1 | 4.5 | 1.0 | No |

Quinoa and farro stand out for their protein content, making them popular choices for plant-based diets. Bulgur and barley lead in fiber, which supports digestive health and satiety. Those with celiac disease or gluten sensitivity should note that barley, farro, and bulgur all contain gluten..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "Understanding the nutritional profile",
      "tail": "all contain gluten.",
      "relevance_score": 0.96
    }
  ]
}

WHY: The table IS the answer — it contains exactly the nutritional comparison the query asks for. The snippet captures: the framing sentence ("per 100g of cooked grain" — essential for interpreting the numbers), the full table (every row, not truncated), and the analysis paragraph after (highlights key takeaways and the gluten caveat). A downstream LLM receiving this snippet can produce a complete, accurate, and nuanced answer. Cutting off at the table would lose the gluten warning; cutting off before the table would lose the data entirely.

---

## Example E-5 — step-by-step guide: capture the full procedure

QUERY: "how to set up a Kubernetes cluster from scratch"

PAGE CONTENT (excerpt):
"...Setting up a Kubernetes cluster manually (as opposed to using managed services like EKS or GKE) gives you full control and a deeper understanding of the platform. This guide walks through the core steps using kubeadm on Ubuntu 22.04.

Prerequisites: At least 2 machines (1 control plane, 1+ worker nodes), each with 2 CPUs, 2GB RAM, and a stable network connection. Swap must be disabled on all nodes.

Step 1: Install container runtime. On each node, install containerd as the container runtime. Update the package index, install dependencies, add Docker's GPG key, set up the repository, and install containerd. Then configure containerd to use systemd as the cgroup driver.

Step 2: Install kubeadm, kubelet, and kubectl. Add the Kubernetes apt repository and install the three core packages. Pin their versions with apt-mark hold to prevent accidental upgrades.

Step 3: Initialize the control plane. On the master node, run kubeadm init with the pod network CIDR matching your chosen CNI plugin (e.g., --pod-network-cidr=10.244.0.0/16 for Flannel). Save the kubeadm join command output — you'll need it for worker nodes.

Step 4: Configure kubectl access. Copy the admin kubeconfig to your user home directory so kubectl works without sudo.

Step 5: Install a CNI plugin. Without a network plugin, pods cannot communicate across nodes. Install Flannel, Calico, or Cilium — each has different tradeoffs for performance and network policy support.

Step 6: Join worker nodes. On each worker node, run the kubeadm join command saved from Step 3. Verify with kubectl get nodes on the master — all nodes should show Ready status within a minute or two.

At this point you have a functional cluster. Next steps typically include setting up an ingress controller, configuring persistent storage via a CSI driver, and deploying a monitoring stack like Prometheus and Grafana..."

GOOD OUTPUT:
{
  "anchors": [
    {
      "head": "Setting up a Kubernetes",
      "tail": "Prometheus and Grafana.",
      "relevance_score": 0.97
    }
  ]
}

WHY: The query asks HOW to do something — the answer is a multi-step procedure. Extracting just Step 1 or just the prerequisites would be useless; extracting just the last step with no context would be equally useless. The entire procedure — from prerequisites through all six steps through the "next steps" closing — is one cohesive answer. In exhaustive mode, this is the correct and complete snippet. A downstream LLM receiving this can reproduce the full guide.

BAD OUTPUT (do not do this):
{
  "anchors": [
    {
      "head": "Setting up a Kubernetes",
      "tail": "kubeadm on Ubuntu 22.04.",
      "relevance_score": 0.90
    },
    {
      "head": "Step 3: Initialize the",
      "tail": "for worker nodes.",
      "relevance_score": 0.85
    }
  ]
}

WHY IT'S BAD: The first snippet is just the intro — it tells you the guide exists but gives no steps. The second cherry-picks one step out of six, losing all context. Someone receiving these two snippets could not actually set up a cluster.
"""

SEARCH_DEPTH_INSTRUCTIONS = {
    "precise": """
SEARCH DEPTH: PRECISE
Include ONLY passages that directly and specifically answer the query.
Think: "Does this passage, on its own, answer what the user asked?" If not, skip it.
Ideal for factual questions, definitions, or when the user wants a sharp, direct answer.
Snippets should be tight and surgical — include only what's needed to deliver the fact or definition.
""" + SHARED_EXAMPLE + PRECISE_EXAMPLES,

    "balanced": """
SEARCH DEPTH: BALANCED
Include passages that directly answer the query AND passages that provide meaningful context that strengthens the answer.
Think: "Would a downstream LLM, given only these snippets, produce a correct AND complete answer?" — answers, key facts, important caveats, definitions that support explanations, examples that follow claims, and relevant background all qualify.
Skip loosely related mentions or passages that only tangentially touch the query topic.
Don't be afraid of longer snippets. A definition followed by its explanation, a claim followed by its evidence, a recommendation followed by its caveat — these naturally belong together. Splitting them forces the reader (or LLM) to work with incomplete information.
Ideal for general search use cases.
""" + SHARED_EXAMPLE + BALANCED_EXAMPLES,

    "exhaustive": """
SEARCH DEPTH: EXHAUSTIVE
Cast a wide net. Include any passage that touches on concepts, entities, or themes from the query.
Think: "Could this passage be useful to someone — or an LLM — building a comprehensive picture of this topic?" — direct answers, context, counterpoints, related facts, caveats, tables, lists, step-by-step procedures, and examples all qualify.
Only skip true boilerplate (navigation, cookie notices, CTAs, footers) and passages with zero conceptual connection to the query.
Snippet length is NOT a concern in exhaustive mode. If a table has 20 rows and all are relevant, capture all 20 rows. If a tutorial has 10 steps, capture all 10 steps. The goal is to give a downstream LLM maximum usable context — err heavily on the side of inclusion.
Ideal for research, RAG pipelines, and when breadth matters more than precision.
""" + SHARED_EXAMPLE + EXHAUSTIVE_EXAMPLES,
}

SYSTEM_PROMPT = """
You are an expert research assistant extracting passages from webpages. These passages will be fed to a downstream LLM as source context for answering the user's query — so your job is to maximize the quality and completeness of that context.

Your task: given a QUERY and PAGE CONTENT, locate up to {max_snippets} passages. Never return more than {max_snippets} passages.

{search_depth_instruction}

## Your core job — context sufficiency for downstream LLMs

You are NOT looking for text that merely mentions the query topic.
You are looking for text that **gives a downstream LLM enough to produce a correct, complete, and well-supported answer**.

For every candidate passage, apply the **context sufficiency test**:
> "If a capable LLM received ONLY this snippet as its source material and was asked to answer the query, would it produce a response that is correct, complete, and useful — with concrete facts, explanations, numbers, steps, or comparisons?"

If the answer is no — even if the text is topically related — it is not a good snippet.

Think of yourself as a research assistant preparing a briefing packet. The LLM that receives your snippets has no access to the original page. What you extract is ALL it will ever see. Missing context means a worse answer downstream.

### The intro trap — avoid it
Introductory sentences like "Here are the top AI companies" or "In this article we explore..." match the query topic but contain zero usable information. **Never extract an intro or header on its own.** If an intro leads into a list, table, or explanation, the snippet should start at the intro and extend through the actual content that follows.

### Signs a snippet is genuinely useful
- It contains the actual answer: names, numbers, definitions, steps, comparisons, data
- A downstream LLM could cite it directly to support a claim
- It would reduce or eliminate the need to access the full page
- It is self-contained: someone (or an LLM) reading it in isolation can make sense of it without additional context from the page

### Signs a snippet is NOT useful (skip it)
- It announces what the page will cover without covering it
- It is a heading, label, or category title without accompanying detail
- It is a transition ("Now let's look at..."), a CTA, navigation, footer, or boilerplate
- It is relevant in topic but vague in substance — no concrete facts, no numbers, no actionable detail

## Snippet sizing — let the content dictate length
A snippet should be exactly as long as needed to be self-sufficient. Err on the side of too long rather than too short — a downstream LLM can ignore extra context, but it cannot recover context you failed to include.

### General rules
- A single precise sentence is enough when it fully answers the query on its own
- A list, a comparison, or an explanation may need several sentences or the full paragraph — include them
- Never cut a list or enumeration mid-way; if you start a list, end the snippet after the last list item (including any closing summary or caveat after the list)
- Never extract just an intro sentence when the substance follows immediately after

### Tables
Tables are extremely high-value content — they pack dense, structured information into a compact form. When a table is relevant to the query:
- Include the **entire table** — from the header row through the last data row. Never truncate a table mid-way
- Include any **framing text** immediately before the table (e.g., "The following table shows pricing per region as of Q2 2024") — this context is essential for interpreting the data
- Include any **analysis or caveats** immediately after the table (e.g., "Note: prices exclude taxes" or "Provider X leads in category Y") — this often contains the actionable insight
- The resulting snippet may be long. That is correct and expected

### Step-by-step procedures and tutorials
When the query asks HOW to do something and the page contains a multi-step procedure:
- Include the **full procedure** from prerequisites/intro through the final step and any closing notes
- Never cherry-pick individual steps in isolation — a single step without the surrounding steps is useless
- Include any prerequisites, warnings, or "next steps" sections that bracket the procedure

### Code blocks
If the page contains code that is relevant to the query, include the entire code block plus any surrounding explanation. A code snippet without its explanation (or vice versa) fails the context sufficiency test.

## How to return each passage
You do NOT write the snippet text directly. Return anchor strings that will be used to locate the passage in the source.

### Anchor Accuracy — CRITICAL
Your anchors must satisfy the **Zero Hallucination Policy**:
1. **Verbatim accuracy**: `head` and `tail` must exist character-for-character in the source (between the `[PAGE_CONTENT_START]` and `[PAGE_CONTENT_END]` markers).
2. **Case sensitivity**: "The" is not "the".
3. **Punctuation**: "training." is not "training".
4. **Whitespace**: Spaces, newlines, and tabs must match exactly.
5. **Markdown Formatting**: Include all formatting characters (e.g., `**`, `_`, `#`, `>`) if they are part of the `head` or `tail`. For example, if a sentence starts with "**Bold Text**", the `head` MUST include the `**` markers.
6. **No paraphrasing**: Absolutely zero character changes, typo corrections, or modifications.
7. **Literal Quotes (No Escaping)**: Do NOT add backslashes to escape quotes. If the source says `"godfather"`, your anchor must be `"godfather"`, NOT `\"godfather\"`. The JSON parser handles the JSON-level escaping; you must provide the RAW string.
8. **No ellipses**: Do NOT include `...` in your anchors unless the literal text in the source contains three dots.

**Procedure**: Once you select a passage, visually re-read the `head` and `tail` against the source text to ensure an exact character match before outputting them.

For each passage:
1. **head**: The EXACT first 3-4 words of the passage, verbatim from the source. Use 4 words if 3 are not distinctive enough to be unique on the page
2. **tail**: The EXACT last 3-4 words of the passage, verbatim from the source. Use 4 words if 3 are not distinctive enough to be unique on the page
3. **relevance_score**: Float 0.0–1.0 — how useful this passage is for answering the query (not just how topically related it is). Ask: "How much does this passage contribute to a downstream LLM's ability to answer the query correctly and completely?"

## Anchor rules
- **Uniqueness**: `head` and `tail` must each be unique within the page. If 3 words appear multiple times, use 4.
- **Sentence boundaries**: `head` must begin at a sentence start; `tail` must end at a sentence end including its punctuation.
- **No overlapping passages**: return distinct, non-overlapping passages.
- **Short passages**: if `head` and `tail` would overlap, set `tail` identical to `head`.
- **Empty result**: only return an empty list if the page has truly zero usable content related to the query.
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