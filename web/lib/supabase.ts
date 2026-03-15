import { createClient } from "@supabase/supabase-js";

// ---------------------------------------------------------------------------
// Types matching supabase/schema.sql
// ---------------------------------------------------------------------------

export interface ApiKey {
  id: string;
  user_id: string;       // Clerk user ID
  name: string;
  key: string;           // snx_... — shown once at creation, then masked
  created_at: string;
  last_used_at: string | null;
}

export interface UsageStat {
  user_id: string;
  date: string;          // YYYY-MM-DD
  request_count: number;
}

export interface Credits {
  user_id: string;
  credits_remaining: number;
  updated_at: string;
}

// ---------------------------------------------------------------------------
// Client factory
// ---------------------------------------------------------------------------

function getSupabaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  if (!url) throw new Error("NEXT_PUBLIC_SUPABASE_URL is not set");
  return url;
}

function getSupabaseAnonKey(): string {
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!key) throw new Error("NEXT_PUBLIC_SUPABASE_ANON_KEY is not set");
  return key;
}

/** Browser/client-side Supabase client (uses anon key, RLS enforced). */
export function createBrowserClient() {
  return createClient(getSupabaseUrl(), getSupabaseAnonKey());
}

/** Server-side Supabase client with service role key (bypasses RLS). */
export function createServerClient() {
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!serviceKey) throw new Error("SUPABASE_SERVICE_ROLE_KEY is not set");
  return createClient(getSupabaseUrl(), serviceKey);
}

// ---------------------------------------------------------------------------
// Helper functions (server-side — call from API routes / server components)
// ---------------------------------------------------------------------------

/** Fetch all API keys for a user. Keys are masked (never expose raw value here). */
export async function getUserApiKeys(userId: string): Promise<ApiKey[]> {
  const db = createServerClient();
  const { data, error } = await db
    .from("api_keys")
    .select("id, user_id, name, key, created_at, last_used_at")
    .eq("user_id", userId)
    .order("created_at", { ascending: false });

  if (error) throw new Error(error.message);
  return (data ?? []) as ApiKey[];
}

/** Get usage stats for a user for a given date range. */
export async function getUserUsage(
  userId: string,
  fromDate: string, // YYYY-MM-DD
  toDate: string    // YYYY-MM-DD
): Promise<UsageStat[]> {
  const db = createServerClient();
  const { data, error } = await db
    .from("usage")
    .select("user_id, date, request_count")
    .eq("user_id", userId)
    .gte("date", fromDate)
    .lte("date", toDate)
    .order("date", { ascending: false });

  if (error) throw new Error(error.message);
  return (data ?? []) as UsageStat[];
}

/** Get credits for a user. */
export async function getUserCredits(userId: string): Promise<Credits | null> {
  const db = createServerClient();
  const { data, error } = await db
    .from("credits")
    .select("user_id, credits_remaining, updated_at")
    .eq("user_id", userId)
    .single();

  if (error && error.code !== "PGRST116") throw new Error(error.message);
  return (data as Credits) ?? null;
}

/** Generate a new API key. Returns the full key — show it once, then mask. */
export async function createApiKey(
  userId: string,
  name: string
): Promise<ApiKey> {
  const db = createServerClient();
  const rawKey = generateApiKey();

  const { data, error } = await db
    .from("api_keys")
    .insert({ user_id: userId, name, key: rawKey })
    .select()
    .single();

  if (error) throw new Error(error.message);
  return data as ApiKey;
}

/** Delete an API key by id (only if it belongs to the user). */
export async function deleteApiKey(
  userId: string,
  keyId: string
): Promise<void> {
  const db = createServerClient();
  const { error } = await db
    .from("api_keys")
    .delete()
    .eq("id", keyId)
    .eq("user_id", userId);

  if (error) throw new Error(error.message);
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function generateApiKey(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  const raw = Array.from(bytes)
    .map((b) => chars[b % chars.length])
    .join("");
  return `snx_${raw}`;
}

/** Mask an API key for display: snx_abc...xyz */
export function maskApiKey(key: string): string {
  if (key.length <= 12) return key;
  return `${key.slice(0, 8)}${"•".repeat(20)}${key.slice(-4)}`;
}
