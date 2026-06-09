import type { Metadata } from "next";
import RoutePage from "@/components/RoutePage";

export const metadata: Metadata = {
  title: "Threat Hunting — SentinelX AI-SOC",
};

export default function ThreatHuntPage() {
  return (
    <RoutePage
      title="Threat Hunting"
      description="Search across events, endpoints, and suspicious patterns."
    >
      <div className="text-sm text-[var(--color-text-muted)]">Hunting queries and saved investigations coming soon.</div>
    </RoutePage>
  );
}