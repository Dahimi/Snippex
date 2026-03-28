"""
Eval report — prints summary stats for one run, or compares two runs side-by-side.

Usage:
    python evals/report.py evals/results/20260328_120000_baseline.jsonl
    python evals/report.py evals/results/baseline.jsonl evals/results/new-provider.jsonl
"""

import json
import sys
from pathlib import Path
from collections import defaultdict


# ── helpers ──────────────────────────────────────────────────────────────────

def load_records(path: str) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = max(0, int(len(sorted_vals) * p / 100) - 1)
    return sorted_vals[idx]


def pct(num, denom) -> str:
    if not denom:
        return "  n/a"
    return f"{num / denom:.1%}"


def delta_str(a, b, unit="") -> str:
    """Format a delta between two values with direction indicator."""
    if a is None or b is None:
        return ""
    diff = b - a
    sign = "+" if diff >= 0 else ""
    return f"  ({sign}{diff:.1f}{unit})"


def delta_pct_str(a, b) -> str:
    """Format a percentage-point delta."""
    if a is None or b is None:
        return ""
    diff = (b - a) * 100
    sign = "+" if diff >= 0 else ""
    return f"  ({sign}{diff:.1f}pp)"


# ── aggregate one run ─────────────────────────────────────────────────────────

def aggregate(records: list[dict]) -> dict:
    ok = [r for r in records if r["status"] == "ok"]
    errors = [r for r in records if r["status"] == "error"]

    # Latency
    search_ms = [r["latency"]["search_ms"] for r in ok if r.get("latency")]
    extraction_ms = [r["latency"]["extraction_ms"] for r in ok if r.get("latency")]
    total_ms = [r["latency"]["total_ms"] for r in ok if r.get("latency")]

    # Reconstruction
    recon_rates = [
        r["metrics"]["reconstruction_rate"]
        for r in ok
        if r.get("metrics") and r["metrics"]["reconstruction_rate"] is not None
    ]
    total_anchors = sum(
        r["metrics"]["total_anchors_proposed"] for r in ok if r.get("metrics")
    )
    succeeded_anchors = sum(
        r["metrics"]["total_anchors_succeeded"] for r in ok if r.get("metrics")
    )
    total_results = sum(
        r["metrics"]["num_results"] for r in ok if r.get("metrics")
    )
    zero_snippet_results = sum(
        r["metrics"]["zero_snippet_results"] for r in ok if r.get("metrics")
    )
    queries_with_zero = sum(
        1 for r in ok
        if r.get("metrics") and r["metrics"]["total_snippets"] == 0
    )
    total_snippets = sum(
        r["metrics"]["total_snippets"] for r in ok if r.get("metrics")
    )
    avg_rel_scores = [
        r["metrics"]["avg_relevance_score"]
        for r in ok
        if r.get("metrics") and r["metrics"]["avg_relevance_score"] is not None
    ]

    # Fuzzy stages
    stages: dict[str, int] = {"exact": 0, "levenshtein": 0, "jaccard": 0}
    for r in ok:
        if r.get("metrics") and r["metrics"].get("fuzzy_stage_counts"):
            for k, v in r["metrics"]["fuzzy_stage_counts"].items():
                stages[k] = stages.get(k, 0) + v

    # Per-category breakdown
    by_category: dict[str, dict] = defaultdict(lambda: {
        "count": 0, "ok": 0,
        "recon_rates": [], "zero_snippet_results": 0, "total_results": 0,
        "total_ms": [],
    })
    for r in records:
        cat = r.get("category", "unknown")
        by_category[cat]["count"] += 1
        if r["status"] == "ok":
            by_category[cat]["ok"] += 1
            if r.get("latency"):
                by_category[cat]["total_ms"].append(r["latency"]["total_ms"])
            if r.get("metrics"):
                m = r["metrics"]
                if m["reconstruction_rate"] is not None:
                    by_category[cat]["recon_rates"].append(m["reconstruction_rate"])
                by_category[cat]["zero_snippet_results"] += m["zero_snippet_results"]
                by_category[cat]["total_results"] += m["num_results"]

    return {
        "n_total": len(records),
        "n_ok": len(ok),
        "n_errors": len(errors),
        "search_ms": search_ms,
        "extraction_ms": extraction_ms,
        "total_ms": total_ms,
        "recon_rates": recon_rates,
        "total_anchors": total_anchors,
        "succeeded_anchors": succeeded_anchors,
        "total_results": total_results,
        "zero_snippet_results": zero_snippet_results,
        "queries_with_zero": queries_with_zero,
        "total_snippets": total_snippets,
        "avg_rel_scores": avg_rel_scores,
        "fuzzy_stages": stages,
        "by_category": dict(by_category),
        "errors": errors,
    }


