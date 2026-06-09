"use client";

import { Bell, Search, Download } from "lucide-react";

export default function Topbar() {
  return (
    <header className="topbar gap-4">
      {/* Search */}
      <div className="flex-1 max-w-md relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]" />
        <input
          type="text"
          placeholder="Search events, IPs, hashes…"
          className="w-full pl-9 pr-4 py-1.5 rounded-lg bg-[var(--color-bg-elevated)] border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-brand)] transition-colors"
          id="topbar-search"
        />
      </div>

      <div className="flex items-center gap-3 ml-auto">
        {/* Agent Download */}
        <button
          id="download-agent-btn"
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 transition-colors text-white text-sm font-medium shadow-lg shadow-blue-600/25"
        >
          <Download className="w-4 h-4" />
          <span>Install Agent</span>
        </button>

        {/* Notifications */}
        <button
          id="notifications-btn"
          className="relative w-8 h-8 flex items-center justify-center rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors"
        >
          <Bell className="w-4 h-4 text-[var(--color-text-secondary)]" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
        </button>
      </div>
    </header>
  );
}
