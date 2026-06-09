import type { Metadata } from "next";
import RoutePage from "@/components/RoutePage";
import EndpointsTable from "@/components/EndpointsTable";

export const metadata: Metadata = {
  title: "Endpoints — SentinelX AI-SOC",
};

export default function EndpointsPage() {
  return (
    <RoutePage
      title="Endpoints"
      description="Track connected hosts, status, and threat score at a glance."
    >
      <EndpointsTable />
    </RoutePage>
  );
}