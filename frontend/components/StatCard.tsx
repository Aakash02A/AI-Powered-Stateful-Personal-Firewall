import { LucideIcon } from "lucide-react";

interface StatCardProps {
  id: string;
  label: string;
  value: string | number;
  suffix?: string;
  icon: LucideIcon;
  severity: "critical" | "high" | "medium" | "safe";
  trend?: string;
  trendUp?: boolean;
}

const SEVERITY_STYLES: Record<
  StatCardProps["severity"],
  { glow: string; text: string; bg: string }
> = {
  critical: {
    glow: "rgba(239,68,68,0.12)",
    text: "text-red-400",
    bg: "bg-red-500/10 border-red-500/20",
  },
  high: {
    glow: "rgba(249,115,22,0.12)",
    text: "text-orange-400",
    bg: "bg-orange-500/10 border-orange-500/20",
  },
  medium: {
    glow: "rgba(234,179,8,0.10)",
    text: "text-yellow-400",
    bg: "bg-yellow-500/10 border-yellow-500/20",
  },
  safe: {
    glow: "rgba(34,197,94,0.10)",
    text: "text-emerald-400",
    bg: "bg-emerald-500/10 border-emerald-500/20",
  },
};

export default function StatCard({
  id,
  label,
  value,
  suffix,
  icon: Icon,
  severity,
  trend,
  trendUp,
}: StatCardProps) {
  const styles = SEVERITY_STYLES[severity];

  return (
    <div
      id={id}
      className="glass-card stat-card"
      style={{ "--glow-color": styles.glow } as React.CSSProperties}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-2">
            {label}
          </p>
          <div className="flex items-baseline gap-1">
            <span className={`text-2xl font-bold tabular-nums ${styles.text}`}>{value}</span>
            {suffix && (
              <span className="text-sm text-[var(--color-text-muted)]">{suffix}</span>
            )}
          </div>
          {trend && (
            <p
              className={`text-xs mt-1.5 ${
                trendUp ? styles.text : "text-[var(--color-text-muted)]"
              }`}
            >
              {trend}
            </p>
          )}
        </div>
        <div className={`w-9 h-9 rounded-lg border flex items-center justify-center shrink-0 ${styles.bg}`}>
          <Icon className={`w-4 h-4 ${styles.text}`} />
        </div>
      </div>
    </div>
  );
}