# ── report for one run ────────────────────────────────────────────────────────

def print_run_summary(path: str, agg: dict, label_override: str = None):
    label = label_override or Path(path).stem
    print(f"\n{'═' * 60}")
    print(f"  Run: {label}")
    print(f"  File: {path}")
    print(f"{'═' * 60}")

    # Header
    prov_sample = None
    # Try to get provider info from first record
    try:
        with open(path) as f:
            first = json.loads(f.readline())
        prov_sample = f"search={first.get('search_provider','?')}  llm={first.get('llm_provider','?')}"
    except Exception:
        pass

    if prov_sample:
        print(f"  Providers : {prov_sample}")
    print(f"  Queries   : {agg['n_total']} total  |  {agg['n_ok']} ok  |  {agg['n_errors']} errors")

    # Latency
    print(f"\n  LATENCY (ms)")
    for name, vals in [
        ("search", agg["search_ms"]),
        ("extraction", agg["extraction_ms"]),
        ("total", agg["total_ms"]),
    ]:
        if vals:
            print(
                f"    {name:12} p50={percentile(vals, 50):>5.0f}  "
                f"p75={percentile(vals, 75):>5.0f}  "
                f"p95={percentile(vals, 95):>5.0f}  "
                f"p99={percentile(vals, 99):>5.0f}"
            )

    # Quality
    print(f"\n  QUALITY")
    overall_recon = (
        agg["succeeded_anchors"] / agg["total_anchors"]
        if agg["total_anchors"] else None
    )
    avg_recon = (
        sum(agg["recon_rates"]) / len(agg["recon_rates"])
        if agg["recon_rates"] else None
    )
    print(f"    reconstruction rate (overall)  : {pct(agg['succeeded_anchors'], agg['total_anchors'])}")
    print(f"    reconstruction rate (avg/query) : {f'{avg_recon:.1%}' if avg_recon is not None else 'n/a'}")
    print(f"    anchors proposed               : {agg['total_anchors']}")
    print(f"    anchors succeeded              : {agg['succeeded_anchors']}")
    print(f"    total snippets extracted       : {agg['total_snippets']}")
    print(f"    avg snippets / result          : {agg['total_snippets'] / agg['total_results']:.1f}"
          if agg["total_results"] else "    avg snippets / result          : n/a")
    print(f"    zero-snippet results           : {agg['zero_snippet_results']} / {agg['total_results']}  "
          f"({pct(agg['zero_snippet_results'], agg['total_results'])})")
    print(f"    queries with 0 snippets total  : {agg['queries_with_zero']} / {agg['n_ok']}  "
          f"({pct(agg['queries_with_zero'], agg['n_ok'])})")

    if agg["avg_rel_scores"]:
        avg_rel = sum(agg["avg_rel_scores"]) / len(agg["avg_rel_scores"])
        print(f"    avg relevance score (LLM)      : {avg_rel:.3f}")

    # Fuzzy stages
    stages = agg["fuzzy_stages"]
    total_stage = sum(stages.values())
    if total_stage:
        print(f"\n  RECONSTRUCTION STAGES (of {total_stage} successes)")
        for stage, count in stages.items():
            print(f"    {stage:12} : {count:4}  ({pct(count, total_stage)})")

    # Per-category
    print(f"\n  BY CATEGORY")
    print(f"    {'category':14} {'queries':>7} {'ok':>4} {'recon%':>7} {'zero%':>7} {'p50ms':>6}")
    print(f"    {'-'*14} {'-'*7} {'-'*4} {'-'*7} {'-'*7} {'-'*6}")
    for cat, c in sorted(agg["by_category"].items()):
        avg_r = sum(c["recon_rates"]) / len(c["recon_rates"]) if c["recon_rates"] else None
        zero_p = c["zero_snippet_results"] / c["total_results"] if c["total_results"] else None
        p50 = percentile(c["total_ms"], 50) if c["total_ms"] else None
        avg_r_str = f"{avg_r:>7.1%}" if avg_r is not None else f"{'n/a':>7}"
        zero_str = f"{zero_p:>7.1%}" if zero_p is not None else f"{'n/a':>7}"
        p50_str = f"{p50:>6.0f}" if p50 is not None else f"{'n/a':>6}"
        print(f"    {cat:14} {c['count']:>7} {c['ok']:>4} {avg_r_str} {zero_str} {p50_str}")

    # Errors
    if agg["errors"]:
        print(f"\n  ERRORS")
        for e in agg["errors"]:
            print(f"    [{e.get('category','?')}] {e['query'][:60]}")
            print(f"      → {e.get('error','unknown error')}")


