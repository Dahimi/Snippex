"use client";

import { useEffect, useState, useCallback } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { useUser } from "@clerk/nextjs";
import {
  Key,
  Copy,
  Check,
  Trash2,
  Plus,
  Loader2,
  TrendingUp,
  Zap,
  AlertCircle,
  Eye,
  EyeOff,
  RefreshCw,
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import type { ApiKey } from "@/lib/supabase";

// ---------------------------------------------------------------------------
// Types for API responses from our Next.js routes
// ---------------------------------------------------------------------------

interface DailyUsage {
  date: string;
  request_count: number;
}

interface UsageData {
  today: number;
  this_month: number;
  credits_remaining: number;
  daily_breakdown: DailyUsage[];
}

interface NewKeyResponse {
  key: ApiKey; // full key returned only on creation
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
      <p className="text-sm text-zinc-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums text-zinc-50">
        {value}
      </p>
      {sub && <p className="mt-0.5 text-xs text-zinc-600">{sub}</p>}
    </div>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="rounded-md p-1.5 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 transition-colors"
      title="Copy"
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
    </button>
  );
}

function ApiKeyRow({
  apiKey,
  onDelete,
}: {
  apiKey: ApiKey & { rawKey?: string }; // rawKey present only right after creation
  onDelete: (id: string) => void;
}) {
  const [visible, setVisible] = useState(!!apiKey.rawKey);
  const [deleting, setDeleting] = useState(false);

  const displayKey = visible && apiKey.rawKey ? apiKey.rawKey : apiKey.key;

  const handleDelete = async () => {
    if (!confirm(`Delete API key "${apiKey.name}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await fetch(`/api/keys/${apiKey.id}`, { method: "DELETE" });
      onDelete(apiKey.id);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border border-zinc-800 bg-zinc-900/50 p-4">
      <div className="flex items-start gap-3 min-w-0">
        <Key size={16} className="mt-0.5 shrink-0 text-zinc-500" />
        <div className="min-w-0">
          <p className="text-sm font-medium text-zinc-200">{apiKey.name}</p>
          <div className="mt-1 flex items-center gap-2">
            <code className="font-mono text-xs text-zinc-400 truncate max-w-xs sm:max-w-sm">
              {displayKey}
            </code>
            {apiKey.rawKey && (
              <button
                onClick={() => setVisible((v) => !v)}
                className="shrink-0 text-zinc-600 hover:text-zinc-400 transition-colors"
                title={visible ? "Hide key" : "Show key"}
              >
                {visible ? <EyeOff size={12} /> : <Eye size={12} />}
              </button>
            )}
          </div>
          <p className="mt-1 text-xs text-zinc-600">
            Created {new Date(apiKey.created_at).toLocaleDateString()}
            {apiKey.last_used_at &&
              ` · Last used ${new Date(apiKey.last_used_at).toLocaleDateString()}`}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-1 shrink-0">
        {apiKey.rawKey && <CopyButton text={apiKey.rawKey} />}
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="rounded-md p-1.5 text-zinc-600 hover:text-red-400 hover:bg-zinc-800 disabled:opacity-50 transition-colors"
          title="Delete key"
        >
          {deleting ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Newly-created key banner (shown once)
// ---------------------------------------------------------------------------
function NewKeyBanner({ rawKey, onDismiss }: { rawKey: string; onDismiss: () => void }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(rawKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mb-6 rounded-xl border border-emerald-700/40 bg-emerald-900/10 p-4">
      <div className="flex items-start gap-3">
        <Check size={16} className="mt-0.5 shrink-0 text-emerald-400" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-emerald-300">
            API key created — copy it now
          </p>
          <p className="mt-0.5 text-xs text-emerald-500">
            This is the only time the full key is shown.
          </p>
          <div className="mt-3 flex items-center gap-2">
            <code className="flex-1 font-mono text-xs text-emerald-200 bg-emerald-950/50 rounded-lg px-3 py-2 break-all">
              {rawKey}
            </code>
            <button
              onClick={handleCopy}
              className="shrink-0 flex items-center gap-1.5 rounded-lg bg-emerald-700/40 px-3 py-2 text-xs text-emerald-300 hover:bg-emerald-700/60 transition-colors"
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
        </div>
        <button
          onClick={onDismiss}
          className="text-emerald-700 hover:text-emerald-500 transition-colors text-xs"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const { user } = useUser();

  const [keys, setKeys] = useState<(ApiKey & { rawKey?: string })[]>([]);
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [showNewKeyForm, setShowNewKeyForm] = useState(false);
  const [justCreatedKey, setJustCreatedKey] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [keysRes, usageRes] = await Promise.all([
        fetch("/api/keys"),
        fetch("/api/usage"),
      ]);
      const keysData = await keysRes.json() as { keys: ApiKey[] };
      const usageData = await usageRes.json() as UsageData;
      setKeys(keysData.keys ?? []);
      setUsage(usageData);
    } catch {
      setError("Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const res = await fetch("/api/keys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newKeyName || "Default" }),
      });
      const data = await res.json() as NewKeyResponse;
      const newKey = data.key;
      setKeys((prev) => [{ ...newKey, rawKey: newKey.key }, ...prev]);
      setJustCreatedKey(newKey.key);
      setNewKeyName("");
      setShowNewKeyForm(false);
    } catch {
      setError("Failed to create API key.");
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteKey = (id: string) => {
    setKeys((prev) => prev.filter((k) => k.id !== id));
  };

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-1 mx-auto w-full max-w-4xl px-4 py-10">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-zinc-50">Dashboard</h1>
          {user && (
            <p className="mt-1 text-sm text-zinc-400">
              Welcome back, {user.firstName ?? user.emailAddresses[0]?.emailAddress}
            </p>
          )}
        </div>

        {/* New key banner */}
        {justCreatedKey && (
          <NewKeyBanner
            rawKey={justCreatedKey}
            onDismiss={() => setJustCreatedKey(null)}
          />
        )}

        {/* Error */}
        {error && (
          <div className="mb-6 flex items-start gap-2 rounded-xl border border-red-900/40 bg-red-900/10 px-4 py-3 text-sm text-red-400">
            <AlertCircle size={16} className="mt-0.5 shrink-0" />
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 size={24} className="animate-spin text-zinc-500" />
          </div>
        ) : (
          <>
            {/* Usage stats */}
            <section className="mb-8">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">
                  Usage
                </h2>
                <button
                  onClick={async () => { setRefreshing(true); await loadData(); setRefreshing(false); }}
                  disabled={refreshing}
                  className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors disabled:opacity-50"
                >
                  <RefreshCw size={12} className={refreshing ? "animate-spin" : ""} />
                  Refresh
                </button>
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                <StatCard
                  label="Requests today"
                  value={usage?.today ?? 0}
                />
                <StatCard
                  label="Requests this month"
                  value={usage?.this_month ?? 0}
                />
                <StatCard
                  label="Credits remaining"
                  value={usage?.credits_remaining ?? 0}
                  sub="Need more? Go to Settings → Billing"
                />
              </div>
            </section>

            {/* API Keys */}
            <section>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">
                  API Keys
                </h2>
                {!showNewKeyForm && (
                  <button
                    onClick={() => setShowNewKeyForm(true)}
                    className="flex items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-sm text-zinc-300 hover:border-zinc-600 hover:bg-zinc-800 transition-colors"
                  >
                    <Plus size={14} />
                    New key
                  </button>
                )}
              </div>

              {/* New key form */}
              {showNewKeyForm && (
                <form
                  onSubmit={handleCreateKey}
                  className="mb-4 flex items-center gap-2 rounded-xl border border-zinc-700 bg-zinc-900 p-3"
                >
                  <Key size={16} className="shrink-0 text-zinc-500" />
                  <input
                    type="text"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    placeholder="Key name (optional)"
                    className="flex-1 bg-transparent text-sm text-zinc-200 placeholder-zinc-600 outline-none"
                    autoFocus
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewKeyForm(false)}
                    className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creating}
                    className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors"
                  >
                    {creating ? (
                      <Loader2 size={12} className="animate-spin" />
                    ) : (
                      <Plus size={12} />
                    )}
                    Create
                  </button>
                </form>
              )}

              {/* Key list */}
              <div className="space-y-3">
                {keys.length === 0 ? (
                  <div className="rounded-xl border border-dashed border-zinc-800 py-12 text-center">
                    <Key size={24} className="mx-auto mb-3 text-zinc-700" />
                    <p className="text-sm text-zinc-500">No API keys yet.</p>
                    <button
                      onClick={() => setShowNewKeyForm(true)}
                      className="mt-3 text-sm text-indigo-400 hover:underline"
                    >
                      Create your first key
                    </button>
                  </div>
                ) : (
                  keys.map((k) => (
                    <ApiKeyRow key={k.id} apiKey={k} onDelete={handleDeleteKey} />
                  ))
                )}
              </div>
            </section>

            {/* Quick start */}
            <section className="mt-12 rounded-xl border border-zinc-800 bg-zinc-900/30 p-6">
              <h2 className="mb-4 flex items-center gap-2 text-sm font-medium text-zinc-300">
                <Zap size={16} className="text-indigo-400" />
                Quick start
              </h2>
              <div className="space-y-2 text-sm text-zinc-400">
                <p>
                  <span className="text-zinc-200">1.</span> Copy your API key above.
                </p>
                <p>
                  <span className="text-zinc-200">2.</span> Make a POST request to{" "}
                  <code className="font-mono text-xs text-indigo-300">
                    {process.env.NEXT_PUBLIC_SNIPEX_API_URL ?? "https://api.snipex.dev"}/v1/search
                  </code>
                </p>
                <p>
                  <span className="text-zinc-200">3.</span> Include{" "}
                  <code className="font-mono text-xs text-zinc-300">
                    Authorization: Bearer &lt;your_key&gt;
                  </code>{" "}
                  in the headers.
                </p>
                <p>
                  <span className="text-zinc-200">4.</span>{" "}
                  <a
                    href="/playground"
                    className="text-indigo-400 hover:underline"
                  >
                    Try the playground
                  </a>{" "}
                  to see live results, or read the{" "}
                  <a
                    href="https://docs.snippex.ai"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-400 hover:underline"
                  >
                    full docs
                  </a>
                  .
                </p>
              </div>
            </section>

            {/* Usage chart */}
            <section className="mt-8 rounded-xl border border-zinc-800 bg-zinc-900/30 p-6">
              <h2 className="mb-6 flex items-center gap-2 text-sm font-medium text-zinc-300">
                <TrendingUp size={16} className="text-indigo-400" />
                Requests this month
              </h2>
              {usage?.daily_breakdown && usage.daily_breakdown.length > 0 ? (
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={usage.daily_breakdown} barCategoryGap="30%">
                    <XAxis
                      dataKey="date"
                      tickFormatter={(d: string) => new Date(d).getDate().toString()}
                      tick={{ fill: "#52525b", fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      allowDecimals={false}
                      tick={{ fill: "#52525b", fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      width={24}
                    />
                    <Tooltip
                      cursor={{ fill: "rgba(99,102,241,0.08)" }}
                      contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }}
                      labelFormatter={(d) => typeof d === "string" ? new Date(d).toLocaleDateString(undefined, { month: "short", day: "numeric" }) : d}
                      formatter={(v) => [v, "requests"]}
                    />
                    <Bar dataKey="request_count" fill="#6366f1" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center py-10 text-xs text-zinc-600">
                  No requests yet this month.
                </div>
              )}
            </section>
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}
