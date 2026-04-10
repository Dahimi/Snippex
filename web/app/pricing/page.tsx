import Link from "next/link";
import { SignUpButton, SignedIn, SignedOut } from "@clerk/nextjs";
import { Check, Zap } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const FREE_CREDITS = parseInt(process.env.NEXT_PUBLIC_FREE_CREDITS ?? "20");
const CREDIT_PRICE_CENTS = parseInt(process.env.NEXT_PUBLIC_CREDIT_PRICE_CENTS ?? "2");
const MIN_CREDITS = parseInt(process.env.NEXT_PUBLIC_MIN_CREDITS ?? "250");

const FREE_FEATURES = [
  `${FREE_CREDITS} credits on signup — no card required`,
  "Full API access",
  "All search depths (fast, balanced, deep)",
  "Domain & recency filtering",
  "Up to 10 results per request",
];

const PAYG_FEATURES = [
  `$${(CREDIT_PRICE_CENTS / 100).toFixed(2)} per credit (1 credit = 1 API request)`,
  `Minimum top-up: ${MIN_CREDITS} credits ($${((MIN_CREDITS * CREDIT_PRICE_CENTS) / 100).toFixed(0)})`,
  "Credits never expire",
  "No subscription, no commitment",
  "Everything in the free tier",
];

const FAQS = [
  {
    q: "What counts as one credit?",
    a: "One API request to /v1/search, regardless of the number of results or search depth.",
  },
  {
    q: "Do credits expire?",
    a: "No. Credits you purchase are yours to keep — no monthly reset.",
  },
  {
    q: "What happens when I run out?",
    a: "Requests return a 402 error. Top up anytime from your settings page and usage resumes immediately.",
  },
  {
    q: "Is there a free trial?",
    a: `Yes — every new account starts with ${FREE_CREDITS} free credits, no credit card needed.`,
  },
  {
    q: "Can I use the API commercially?",
    a: "Yes. There are no restrictions on commercial use.",
  },
];

export default function PricingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-1 mx-auto w-full max-w-4xl px-4 py-16">
        {/* Header */}
        <div className="mb-14 text-center">
          <h1 className="text-3xl font-semibold text-zinc-50">Simple, transparent pricing</h1>
          <p className="mt-3 text-zinc-400">
            Start free. Pay only for what you use. No subscriptions.
          </p>
        </div>

        {/* Cards */}
        <div className="grid gap-6 sm:grid-cols-2 mb-16">
          {/* Free */}
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-8 flex flex-col">
            <div className="mb-6">
              <p className="text-sm font-medium text-zinc-400 uppercase tracking-wider">Free</p>
              <p className="mt-3 text-4xl font-semibold text-zinc-50">$0</p>
              <p className="mt-1 text-sm text-zinc-500">to get started</p>
            </div>
            <ul className="space-y-3 flex-1 mb-8">
              {FREE_FEATURES.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-sm text-zinc-300">
                  <Check size={15} className="mt-0.5 shrink-0 text-emerald-400" />
                  {f}
                </li>
              ))}
            </ul>
            <SignedOut>
              <SignUpButton mode="modal">
                <button className="w-full rounded-lg border border-zinc-700 bg-zinc-800 py-2.5 text-sm font-medium text-zinc-200 hover:bg-zinc-700 transition-colors">
                  Get started free
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link
                href="/dashboard"
                className="block w-full rounded-lg border border-zinc-700 bg-zinc-800 py-2.5 text-center text-sm font-medium text-zinc-200 hover:bg-zinc-700 transition-colors"
              >
                Go to dashboard
              </Link>
            </SignedIn>
          </div>

          {/* Pay-as-you-go */}
          <div className="rounded-2xl border border-indigo-500/40 bg-indigo-950/20 p-8 flex flex-col relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
              <span className="flex items-center gap-1 rounded-full bg-indigo-600 px-3 py-1 text-xs font-medium text-white">
                <Zap size={11} />
                Most popular
              </span>
            </div>
            <div className="mb-6">
              <p className="text-sm font-medium text-indigo-400 uppercase tracking-wider">Pay-as-you-go</p>
              <div className="mt-3 flex items-end gap-1.5">
                <p className="text-4xl font-semibold text-zinc-50">
                  ${(CREDIT_PRICE_CENTS / 100).toFixed(2)}
                </p>
                <p className="mb-1 text-sm text-zinc-400">/ credit</p>
              </div>
              <p className="mt-1 text-sm text-zinc-500">
                Min. ${((MIN_CREDITS * CREDIT_PRICE_CENTS) / 100).toFixed(0)} ({MIN_CREDITS} credits)
              </p>
            </div>
            <ul className="space-y-3 flex-1 mb-8">
              {PAYG_FEATURES.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-sm text-zinc-300">
                  <Check size={15} className="mt-0.5 shrink-0 text-indigo-400" />
                  {f}
                </li>
              ))}
            </ul>
            <SignedOut>
              <SignUpButton mode="modal">
                <button className="w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 transition-colors">
                  Get started
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link
                href="/settings"
                className="block w-full rounded-lg bg-indigo-600 py-2.5 text-center text-sm font-medium text-white hover:bg-indigo-500 transition-colors"
              >
                Top up credits
              </Link>
            </SignedIn>
          </div>
        </div>

        {/* FAQ */}
        <div className="max-w-2xl mx-auto">
          <h2 className="mb-8 text-center text-lg font-medium text-zinc-200">
            Frequently asked questions
          </h2>
          <div className="space-y-6">
            {FAQS.map(({ q, a }) => (
              <div key={q} className="border-b border-zinc-800 pb-6 last:border-0">
                <p className="text-sm font-medium text-zinc-200 mb-1.5">{q}</p>
                <p className="text-sm text-zinc-400">{a}</p>
              </div>
            ))}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
