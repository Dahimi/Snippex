import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { Redis } from "@upstash/redis";
import type { SearchRequest } from "@/lib/api";

const ANON_LIMIT = 5;     // requests per IP per hour (unauthenticated)
const AUTHED_LIMIT = 100; // requests per user per hour (authenticated, playground only)
const WINDOW_SECONDS = 3600;

function getRedis(): Redis | null {
  const url = process.env.UPSTASH_REDIS_URL;
  const token = process.env.UPSTASH_REDIS_TOKEN;
  if (!url || !token) return null;
  return new Redis({ url, token });
}

async function checkRateLimit(
  redis: Redis | null,
  key: string,
  limit: number
): Promise<{ allowed: boolean; remaining: number }> {
  if (!redis) {
    // Redis not configured — fall back to allow (better than blocking everyone)
    return { allowed: true, remaining: limit };
  }

  const count = await redis.incr(key);
  if (count === 1) await redis.expire(key, WINDOW_SECONDS);

  const remaining = Math.max(0, limit - count);
  return { allowed: count <= limit, remaining };
}

function getClientIp(req: NextRequest): string {
  return (
    req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ??
    req.headers.get("x-real-ip") ??
    "unknown"
  );
}

export async function POST(req: NextRequest) {
  const { userId } = await auth();

  const redis = getRedis();
  const rateLimitKey = userId
    ? `snx:playground:user:${userId}`
    : `snx:playground:ip:${getClientIp(req)}`;
  const limit = userId ? AUTHED_LIMIT : ANON_LIMIT;

  const { allowed, remaining } = await checkRateLimit(redis, rateLimitKey, limit);

  if (!allowed) {
    return NextResponse.json(
      { error: "Rate limit exceeded. Sign in for higher limits." },
      { status: 429, headers: { "X-RateLimit-Remaining": "0" } }
    );
  }

  let body: SearchRequest;
  try {
    body = (await req.json()) as SearchRequest;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  if (!body.query || typeof body.query !== "string") {
    return NextResponse.json({ error: "query is required" }, { status: 400 });
  }

  const backendUrl = process.env.SNIPEX_API_URL ?? process.env.NEXT_PUBLIC_SNIPEX_API_URL;
  if (!backendUrl) {
    return NextResponse.json({ error: "Backend URL not configured" }, { status: 500 });
  }

  const serviceKey = process.env.SNIPEX_INTERNAL_SERVICE_KEY;
  if (!serviceKey) {
    return NextResponse.json({ error: "Internal service key not configured" }, { status: 500 });
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
