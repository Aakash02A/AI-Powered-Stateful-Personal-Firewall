import type { Metadata } from "next";
import RoutePage from "@/components/RoutePage";
import AlertsTable from "@/components/AlertsTable";

export const metadata: Metadata = {
  title: "Alert Center — SentinelX AI-SOC",
};

export default function AlertsPage() {
  return (
    <RoutePage
      title="Alert Center"
      description="Review active detections, severities, and response status."
    >
      <AlertsTable />
    </RoutePage>
  );
}