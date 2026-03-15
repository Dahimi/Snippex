import Link from "next/link";
import { SignUpButton, SignedIn, SignedOut } from "@clerk/nextjs";

const DOCS_URL = process.env.NEXT_PUBLIC_DOCS_URL ?? "https://docs.snippex.com";
import { ArrowRight, Zap, Search, Code2, ChevronRight } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import CodeBlock from "@/components/CodeBlock";

const REQUEST_EXAMPLE = `curl -X POST https://api.snippex.com/search \\
  -H "Authorization: Bearer snx_your_api_key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "latest advances in quantum computing",
    "num_results": 3,
    "search_depth": "balanced"
  }'`;

const RESPONSE_EXAMPLE = `{
  "query": "latest advances in quantum computing",
  "results": [
    {
      "rank": 1,
      "url": "https://nature.com/articles/quantum-2024",
      "title": "Quantum Computing Breakthroughs in 2024",
      "snippets": [
        {
          "text": "IBM's Condor processor achieved over 1,000 qubits with a
significantly lower error rate than previous generations, marking
a pivotal step toward fault-tolerant quantum computation.",
          "relevance_score": 0.96
        },
        {
          "text": "Google's Willow chip demonstrated quantum error correction
that improves exponentially as the system scales — a long-sought
milestone in the field.",
          "relevance_score": 0.91
        }
      ],
      "publish_date": "2024-12-15"
    }
  ],
  "total_latency_ms": 847
}`;

const features = [
  {
    icon: Search,
    title: "Deep snippets, not surface excerpts",
    description:
      "Other search APIs return the short blurb shown in Google results. Snippex digs into the actual page and extracts the passages that directly answer your query.",
  },
  {
    icon: Zap,
    title: "Proprietary extraction engine",
    description:
      "Our extraction algorithm identifies and pulls the most relevant passages from each page with high precision — grounded entirely in source content, not summaries.",
  },
  {
    icon: Code2,
    title: "Simple REST API",
    description:
      "One endpoint. JSON in, JSON out. Control depth, freshness, domains, and snippet count with straightforward parameters.",
  },
];

