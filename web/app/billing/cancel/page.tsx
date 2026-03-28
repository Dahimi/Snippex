import Link from "next/link";
import { XCircle } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function BillingCancelPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex flex-1 flex-col items-center justify-center px-4 py-20 text-center">
        <XCircle size={48} className="mb-4 text-zinc-500" />
        <h1 className="text-2xl font-semibold text-zinc-50">Payment cancelled</h1>
        <p className="mt-2 text-sm text-zinc-400">
          No charge was made. You can try again from your settings page.
        </p>
        <Link
          href="/settings"
          className="mt-6 rounded-lg border border-zinc-700 bg-zinc-900 px-5 py-2.5 text-sm font-medium text-zinc-300 hover:border-zinc-600 hover:bg-zinc-800 transition-colors"
        >
          Back to settings
        </Link>
      </main>
      <Footer />
    </div>
  );
}
