/**
 * Snippex API — single source of truth for all types and fetch functions.
 * If the backend contract changes, update only this file.
 *
 * Backend: POST /v1/search  (FastAPI, see models/request.py + models/response.py)
 */

// ---------------------------------------------------------------------------
// Request types
// ---------------------------------------------------------------------------

export type SearchDepth = "precise" | "balanced" | "exhaustive";
export type Recency = "day" | "week" | "month" | "year";

export interface SearchRequest {
  query: string;
  num_results?: number;           // 1–10, default 5
  max_snippets_per_result?: number; // 1–5, default 3
  recency?: Recency | null;
  language?: string;              // default "en"
  include_domains?: string[];
  exclude_domains?: string[];
  search_depth?: SearchDepth;     // default "balanced"
}

// ---------------------------------------------------------------------------
// Response types
// ---------------------------------------------------------------------------

export interface Snippet {
  text: string;
  relevance_score: number;  // 0.0–1.0
}

export interface SearchResult {
  rank: number;
  url: string;
  title: string;
  snippets: Snippet[];
  publish_date?: string | null;
  last_updated?: string | null;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_latency_ms: number;
}

// ---------------------------------------------------------------------------
// Health check
// ---------------------------------------------------------------------------

export interface HealthResponse {
  status: "ok";
}

// ---------------------------------------------------------------------------
// Fetch helpers
// ---------------------------------------------------------------------------

/** Base URL for the Snippex backend — set via NEXT_PUBLIC_SNIPEX_API_URL */
function getApiBase(): string {
  const base = process.env.NEXT_PUBLIC_SNIPEX_API_URL;
  if (!base) throw new Error("NEXT_PUBLIC_SNIPEX_API_URL is not set");
  return base.replace(/\/$/, "");
}

/**
 * Call the Snippex /search endpoint directly (e.g. from server components or
 * authenticated server-side code). For client-side playground calls, use the
 * Next.js proxy route /api/search instead to avoid CORS and hide the backend URL.
 */
export async function searchDirect(
  request: SearchRequest,
  apiKey?: string
): Promise<SearchResponse> {
  const base = getApiBase();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (apiKey) {
    headers["Authorization"] = `Bearer ${apiKey}`;
  }

  const res = await fetch(`${base}/v1/search`, {
    method: "POST",
    headers,
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Search failed (${res.status}): ${text}`);
  }

  return res.json() as Promise<SearchResponse>;
}

/**
 * Call the Snippex /search endpoint via the Next.js proxy route.
 * Safe to use from browser — doesn't expose backend URL or API key.
 */
export async function searchViaProxy(
  request: SearchRequest
): Promise<SearchResponse> {
  const res = await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(
      (data as { error?: string }).error ?? `Search failed (${res.status})`
    );
  }

  return res.json() as Promise<SearchResponse>;
}

/**
 * Health check — useful for status pages or startup validation.
 */
export async function healthCheck(): Promise<HealthResponse> {
  const base = getApiBase();
  const res = await fetch(`${base}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json() as Promise<HealthResponse>;
}