const steps = [
  {
    number: "01",
    title: "Send a query",
    description:
      "POST your query with optional filters — search depth, recency, language, domain allow/block lists.",
  },
  {
    number: "02",
    title: "We fetch and extract",
    description:
      "Snippex crawls the web, retrieves full page content, and runs it through our proprietary extraction engine to surface the passages most relevant to your query.",
  },
  {
    number: "03",
    title: "Get ranked snippets",
    description:
      "Receive structured JSON with ranked results, each containing verbatim relevant passages scored by relevance — ready to use, no post-processing needed.",
  },
];

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-1">
        {/* Hero */}
        <section className="relative mx-auto max-w-6xl px-4 pt-24 pb-16 text-center">
          <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3.5 py-1.5 text-sm text-indigo-300">
            <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse" />
            Now in early access
          </div>

          <h1 className="mb-6 text-4xl font-bold tracking-tight text-zinc-50 sm:text-5xl lg:text-6xl">
            Search results that actually{" "}
            <span className="text-indigo-400">answer</span> your query
          </h1>

          <p className="mx-auto mb-10 max-w-2xl text-lg text-zinc-400 leading-relaxed">
            Snippex is a search API that returns the{" "}
            <strong className="text-zinc-200">exact relevant passages</strong>{" "}
            from inside each page — not the surface-level excerpts other APIs give you.
            Build smarter AI pipelines, research tools, and knowledge systems without scraping.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <SignedOut>
              <SignUpButton mode="modal">
                <button className="flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 font-medium text-white hover:bg-indigo-500 transition-colors">
                  Get your API key
                  <ArrowRight size={16} />
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link
                href="/dashboard"
                className="flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 font-medium text-white hover:bg-indigo-500 transition-colors"
              >
                Go to dashboard
                <ArrowRight size={16} />
              </Link>
            </SignedIn>
            <Link
              href="/playground"
              className="flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-900 px-6 py-3 font-medium text-zinc-200 hover:border-zinc-600 hover:bg-zinc-800 transition-colors"
            >
              Try the playground
              <ChevronRight size={16} />
            </Link>
          </div>
        </section>

        {/* Code example */}
        <section className="mx-auto max-w-6xl px-4 pb-20">
          <div className="grid gap-4 lg:grid-cols-2">
            <CodeBlock code={REQUEST_EXAMPLE} language="bash" />
            <CodeBlock code={RESPONSE_EXAMPLE} language="json" />
          </div>
        </section>

        {/* Features */}
        <section className="border-t border-zinc-800 py-20">
          <div className="mx-auto max-w-6xl px-4">
            <h2 className="mb-12 text-center text-2xl font-semibold text-zinc-50">
              What makes Snippex different
            </h2>
            <div className="grid gap-6 sm:grid-cols-3">
              {features.map(({ icon: Icon, title, description }) => (
                <div
                  key={title}
                  className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-6"
                >
                  <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400">
                    <Icon size={20} />
                  </div>
                  <h3 className="mb-2 font-semibold text-zinc-100">{title}</h3>
                  <p className="text-sm text-zinc-400 leading-relaxed">{description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* How it works */}
        <section className="py-20">
          <div className="mx-auto max-w-6xl px-4">
            <h2 className="mb-12 text-center text-2xl font-semibold text-zinc-50">
              How it works
            </h2>
            <div className="grid gap-8 sm:grid-cols-3">
              {steps.map(({ number, title, description }) => (
                <div key={number} className="relative">
                  <div className="mb-4 font-mono text-4xl font-bold text-zinc-800">
                    {number}
                  </div>
                  <h3 className="mb-2 font-semibold text-zinc-100">{title}</h3>
                  <p className="text-sm text-zinc-400 leading-relaxed">{description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Parameters reference */}
        <section className="border-t border-zinc-800 py-20 bg-zinc-900/30">
          <div className="mx-auto max-w-6xl px-4">
            <h2 className="mb-2 text-center text-2xl font-semibold text-zinc-50">
              API at a glance
            </h2>
            <p className="mb-10 text-center text-sm text-zinc-500">
              One endpoint.{" "}
              <Link
                href={DOCS_URL}
                className="text-indigo-400 hover:underline"
                target="_blank"
              >
                Full docs →
              </Link>
            </p>

            <div className="overflow-hidden rounded-xl border border-zinc-800">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-zinc-800 bg-zinc-900">
                    <th className="px-4 py-3 text-left font-medium text-zinc-400">Parameter</th>
                    <th className="px-4 py-3 text-left font-medium text-zinc-400">Type</th>
                    <th className="px-4 py-3 text-left font-medium text-zinc-400">Default</th>
                    <th className="px-4 py-3 text-left font-medium text-zinc-400 hidden sm:table-cell">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800">
                  {[
                    { name: "query", type: "string", def: "—", desc: "The search query (required)" },
                    { name: "num_results", type: "1–10", def: "5", desc: "Number of results to return" },
                    { name: "max_snippets_per_result", type: "1–5", def: "3", desc: "Max snippets extracted per result" },
                    { name: "search_depth", type: "precise | balanced | exhaustive", def: "balanced", desc: "Controls extraction depth and coverage" },
                    { name: "recency", type: "day | week | month | year", def: "null", desc: "Filter results by publish date" },
                    { name: "language", type: "string", def: "en", desc: "Language code for results" },
                    { name: "include_domains", type: "string[]", def: "[]", desc: "Restrict to these domains" },
                    { name: "exclude_domains", type: "string[]", def: "[]", desc: "Exclude these domains" },
                  ].map((row) => (
                    <tr key={row.name} className="bg-background hover:bg-zinc-900/50 transition-colors">
                      <td className="px-4 py-3">
                        <code className="font-mono text-indigo-300">{row.name}</code>
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-zinc-400">{row.type}</td>
                      <td className="px-4 py-3 font-mono text-xs text-zinc-500">{row.def}</td>
                      <td className="px-4 py-3 text-zinc-400 hidden sm:table-cell">{row.desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Pricing teaser */}
        <section className="py-20">
          <div className="mx-auto max-w-6xl px-4 text-center">
            <h2 className="mb-4 text-2xl font-semibold text-zinc-50">Pricing</h2>
            <p className="mb-8 text-zinc-400">
              Simple, credit-based pricing. Details coming soon — sign up for
              early access and get free credits to start.
            </p>
            <div className="inline-flex items-center gap-3 rounded-xl border border-zinc-800 bg-zinc-900 px-8 py-6">
              <div className="text-left">
                <div className="text-3xl font-bold text-zinc-50">Free</div>
                <div className="text-sm text-zinc-400">to start</div>
              </div>
              <div className="h-10 w-px bg-zinc-700" />
              <div className="text-left text-sm text-zinc-400">
                100 credits on sign up
                <br />
                No credit card required
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="border-t border-zinc-800 py-20 bg-zinc-900/30">
          <div className="mx-auto max-w-2xl px-4 text-center">
            <h2 className="mb-4 text-2xl font-semibold text-zinc-50">
              Start extracting snippets today
            </h2>
            <p className="mb-8 text-zinc-400">
              Get an API key in 30 seconds. No credit card required.
            </p>
            <SignedOut>
              <SignUpButton mode="modal">
                <button className="flex items-center gap-2 mx-auto rounded-lg bg-indigo-600 px-8 py-3 font-medium text-white hover:bg-indigo-500 transition-colors">
                  Get started for free
                  <ArrowRight size={16} />
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link
                href="/dashboard"
                className="flex items-center gap-2 mx-auto w-fit rounded-lg bg-indigo-600 px-8 py-3 font-medium text-white hover:bg-indigo-500 transition-colors"
              >
                Go to dashboard
                <ArrowRight size={16} />
              </Link>
            </SignedIn>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
