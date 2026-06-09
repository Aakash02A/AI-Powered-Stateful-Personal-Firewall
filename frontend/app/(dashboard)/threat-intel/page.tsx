import type { Metadata } from "next";
import RoutePage from "@/components/RoutePage";

export const metadata: Metadata = {
  title: "Threat Intel — SentinelX AI-SOC",
};

export default function ThreatIntelPage() {
  return (
    <RoutePage
      title="Threat Intel"
      description="Enrichment feeds, IOC lookups, and external reputation data."
    >
      <div className="text-sm text-[var(--color-text-muted)]">IOC enrichment feeds will appear here.</div>
    </RoutePage>
  );
}