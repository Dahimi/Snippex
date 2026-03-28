import Link from "next/link";
import { CheckCircle } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function BillingSuccessPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex flex-1 flex-col items-center justify-center px-4 py-20 text-center">
        <CheckCircle size={48} className="mb-4 text-green-400" />
        <h1 className="text-2xl font-semibold text-zinc-50">Payment successful</h1>
        <p className="mt-2 text-sm text-zinc-400">
          Your credits have been added to your account. It may take a few seconds to reflect.
        </p>
        <Link
          href="/settings"
          className="mt-6 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 transition-colors"
        >
          Back to settings
        </Link>
      </main>
      <Footer />
    </div>
  );
}
