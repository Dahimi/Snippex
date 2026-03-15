import Link from "next/link";

const DOCS_URL = process.env.NEXT_PUBLIC_DOCS_URL ?? "https://docs.snippex.com";

export default function Footer() {
  return (
    <footer className="border-t border-zinc-800 py-10 mt-20">
      <div className="mx-auto max-w-6xl px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <span className="font-mono text-sm text-zinc-500">
          snippex<span className="text-indigo-400">.</span>
        </span>
        <nav className="flex items-center gap-6 text-sm text-zinc-500">
          <Link href="/playground" className="hover:text-zinc-300 transition-colors">
            Playground
          </Link>
          <Link
            href={DOCS_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-zinc-300 transition-colors"
          >
            Docs
          </Link>
          <Link href="/dashboard" className="hover:text-zinc-300 transition-colors">
            Dashboard
          </Link>
        </nav>
        <p className="text-xs text-zinc-600">
          &copy; {new Date().getFullYear()} Snipex. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
