"use client";

import Link from "next/link";
import { SignInButton, SignUpButton, SignedIn, SignedOut, useUser, useClerk } from "@clerk/nextjs";
import { usePathname } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { LayoutDashboard, Settings, LogOut } from "lucide-react";
import clsx from "clsx";

const DOCS_URL = process.env.NEXT_PUBLIC_DOCS_URL ?? "https://docs.snippex.ai";

const navLinks = [
  { href: "/playground", label: "Playground" },
  { href: DOCS_URL, label: "Docs", external: true },
];

function UserMenu() {
  const { user } = useUser();
  const { signOut } = useClerk();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const initials = user?.fullName
    ? user.fullName.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase()
    : user?.primaryEmailAddress?.emailAddress?.[0]?.toUpperCase() ?? "?";

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-xs font-semibold text-white hover:bg-indigo-500 transition-colors focus:outline-none"
        aria-label="Account menu"
      >
        {user?.imageUrl ? (
          <img src={user.imageUrl} alt="" className="h-8 w-8 rounded-full object-cover" />
        ) : (
          initials
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-52 rounded-xl border border-zinc-800 bg-zinc-950 py-1 shadow-xl">
          <div className="border-b border-zinc-800 px-3 py-2.5">
            <p className="truncate text-sm font-medium text-zinc-100">{user?.fullName ?? "Account"}</p>
            <p className="truncate text-xs text-zinc-500">{user?.primaryEmailAddress?.emailAddress}</p>
          </div>
          <div className="py-1">
            <Link
              href="/dashboard"
              onClick={() => setOpen(false)}
              className={clsx(
                "flex items-center gap-2.5 px-3 py-2 text-sm transition-colors hover:bg-zinc-800",
                pathname.startsWith("/dashboard") ? "text-zinc-100" : "text-zinc-300"
              )}
            >
              <LayoutDashboard size={14} className="text-zinc-500" />
              Dashboard
            </Link>
            <Link
              href="/settings"
              onClick={() => setOpen(false)}
              className={clsx(
                "flex items-center gap-2.5 px-3 py-2 text-sm transition-colors hover:bg-zinc-800",
                pathname.startsWith("/settings") ? "text-zinc-100" : "text-zinc-300"
              )}
            >
              <Settings size={14} className="text-zinc-500" />
              Settings
            </Link>
          </div>
          <div className="border-t border-zinc-800 py-1">
            <button
              onClick={() => signOut()}
              className="flex w-full items-center gap-2.5 px-3 py-2 text-sm text-zinc-300 transition-colors hover:bg-zinc-800 hover:text-red-400"
            >
              <LogOut size={14} className="text-zinc-500" />
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

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
          snippex
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
            <UserMenu />
          </SignedIn>
        </div>
      </div>
    </header>
  );
}
