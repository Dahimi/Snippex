"""
Eval runner — calls providers directly (no cache, no auth, no Redis).

Usage:
    python evals/runner.py
    python evals/runner.py --label my-run --concurrency 3
    python evals/runner.py --queries evals/queries.yaml --search perplexity --llm cerebras
    python evals/runner.py --dry-run          # validate setup, print queries, no API calls

Output:
    evals/results/YYYYMMDD_HHMMSS_<label>.jsonl
    One JSON line per query.
"""

import argparse
import asyncio
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv

# ── path setup so we can import from the project root ──────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from models.request import SearchRequest
from services.snippet_reconstructor import reconstruct_snippet


# ── provider registry ───────────────────────────────────────────────────────

def _load_search_provider(name: str):
    if name == "perplexity":
        from providers.search.perplexity import PerplexitySearchProvider
        return PerplexitySearchProvider()
    raise ValueError(f"Unknown search provider: {name!r}. Add it to _load_search_provider().")


def _load_llm_provider(name: str):
    if name == "cerebras":
        from providers.llm.cerebras import CerebrasLLMProvider
        return CerebrasLLMProvider()
    raise ValueError(f"Unknown LLM provider: {name!r}. Add it to _load_llm_provider().")


# ── per-query metrics ────────────────────────────────────────────────────────

def _compute_metrics(raw_results, all_extraction_results) -> dict:
    """
    Given raw search results and extraction results, compute quality metrics.
    Mirrors the logic in SearchService.search_and_extract but captures more detail.
    """
    total_anchors = 0
    succeeded_anchors = 0
    zero_snippet_results = 0
    snippets_per_result = []
    relevance_scores = []
    fuzzy_stages: dict[str, int] = {"exact": 0, "levenshtein": 0, "jaccard": 0}

    for raw_result, extraction in zip(raw_results, all_extraction_results):
        if isinstance(extraction, Exception):
            anchors = []
        else:
            anchors, _ = extraction

        result_snippets = 0
        for anchor in anchors:
            total_anchors += 1
            outcome = reconstruct_snippet(raw_result.content, anchor)
            if outcome.succeeded:
                succeeded_anchors += 1
                result_snippets += 1
                relevance_scores.append(anchor.relevance_score)
                stage = outcome.head_stage or "exact"
                if stage in fuzzy_stages:
                    fuzzy_stages[stage] += 1

        snippets_per_result.append(result_snippets)
        if result_snippets == 0:
            zero_snippet_results += 1

    reconstruction_rate = (
        round(succeeded_anchors / total_anchors, 4) if total_anchors > 0 else None
    )
    avg_relevance = (
        round(sum(relevance_scores) / len(relevance_scores), 4) if relevance_scores else None
    )

    return {
        "num_results": len(raw_results),
        "total_anchors_proposed": total_anchors,
        "total_anchors_succeeded": succeeded_anchors,
        "reconstruction_rate": reconstruction_rate,
        "total_snippets": succeeded_anchors,
        "zero_snippet_results": zero_snippet_results,
        "snippets_per_result": snippets_per_result,
        "avg_relevance_score": avg_relevance,
        "fuzzy_stage_counts": fuzzy_stages,
    }


# ── single query runner ──────────────────────────────────────────────────────

