"use client";

import { useState } from "react";
import { SignUpButton, SignedOut } from "@clerk/nextjs";
import {
  Search,
  Loader2,
  AlertCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Info,
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import CodeBlock from "@/components/CodeBlock";
import { searchViaProxy } from "@/lib/api";
import type { SearchResponse, SearchDepth, Recency, SearchRequest } from "@/lib/api";
import clsx from "clsx";

// ---------------------------------------------------------------------------
// Code generation
// ---------------------------------------------------------------------------

function buildCurl(req: SearchRequest): string {
  const body = JSON.stringify(
    Object.fromEntries(Object.entries(req).filter(([, v]) => v !== undefined && v !== null && !(Array.isArray(v) && v.length === 0))),
    null,
    2
  );
  return `curl -X POST https://api.snippex.com/search \\
  -H "Authorization: Bearer snx_your_api_key" \\
  -H "Content-Type: application/json" \\
  -d '${body}'`;
}

function buildPython(req: SearchRequest): string {
  const body = JSON.stringify(
    Object.fromEntries(Object.entries(req).filter(([, v]) => v !== undefined && v !== null && !(Array.isArray(v) && v.length === 0))),
    null,
    2
  );
  return `import requests

response = requests.post(
    "https://api.snippex.com/search",
    headers={"Authorization": "Bearer snx_your_api_key"},
    json=${body},
)

data = response.json()
for result in data["results"]:
    print(result["title"])
    for snippet in result["snippets"]:
        print(" -", snippet["text"][:120])`;
}

function buildJavaScript(req: SearchRequest): string {
  const body = JSON.stringify(
    Object.fromEntries(Object.entries(req).filter(([, v]) => v !== undefined && v !== null && !(Array.isArray(v) && v.length === 0))),
    null,
    2
  );
  return `const response = await fetch("https://api.snippex.com/search", {
  method: "POST",
  headers: {
    "Authorization": "Bearer snx_your_api_key",
    "Content-Type": "application/json",
  },
  body: JSON.stringify(${body}),
});

const data = await response.json();
data.results.forEach((result) => {
  console.log(result.title);
  result.snippets.forEach((s) => console.log(" -", s.text.slice(0, 120)));
});`;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function RelevanceBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 80 ? "text-emerald-400" : pct >= 60 ? "text-amber-400" : "text-zinc-500";
  return <span className={clsx("font-mono text-xs tabular-nums", color)}>{pct}%</span>;
}

function ResultCard({ result }: { result: SearchResponse["results"][number] }) {
  const [expanded, setExpanded] = useState(true);
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 overflow-hidden">
      <div className="flex items-start justify-between gap-3 p-4">
        <div className="flex items-start gap-3 min-w-0">
          <span className="mt-0.5 shrink-0 font-mono text-xs text-zinc-600">#{result.rank}</span>
          <div className="min-w-0">
            <a
              href={result.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 font-medium text-zinc-100 hover:text-indigo-400 transition-colors"
            >
              <span className="truncate">{result.title}</span>
              <ExternalLink size={12} className="shrink-0 text-zinc-500" />
            </a>
            <p className="mt-0.5 truncate text-xs text-zinc-500">{result.url}</p>
          </div>
        </div>
        <button
          onClick={() => setExpanded((v) => !v)}
          className="shrink-0 text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {expanded && (
        <div className="space-y-2 px-4 pb-4">
          {result.snippets.length === 0 ? (
            <p className="text-xs text-zinc-500">No snippets extracted.</p>
          ) : (
            result.snippets.map((s, i) => (
              <div
                key={i}
                className="rounded-lg border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm leading-relaxed"
              >
                <div className="flex items-start justify-between gap-3">
                  <blockquote className="flex-1 text-zinc-300">&ldquo;{s.text}&rdquo;</blockquote>
                  <div className="shrink-0 pt-0.5">
                    <RelevanceBadge score={s.relevance_score} />
                  </div>
                </div>
              </div>
            ))
          )}
          {(result.publish_date || result.last_updated) && (
            <p className="pt-1 text-xs text-zinc-600">
              {result.publish_date && <>Published {result.publish_date}</>}
              {result.publish_date && result.last_updated && " · "}
              {result.last_updated && <>Updated {result.last_updated}</>}
            </p>
          )}
        </div>
      )}
    </div>
  );
}


// ---------------------------------------------------------------------------
// Output tabs
// ---------------------------------------------------------------------------

type OutputTab = "results" | "json" | "code";
type CodeLang = "curl" | "python" | "javascript";

const CODE_LANGS: { id: CodeLang; label: string }[] = [
  { id: "curl", label: "cURL" },
  { id: "python", label: "Python" },
  { id: "javascript", label: "JavaScript" },
];

