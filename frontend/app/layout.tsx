import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "SentinelX AI-SOC | Security Operations Center",
  description:
    "Cloud-native SOC monitoring, Endpoint Detection & Response, and AI-powered threat investigation platform.",
  keywords: ["SOC", "EDR", "SIEM", "security", "threat detection", "cybersecurity"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-[#080c14] text-slate-100`}>
        {children}
      </body>
    </html>
  );
}