async def run_query(
    entry: dict,
    search_provider,
    llm_provider,
    run_id: str,
    label: str,
    semaphore: asyncio.Semaphore,
    default_request_params: dict,
) -> dict:
    query = entry["query"]
    category = entry.get("category", "unknown")

    async with semaphore:
        record = {
            "run_id": run_id,
            "label": label,
            "query": query,
            "category": category,
            "search_provider": search_provider.name,
            "llm_provider": llm_provider.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": None,
            "latency": None,
            "metrics": None,
        }

        try:
            request = SearchRequest(query=query, **default_request_params)

            # 1. Search
            t0 = time.perf_counter()
            raw_results = await search_provider.search(request)
            t1 = time.perf_counter()
            search_ms = int((t1 - t0) * 1000)

            # 2. Parallel LLM extraction
            tasks = [
                llm_provider.extract_snippet_anchors(
                    query=request.query,
                    page_content=result.content,
                    max_snippets=request.max_snippets_per_result,
                    search_depth=request.search_depth,
                )
                for result in raw_results
            ]
            all_extraction_results = await asyncio.gather(*tasks, return_exceptions=True)
            t2 = time.perf_counter()
            extraction_ms = int((t2 - t1) * 1000)

            # 3. Reconstruction (synchronous, fast)
            metrics = _compute_metrics(raw_results, all_extraction_results)
            t3 = time.perf_counter()
            reconstruction_ms = int((t3 - t2) * 1000)

            record["status"] = "ok"
            record["latency"] = {
                "search_ms": search_ms,
                "extraction_ms": extraction_ms,
                "reconstruction_ms": reconstruction_ms,
                "total_ms": int((t3 - t0) * 1000),
            }
            record["metrics"] = metrics

        except Exception as exc:
            record["error"] = str(exc)

        return record


# ── main ─────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Snipex eval runner")
    parser.add_argument("--queries", default="evals/queries.yaml", help="Path to queries YAML")
    parser.add_argument("--search", default="perplexity", help="Search provider name")
    parser.add_argument("--llm", default="cerebras", help="LLM provider name")
    parser.add_argument("--label", default="run", help="Label for the output file")
    parser.add_argument("--concurrency", type=int, default=3, help="Max concurrent queries")
    parser.add_argument("--num-results", type=int, default=5)
    parser.add_argument("--max-snippets", type=int, default=3)
    parser.add_argument("--search-depth", default="balanced")
    parser.add_argument("--dry-run", action="store_true", help="Print queries without calling APIs")
    args = parser.parse_args()

    # Load queries
    queries_path = ROOT / args.queries
    with open(queries_path) as f:
        data = yaml.safe_load(f)
    queries = data["queries"]

    if args.dry_run:
        print(f"Dry run — {len(queries)} queries loaded from {queries_path}")
        for i, q in enumerate(queries, 1):
            print(f"  {i:3}. [{q.get('category', '?'):12}] {q['query']}")
        return

    # Set up providers
    search_provider = _load_search_provider(args.search)
    llm_provider = _load_llm_provider(args.llm)

    run_id = str(uuid.uuid4())
    semaphore = asyncio.Semaphore(args.concurrency)
    default_request_params = {
        "num_results": args.num_results,
        "max_snippets_per_result": args.max_snippets,
        "search_depth": args.search_depth,
    }

    # Output file
    results_dir = ROOT / "evals" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = results_dir / f"{timestamp}_{args.label}.jsonl"

    print(f"Run ID   : {run_id}")
    print(f"Label    : {args.label}")
    print(f"Providers: search={args.search}  llm={args.llm}")
    print(f"Queries  : {len(queries)}")
    print(f"Output   : {out_path}")
    print(f"Concurrency: {args.concurrency}")
    print()

    tasks = [
        run_query(
            entry=q,
            search_provider=search_provider,
            llm_provider=llm_provider,
            run_id=run_id,
            label=args.label,
            semaphore=semaphore,
            default_request_params=default_request_params,
        )
        for q in queries
    ]

    completed = 0
    with open(out_path, "w") as out_file:
        for coro in asyncio.as_completed(tasks):
            record = await coro
            completed += 1
            status_icon = "✓" if record["status"] == "ok" else "✗"
            recon = record.get("metrics") or {}
            rate = recon.get("reconstruction_rate")
            rate_str = f"{rate:.0%}" if rate is not None else "n/a"
            total_ms = (record.get("latency") or {}).get("total_ms", "?")

            print(
                f"  [{completed:3}/{len(queries)}] {status_icon} "
                f"{total_ms:>5}ms  recon={rate_str:>5}  "
                f"[{record['category']:12}]  {record['query'][:60]}"
            )

            out_file.write(json.dumps(record) + "\n")
            out_file.flush()

    print(f"\nDone. Results written to: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
