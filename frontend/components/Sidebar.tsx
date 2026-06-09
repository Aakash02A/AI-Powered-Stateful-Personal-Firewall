"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Bell,
  Folder,
  Monitor,
  Shield,
  Search,
  FileText,
  Settings,
  Zap,
  ChevronRight,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard",   label: "Overview",        icon: LayoutDashboard },
  { href: "/alerts",      label: "Alert Center",    icon: Bell,    badge: "12" },
  { href: "/incidents",   label: "Incidents",       icon: Folder },
  { href: "/endpoints",   label: "Endpoints",       icon: Monitor },
  { href: "/threat-intel",label: "Threat Intel",    icon: Shield },
  { href: "/threat-hunt", label: "Threat Hunting",  icon: Search },
  { href: "/reports",     label: "Reports",         icon: FileText },
  { href: "/settings",    label: "Settings",        icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-[var(--color-border)] flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-600/30">
          <Zap className="w-4 h-4 text-white" />
        </div>
        <div>
          <div className="text-sm font-bold text-white tracking-wide">SentinelX</div>
          <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest">
            AI-SOC
          </div>
        </div>
      </div>

      {/* Live Status */}
      <div className="px-5 py-3 border-b border-[var(--color-border)] flex items-center gap-2">
        <div className="live-pulse"></div>
        <span className="text-xs text-[var(--color-text-muted)]">All systems operational</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 overflow-y-auto">
        <div className="mb-1 px-5 py-2">
          <span className="text-[10px] font-semibold uppercase tracking-widest text-[var(--color-text-muted)]">
            Operations
          </span>
        </div>
        {NAV_ITEMS.slice(0, 6).map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-item ${isActive ? "active" : ""}`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="flex-1">{item.label}</span>
              {item.badge && (
                <span className="text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/30 rounded-full px-1.5 py-0.5">
                  {item.badge}
                </span>
              )}
              {isActive && <ChevronRight className="w-3 h-3 opacity-50" />}
            </Link>
          );
        })}

        <div className="mb-1 px-5 py-2 mt-4">
          <span className="text-[10px] font-semibold uppercase tracking-widest text-[var(--color-text-muted)]">
            Management
          </span>
        </div>
        {NAV_ITEMS.slice(6).map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-item ${isActive ? "active" : ""}`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="flex-1">{item.label}</span>
              {isActive && <ChevronRight className="w-3 h-3 opacity-50" />}
            </Link>
          );
        })}
      </nav>

      {/* Bottom user area */}
      <div className="px-4 py-4 border-t border-[var(--color-border)]">
        <div className="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-[var(--color-brand-dim)] cursor-pointer transition-colors">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
            A
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-medium text-[var(--color-text-primary)] truncate">
              Admin
            </div>
            <div className="text-[10px] text-[var(--color-text-muted)]">Super Admin</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
