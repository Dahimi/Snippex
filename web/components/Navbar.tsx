"use client";

import Link from "next/link";
import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { usePathname } from "next/navigation";
import clsx from "clsx";

const DOCS_URL = process.env.NEXT_PUBLIC_DOCS_URL ?? "https://docs.snipex.com";

const navLinks = [
  { href: "/playground", label: "Playground" },
  { href: DOCS_URL, label: "Docs", external: true },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-zinc-800 bg-background/90 backdrop-blur-sm">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        {/* Logo */}
        <Link
          href="/"
          className="font-mono text-lg font-semibold tracking-tight text-zinc-50 hover:text-white transition-colors"
        >
          snipex
          <span className="text-indigo-400">.</span>
        </Link>

        {/* Nav links */}
        <nav className="hidden sm:flex items-center gap-6">
          {navLinks.map(({ href, label, external }) => (
            <Link
              key={href}
              href={href}
              target={external ? "_blank" : undefined}
              rel={external ? "noopener noreferrer" : undefined}
              className={clsx(
                "text-sm transition-colors",
                pathname === href
                  ? "text-zinc-50"
                  : "text-zinc-400 hover:text-zinc-200"
              )}
            >
              {label}
            </Link>
          ))}
        </nav>

        {/* Auth */}
        <div className="flex items-center gap-3">
          <SignedOut>
            <SignInButton mode="modal">
              <button className="text-sm text-zinc-400 hover:text-zinc-200 transition-colors">
                Sign in
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="rounded-md bg-indigo-600 px-3.5 py-1.5 text-sm font-medium text-white hover:bg-indigo-500 transition-colors">
                Get started
              </button>
            </SignUpButton>
          </SignedOut>

          <SignedIn>
            <Link
              href="/dashboard"
              className={clsx(
                "text-sm transition-colors",
                pathname.startsWith("/dashboard")
                  ? "text-zinc-50"
                  : "text-zinc-400 hover:text-zinc-200"
              )}
            >
              Dashboard
            </Link>
            <UserButton
              appearance={{
                elements: {
                  avatarBox: "w-8 h-8",
                },
              }}
            />
          </SignedIn>
        </div>
      </div>
    </header>
  );
}
