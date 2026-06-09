import type { Metadata } from "next";
import RoutePage from "@/components/RoutePage";

export const metadata: Metadata = {
  title: "Settings — SentinelX AI-SOC",
};

export default function SettingsPage() {
  return (
    <RoutePage
      title="Settings"
      description="Configure user preferences, integrations, and access controls."
    >
      <div className="text-sm text-[var(--color-text-muted)]">Workspace settings will appear here.</div>
    </RoutePage>
  );
}