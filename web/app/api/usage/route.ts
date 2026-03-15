import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { getUserUsage, getUserCredits } from "@/lib/supabase";

/**
 * GET /api/usage — return usage stats + credits for the authenticated user
 */
export async function GET() {
  const { userId } = await auth();
  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const today = new Date();
  const todayStr = today.toISOString().slice(0, 10);

  // First day of current month
  const firstOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
    .toISOString()
    .slice(0, 10);

  try {
    const [usage, credits] = await Promise.all([
      getUserUsage(userId, firstOfMonth, todayStr),
      getUserCredits(userId),
    ]);

    const todayUsage = usage.find((u) => u.date === todayStr)?.request_count ?? 0;
    const monthUsage = usage.reduce((sum, u) => sum + u.request_count, 0);

    return NextResponse.json({
      today: todayUsage,
      this_month: monthUsage,
      credits_remaining: credits?.credits_remaining ?? 0,
      daily_breakdown: usage,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
