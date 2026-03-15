import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { getUserApiKeys, createApiKey } from "@/lib/supabase";

/**
 * GET /api/keys  — list API keys for the authenticated user
 * POST /api/keys — create a new API key
 */

export async function GET() {
  const { userId } = await auth();
  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const keys = await getUserApiKeys(userId);
    // Mask keys before sending to client
    const masked = keys.map((k) => ({
      ...k,
      key: `${k.key.slice(0, 8)}${"•".repeat(20)}${k.key.slice(-4)}`,
    }));
    return NextResponse.json({ keys: masked });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  const { userId } = await auth();
  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await req.json().catch(() => ({})) as { name?: string };
  const name = typeof body.name === "string" && body.name.trim()
    ? body.name.trim()
    : "Default";

  try {
    const key = await createApiKey(userId, name);
    // Return the full key ONCE — after this it's masked in the DB view
    return NextResponse.json({ key }, { status: 201 });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
