import type { Metadata } from "next";
import RoutePage from "@/components/RoutePage";

export const metadata: Metadata = {
  title: "Reports — SentinelX AI-SOC",
};

export default function ReportsPage() {
  return (
    <RoutePage
      title="Reports"
      description="Export security summaries, incidents, and operational metrics."
    >
      <div className="text-sm text-[var(--color-text-muted)]">Scheduled report generation will live here.</div>
    </RoutePage>
  );
}