import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import type { SearchRequest } from "@/lib/api";

/**
 * POST /api/search
 *
 * Client-side proxy to the Snipex backend.
 * - Hides the backend URL and API key from the browser
 * - Applies rate limiting for unauthenticated users (in-memory, resets on deploy)
 * - Authenticated users get a higher limit
 *
 * TODO: replace in-memory rate limit with Upstash Redis for production
 */

const ANON_LIMIT = 5;      // requests per IP per hour for unauthenticated users
const AUTHED_LIMIT = 100;  // requests per user per hour for authenticated users

// In-memory store: key → { count, resetAt }
// NOT suitable for multi-instance deployments — replace with Redis in production
const rateStore = new Map<string, { count: number; resetAt: number }>();

function checkRateLimit(key: string, limit: number): { allowed: boolean; remaining: number } {
  const now = Date.now();
  const entry = rateStore.get(key);

  if (!entry || now > entry.resetAt) {
    rateStore.set(key, { count: 1, resetAt: now + 60 * 60 * 1000 });
    return { allowed: true, remaining: limit - 1 };
  }

  if (entry.count >= limit) {
    return { allowed: false, remaining: 0 };
  }

  entry.count += 1;
  return { allowed: true, remaining: limit - entry.count };
}

function getClientIp(req: NextRequest): string {
  return (
    req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ??
    req.headers.get("x-real-ip") ??
    "unknown"
  );
}

export async function POST(req: NextRequest) {
  // Auth check
  const { userId } = await auth();

  // Rate limiting
  const rateLimitKey = userId ? `user:${userId}` : `ip:${getClientIp(req)}`;
  const limit = userId ? AUTHED_LIMIT : ANON_LIMIT;
  const { allowed, remaining } = checkRateLimit(rateLimitKey, limit);

  if (!allowed) {
    return NextResponse.json(
      { error: "Rate limit exceeded. Sign in for higher limits." },
      {
        status: 429,
        headers: { "X-RateLimit-Remaining": "0" },
      }
    );
  }

  // Parse + validate request body
  let body: SearchRequest;
  try {
    body = (await req.json()) as SearchRequest;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  if (!body.query || typeof body.query !== "string") {
    return NextResponse.json({ error: "query is required" }, { status: 400 });
  }

  // Forward to backend
  const backendUrl = process.env.SNIPEX_API_URL ?? process.env.NEXT_PUBLIC_SNIPEX_API_URL;
  if (!backendUrl) {
    return NextResponse.json(
      { error: "Backend URL not configured" },
      { status: 500 }
    );
  }

  const serviceKey = process.env.SNIPEX_INTERNAL_SERVICE_KEY;
  if (!serviceKey) {
    return NextResponse.json(
      { error: "Internal service key not configured" },
      { status: 500 }
    );
  }

  try {
    const upstream = await fetch(`${backendUrl.replace(/\/$/, "")}/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${serviceKey}`,
      },
      body: JSON.stringify(body),
    });

    const data = await upstream.json();

    if (!upstream.ok) {
      return NextResponse.json(data, { status: upstream.status });
    }

    return NextResponse.json(data, {
      headers: { "X-RateLimit-Remaining": String(remaining) },
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
