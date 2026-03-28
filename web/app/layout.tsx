import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Snippex — Search Snippet Extraction API",
    template: "%s | Snippex",
  },
  description:
    "Snippex returns the exact relevant passages from each search result — not just links. A search API built for developers.",
  openGraph: {
    title: "Snippex — Search Snippet Extraction API",
    description:
      "Snippex returns the exact relevant passages from each search result — not just links.",
    url: "https://snippex.ai",
    siteName: "Snippex",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Snippex — Search Snippet Extraction API",
    description:
      "Snippex returns the exact relevant passages from each search result — not just links.",
  },
  metadataBase: new URL("https://snippex.ai"),
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en" className="dark">
        <body className="min-h-screen bg-background text-zinc-50 antialiased">
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
