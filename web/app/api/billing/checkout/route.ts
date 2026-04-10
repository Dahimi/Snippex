import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";

const BACKEND_URL = process.env.SNIPEX_API_URL ?? process.env.NEXT_PUBLIC_SNIPEX_API_URL ?? "https://api.snipex.dev";

/**
 * POST /api/billing/checkout
 * Proxies to the backend POST /v1/billing/checkout using the internal service key,
 * injecting the authenticated Clerk user's ID so credits land on the right account.
 */
export async function POST(req: NextRequest) {
  const { userId } = await auth();
  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const serviceKey = process.env.SNIPEX_INTERNAL_SERVICE_KEY;
  if (!serviceKey) {
    return NextResponse.json({ error: "Internal service key not configured" }, { status: 500 });
  }

  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  try {
    const upstream = await fetch(`${BACKEND_URL.replace(/\/$/, "")}/v1/billing/checkout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${serviceKey}`,
      },
      body: JSON.stringify({ ...body, user_id: userId }),
    });

    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