# ── comparison between two runs ───────────────────────────────────────────────

def print_comparison(path_a: str, agg_a: dict, path_b: str, agg_b: dict):
    print(f"\n{'═' * 70}")
    print(f"  COMPARISON")
    print(f"  A: {Path(path_a).stem}")
    print(f"  B: {Path(path_b).stem}")
    print(f"{'═' * 70}")

    def row(label, a_val, b_val, fmt=".0f", unit="ms", higher_is_better=False):
        if a_val is None or b_val is None:
            print(f"  {label:35} {'n/a':>8}  {'n/a':>8}")
            return
        diff = b_val - a_val
        sign = "+" if diff >= 0 else ""
        better = (diff > 0) == higher_is_better
        indicator = "▲" if diff > 0 else ("▼" if diff < 0 else "=")
        color_indicator = indicator  # could add ANSI later
        print(
            f"  {label:35} {a_val:>8{fmt}}{unit}  {b_val:>8{fmt}}{unit}  "
            f"{sign}{diff:{fmt}}{unit} {color_indicator}"
        )

    print(f"\n  {'metric':35} {'A':>9}  {'B':>9}  {'delta':>10}")
    print(f"  {'-'*35} {'-'*9}  {'-'*9}  {'-'*10}")

    def p50(vals): return percentile(vals, 50) if vals else None
    def p95(vals): return percentile(vals, 95) if vals else None

    row("search_ms p50",        p50(agg_a["search_ms"]),     p50(agg_b["search_ms"]),     higher_is_better=False)
    row("search_ms p95",        p95(agg_a["search_ms"]),     p95(agg_b["search_ms"]),     higher_is_better=False)
    row("extraction_ms p50",    p50(agg_a["extraction_ms"]), p50(agg_b["extraction_ms"]), higher_is_better=False)
    row("extraction_ms p95",    p95(agg_a["extraction_ms"]), p95(agg_b["extraction_ms"]), higher_is_better=False)
    row("total_ms p50",         p50(agg_a["total_ms"]),      p50(agg_b["total_ms"]),      higher_is_better=False)
    row("total_ms p95",         p95(agg_a["total_ms"]),      p95(agg_b["total_ms"]),      higher_is_better=False)

    # Quality (these are ratios, show as %)
    def overall_recon(agg):
        return agg["succeeded_anchors"] / agg["total_anchors"] * 100 if agg["total_anchors"] else None

    def zero_pct(agg):
        return agg["zero_snippet_results"] / agg["total_results"] * 100 if agg["total_results"] else None

    row("reconstruction rate (%)", overall_recon(agg_a), overall_recon(agg_b), fmt=".1f", unit="%", higher_is_better=True)
    row("zero-snippet results (%)", zero_pct(agg_a),     zero_pct(agg_b),     fmt=".1f", unit="%", higher_is_better=False)

    def avg_snip(agg):
        return agg["total_snippets"] / agg["total_results"] if agg["total_results"] else None

    row("avg snippets / result",  avg_snip(agg_a), avg_snip(agg_b), fmt=".2f", unit="", higher_is_better=True)


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python evals/report.py <file.jsonl> [<file_b.jsonl>]")
        sys.exit(1)

    path_a = sys.argv[1]
    records_a = load_records(path_a)
    agg_a = aggregate(records_a)
    print_run_summary(path_a, agg_a)

    if len(sys.argv) >= 3:
        path_b = sys.argv[2]
        records_b = load_records(path_b)
        agg_b = aggregate(records_b)
        print_run_summary(path_b, agg_b)
        print_comparison(path_a, agg_a, path_b, agg_b)

    print()


if __name__ == "__main__":
    main()