function OutputPanel({
  result,
  currentRequest,
}: {
  result: SearchResponse;
  currentRequest: SearchRequest;
}) {
  const [tab, setTab] = useState<OutputTab>("results");
  const [codeLang, setCodeLang] = useState<CodeLang>("curl");

  const codeMap: Record<CodeLang, string> = {
    curl: buildCurl(currentRequest),
    python: buildPython(currentRequest),
    javascript: buildJavaScript(currentRequest),
  };

  return (
    <div className="space-y-4">
      {/* Meta bar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3 text-xs text-zinc-500">
          <span>
            <span className="text-zinc-300">{result.results.length}</span>{" "}
            result{result.results.length !== 1 ? "s" : ""}
          </span>
          <span>·</span>
          <span>
            <span className="text-zinc-300">{result.total_latency_ms}ms</span>
          </span>
        </div>

        {/* Tab switcher */}
        <div className="flex rounded-lg border border-zinc-700 overflow-hidden text-xs">
          {(["results", "json", "code"] as OutputTab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={clsx(
                "px-3 py-1.5 capitalize transition-colors",
                tab === t
                  ? "bg-indigo-600 text-white"
                  : "bg-zinc-900 text-zinc-400 hover:text-zinc-200"
              )}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Results tab */}
      {tab === "results" && (
        <div className="space-y-4">
          {result.results.map((r) => (
            <ResultCard key={r.rank} result={r} />
          ))}
        </div>
      )}

      {/* JSON tab */}
      {tab === "json" && (
        <CodeBlock
          code={JSON.stringify(result, null, 2)}
          language="json"
          maxHeight="600px"
        />
      )}

      {/* Code tab */}
      {tab === "code" && (
        <div className="space-y-3">
          {/* Language selector */}
          <div className="flex rounded-lg border border-zinc-700 overflow-hidden w-fit text-xs">
            {CODE_LANGS.map(({ id, label }) => (
              <button
                key={id}
                onClick={() => setCodeLang(id)}
                className={clsx(
                  "px-3 py-1.5 transition-colors",
                  codeLang === id
                    ? "bg-indigo-600 text-white"
                    : "bg-zinc-900 text-zinc-400 hover:text-zinc-200"
                )}
              >
                {label}
              </button>
            ))}
          </div>

          <CodeBlock
            code={codeMap[codeLang]}
            language={codeLang === "curl" ? "bash" : codeLang}
          />
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

const DEPTH_OPTIONS: { value: SearchDepth; label: string; desc: string }[] = [
  { value: "precise", label: "Precise", desc: "Fewer, higher-confidence snippets" },
  { value: "balanced", label: "Balanced", desc: "Default — good mix of speed and coverage" },
  { value: "exhaustive", label: "Exhaustive", desc: "Maximum snippets per result" },
];

const RECENCY_OPTIONS: { value: Recency | ""; label: string }[] = [
  { value: "", label: "Any time" },
  { value: "day", label: "Past 24 hours" },
  { value: "week", label: "Past week" },
  { value: "month", label: "Past month" },
  { value: "year", label: "Past year" },
];

export default function PlaygroundPage() {
  const [query, setQuery] = useState("");
  const [depth, setDepth] = useState<SearchDepth>("balanced");
  const [recency, setRecency] = useState<Recency | "">("");
  const [numResults, setNumResults] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [rateLimited, setRateLimited] = useState(false);
  const [lastRequest, setLastRequest] = useState<SearchRequest | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const req: SearchRequest = {
      query: query.trim(),
      search_depth: depth,
      num_results: numResults,
      ...(recency ? { recency } : {}),
    };

    setLoading(true);
    setError(null);
    setResult(null);
    setRateLimited(false);
    setLastRequest(req);

    try {
      const data = await searchViaProxy(req);
      setResult(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Search failed";
      if (msg.includes("Rate limit")) setRateLimited(true);
      else setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-1 mx-auto w-full max-w-4xl px-4 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-zinc-50">Playground</h1>
          <p className="mt-1 text-sm text-zinc-400">
            Try the Snippex API live. See exactly what your application will receive.
          </p>
        </div>

        <SignedOut>
          <div className="mb-6 flex items-start gap-3 rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-3 text-sm">
            <Info size={16} className="mt-0.5 shrink-0 text-zinc-400" />
            <span className="text-zinc-400">
              Unauthenticated users are limited to 5 requests per hour.{" "}
              <SignUpButton mode="modal">
                <button className="text-indigo-400 hover:underline">Sign up free</button>
              </SignUpButton>{" "}
              for higher limits.
            </span>
          </div>
        </SignedOut>

        {/* Form */}
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your search query..."
              className="flex-1 rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
              Search
            </button>
          </div>

          {/* Options */}
          <div className="flex flex-wrap gap-3">
            <div className="flex items-center gap-2">
              <label className="text-xs text-zinc-500">Depth</label>
              <div className="flex rounded-lg border border-zinc-700 overflow-hidden">
                {DEPTH_OPTIONS.map(({ value, label, desc }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setDepth(value)}
                    title={desc}
                    className={clsx(
                      "px-3 py-1.5 text-xs transition-colors",
                      depth === value
                        ? "bg-indigo-600 text-white"
                        : "bg-zinc-900 text-zinc-400 hover:text-zinc-200"
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-xs text-zinc-500">Recency</label>
              <select
                value={recency}
                onChange={(e) => setRecency(e.target.value as Recency | "")}
                className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-200 outline-none focus:border-indigo-500 transition-colors"
              >
                {RECENCY_OPTIONS.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-xs text-zinc-500">Results</label>
              <input
                type="number"
                min={1}
                max={10}
                value={numResults}
                onChange={(e) => setNumResults(Number(e.target.value))}
                className="w-16 rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-200 outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>
        </form>

        {/* Rate limit */}
        {rateLimited && (
          <div className="mt-6 rounded-xl border border-red-900/40 bg-red-900/10 px-4 py-4 text-sm text-red-400">
            <div className="mb-1 font-medium">Rate limit reached</div>
            <p className="text-red-400/80">
              <SignUpButton mode="modal">
                <button className="text-red-300 hover:underline">Sign up for free</button>
              </SignUpButton>{" "}
              to continue.
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-6 flex items-start gap-3 rounded-xl border border-red-900/40 bg-red-900/10 px-4 py-4 text-sm text-red-400">
            <AlertCircle size={16} className="mt-0.5 shrink-0" />
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="mt-8 space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-32 rounded-xl border border-zinc-800 bg-zinc-900/50 animate-pulse" />
            ))}
          </div>
        )}

        {/* Output */}
        {result && !loading && lastRequest && (
          <div className="mt-8">
            <OutputPanel result={result} currentRequest={lastRequest} />
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
