import type { Metadata } from "next";
import StatCard from "@/components/StatCard";
import AlertsTable from "@/components/AlertsTable";
import EndpointsTable from "@/components/EndpointsTable";
import ThreatChart from "@/components/ThreatChart";
import {
  Shield,
  AlertTriangle,
  Monitor,
  TrendingUp,
  Activity,
  Cpu,
  Folder,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Overview — SentinelX AI-SOC",
};

// In production: fetch from API with React Query / server component
async function getDashboardStats() {
  return {
    threat_score: 34,
    active_endpoints: 127,
    open_alerts: 12,
    critical_alerts: 3,
    open_incidents: 2,
    events_per_minute: 2840,
  };
}

export default async function DashboardPage() {
  const stats = await getDashboardStats();

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* Page header */}
      <div>
        <h1 className="text-xl font-bold text-white">Security Overview</h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-0.5">
          Real-time threat monitoring across all endpoints
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          id="stat-threat-score"
          label="Threat Score"
          value={stats.threat_score}
          suffix="/100"
          icon={Shield}
          severity="medium"
          trend="-5 from yesterday"
          trendUp={false}
        />
        <StatCard
          id="stat-endpoints"
          label="Active Endpoints"
          value={stats.active_endpoints}
          icon={Monitor}
          severity="safe"
          trend="+3 today"
          trendUp={true}
        />
        <StatCard
          id="stat-open-alerts"
          label="Open Alerts"
          value={stats.open_alerts}
          icon={AlertTriangle}
          severity="high"
          trend="4 new"
          trendUp={true}
        />
        <StatCard
          id="stat-critical"
          label="Critical"
          value={stats.critical_alerts}
          icon={AlertTriangle}
          severity="critical"
          trend="Requires action"
          trendUp={true}
        />
        <StatCard
          id="stat-incidents"
          label="Open Incidents"
          value={stats.open_incidents}
          icon={Folder}
          severity="medium"
          trend="Stable"
          trendUp={false}
        />
        <StatCard
          id="stat-events"
          label="Events/min"
          value={stats.events_per_minute.toLocaleString()}
          icon={Activity}
          severity="safe"
          trend="Normal"
          trendUp={false}
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Event Timeline (24h)</h2>
            <TrendingUp className="w-4 h-4 text-[var(--color-text-muted)]" />
          </div>
          <ThreatChart />
        </div>

        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Alert Severity Split</h2>
            <Cpu className="w-4 h-4 text-[var(--color-text-muted)]" />
          </div>
          <div className="space-y-3 mt-4">
            {[
              { label: "Critical", count: 3, color: "var(--color-critical)", pct: 25 },
              { label: "High", count: 5, color: "var(--color-high)", pct: 42 },
              { label: "Medium", count: 3, color: "var(--color-medium)", pct: 25 },
              { label: "Low", count: 1, color: "var(--color-low)", pct: 8 },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-xs mb-1">
                  <span style={{ color: item.color }} className="font-medium">
                    {item.label}
                  </span>
                  <span className="text-[var(--color-text-muted)]">{item.count}</span>
                </div>
                <div className="h-1.5 rounded-full bg-[var(--color-bg-elevated)]">
                  <div
                    className="h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${item.pct}%`, background: item.color }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tables row */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="glass-card">
          <div className="px-5 py-4 border-b border-[var(--color-border)] flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Recent Alerts</h2>
            <a href="/alerts" className="text-xs text-[var(--color-brand)] hover:underline">
              View all
            </a>
          </div>
          <AlertsTable />
        </div>

        <div className="glass-card">
          <div className="px-5 py-4 border-b border-[var(--color-border)] flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Connected Endpoints</h2>
            <a href="/endpoints" className="text-xs text-[var(--color-brand)] hover:underline">
              View all
            </a>
          </div>
          <EndpointsTable />
        </div>
      </div>
    </div>
  );
}
