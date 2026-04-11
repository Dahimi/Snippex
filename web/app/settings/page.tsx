"use client";

import { useUser } from "@clerk/nextjs";
import {
  User,
  CreditCard,
  ExternalLink,
  Info,
  Loader2,
} from "lucide-react";
import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

interface UsageData {
  credits_remaining: number;
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="mb-4 text-sm font-medium text-zinc-400 uppercase tracking-wider">
      {children}
    </h2>
  );
}

function SettingsRow({
  label,
  value,
  sub,
}: {
  label: string;
  value: React.ReactNode;
  sub?: string;
}) {
  return (
    <div className="flex items-start justify-between gap-4 py-3 border-b border-zinc-800 last:border-0">
      <div>
        <p className="text-sm text-zinc-400">{label}</p>
        {sub && <p className="mt-0.5 text-xs text-zinc-600">{sub}</p>}
      </div>
      <div className="text-sm text-zinc-200 text-right">{value}</div>
    </div>
  );
}

const MIN_CREDITS = 250;
const CREDITS_PRICE_CENTS = 2; // $0.02 per credit

export default function SettingsPage() {
  const { user } = useUser();
  const [credits, setCredits] = useState<number | null>(null);
  const [loadingCredits, setLoadingCredits] = useState(true);
  const [topUpAmount, setTopUpAmount] = useState<number>(MIN_CREDITS);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/usage")
      .then((r) => r.json() as Promise<UsageData>)
      .then((d) => setCredits(d.credits_remaining))
      .catch(() => setCredits(null))
      .finally(() => setLoadingCredits(false));
  }, []);

  async function handleTopUp() {
    setCheckoutLoading(true);
    setCheckoutError(null);
    try {
      const res = await fetch("/api/billing/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credits: topUpAmount }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Checkout failed");
      window.location.href = data.checkout_url;
    } catch (err) {
      setCheckoutError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setCheckoutLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-1 mx-auto w-full max-w-2xl px-4 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-zinc-50">Settings</h1>
          <p className="mt-1 text-sm text-zinc-400">
            Manage your account, billing, and preferences.
          </p>
        </div>

        {/* Account */}
        <section className="mb-8 rounded-xl border border-zinc-800 bg-zinc-900/50 p-6">
          <SectionHeading>
            <span className="flex items-center gap-2">
              <User size={14} />
              Account
            </span>
          </SectionHeading>

          <div className="divide-y divide-zinc-800">
            <SettingsRow
              label="Name"
              value={user?.fullName ?? "—"}
            />
            <SettingsRow
              label="Email"
              value={user?.primaryEmailAddress?.emailAddress ?? "—"}
            />
            <SettingsRow
              label="User ID"
              value={
                <code className="font-mono text-xs text-zinc-400">
                  {user?.id ?? "—"}
                </code>
              }
              sub="Your Clerk user ID — used internally"
            />
            <SettingsRow
              label="Joined"
              value={
                user?.createdAt
                  ? new Date(user.createdAt).toLocaleDateString()
                  : "—"
              }
            />
          </div>

          <div className="mt-6">
            <a
              href="https://accounts.snipex.dev/user"
              target="_blank"
              rel="noopener noreferrer"
              className="flex w-fit items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-300 hover:border-zinc-600 hover:bg-zinc-800 transition-colors"
            >
              Manage account
              <ExternalLink size={12} />
            </a>
          </div>
        </section>

        {/* Billing & Credits */}
        <section className="mb-8 rounded-xl border border-zinc-800 bg-zinc-900/50 p-6">
          <SectionHeading>
            <span className="flex items-center gap-2">
              <CreditCard size={14} />
              Billing & Credits
            </span>
          </SectionHeading>

          <div className="divide-y divide-zinc-800">
            <SettingsRow
              label="Credits remaining"
              value={
                loadingCredits ? (
                  <Loader2 size={14} className="animate-spin text-zinc-500" />
                ) : credits !== null ? (
                  <span className="font-mono font-semibold text-zinc-100">
                    {credits}
                  </span>
                ) : (
                  "—"
                )
              }
              sub="1 credit = 1 search request"
            />
            <SettingsRow
              label="Plan"
              value={
                <span className="rounded-full border border-indigo-700/40 bg-indigo-900/20 px-2 py-0.5 text-xs text-indigo-300">
                  Early access
                </span>
              }
            />
          </div>

          {/* Credit top-up */}
          <div className="mt-6 space-y-3">
            <p className="text-sm text-zinc-400">
              Top up credits — ${(CREDITS_PRICE_CENTS / 100).toFixed(2)} per credit, minimum {MIN_CREDITS} credits.
            </p>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min={MIN_CREDITS}
                step={50}
                value={topUpAmount}
                onChange={(e) => setTopUpAmount(Math.max(MIN_CREDITS, parseInt(e.target.value) || MIN_CREDITS))}
                className="w-32 rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-indigo-500 focus:outline-none"
              />
              <span className="text-sm text-zinc-500">
                = ${((topUpAmount * CREDITS_PRICE_CENTS) / 100).toFixed(2)}
              </span>
            </div>
            {checkoutError && (
              <p className="flex items-center gap-1.5 text-sm text-red-400">
                <Info size={13} />
                {checkoutError}
              </p>
            )}
            <button
              onClick={handleTopUp}
              disabled={checkoutLoading}
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
            >
              {checkoutLoading ? <Loader2 size={15} className="animate-spin" /> : <CreditCard size={15} />}
              {checkoutLoading ? "Redirecting…" : "Add credits"}
            </button>
          </div>
        </section>

        {/* Danger zone */}
        <section className="rounded-xl border border-red-900/30 bg-red-950/10 p-6">
          <SectionHeading>Danger zone</SectionHeading>
          <p className="mb-4 text-sm text-zinc-500">
            Permanently delete your Snippex account and all associated data.
            This action cannot be undone.
          </p>
          <button
            disabled
            className="rounded-lg border border-red-900/40 bg-red-950/20 px-4 py-2 text-sm text-red-500 opacity-60 cursor-not-allowed"
            title="Contact support to delete your account"
          >
            Delete account
          </button>
          <p className="mt-2 text-xs text-zinc-600">
            Contact{" "}
            <a href="mailto:hello@snipex.dev" className="text-zinc-500 hover:underline">
              hello@snipex.dev
            </a>{" "}
            to request account deletion.
          </p>
        </section>
      </main>

      <Footer />
    </div>
  );
}
