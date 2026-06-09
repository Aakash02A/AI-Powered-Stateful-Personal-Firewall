import type { Metadata } from "next";
import RoutePage from "@/components/RoutePage";

export const metadata: Metadata = {
  title: "Incidents — SentinelX AI-SOC",
};

export default function IncidentsPage() {
  return (
    <RoutePage
      title="Incidents"
      description="Investigate escalated alerts and coordinate response actions."
    >
      <div className="text-sm text-[var(--color-text-muted)]">Incident workspace coming online.</div>
    </RoutePage>
  );
}