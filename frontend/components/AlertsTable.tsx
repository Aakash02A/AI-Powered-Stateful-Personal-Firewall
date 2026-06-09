const MOCK_ALERTS = [
  {
    id: "a1",
    title: "PowerShell Encoded Command",
    severity: "critical",
    endpoint: "DESKTOP-A1B2C3",
    mitre: "T1059.001",
    time: "2 min ago",
  },
  {
    id: "a2",
    title: "Suspicious Network Connection",
    severity: "high",
    endpoint: "LAPTOP-XY9812",
    mitre: "T1041",
    time: "8 min ago",
  },
  {
    id: "a3",
    title: "Registry Persistence Detected",
    severity: "high",
    endpoint: "SERVER-PROD-01",
    mitre: "T1547.001",
    time: "23 min ago",
  },
  {
    id: "a4",
    title: "Ransomware Extension Pattern",
    severity: "medium",
    endpoint: "WORKSTATION-003",
    mitre: "T1486",
    time: "45 min ago",
  },
  {
    id: "a5",
    title: "LOLBin Execution (certutil)",
    severity: "medium",
    endpoint: "DESKTOP-A1B2C3",
    mitre: "T1218",
    time: "1h ago",
  },
];

const SEVERITY_BADGE: Record<string, string> = {
  critical: "badge badge-critical",
  high: "badge badge-high",
  medium: "badge badge-medium",
  low: "badge badge-low",
};

export default function AlertsTable() {
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Alert</th>
          <th>Endpoint</th>
          <th>MITRE</th>
          <th>Severity</th>
          <th>Time</th>
        </tr>
      </thead>
      <tbody>
        {MOCK_ALERTS.map((alert) => (
          <tr key={alert.id} className="cursor-pointer">
            <td className="text-xs font-medium text-white">{alert.title}</td>
            <td className="text-xs font-mono text-[var(--color-text-muted)]">
              {alert.endpoint}
            </td>
            <td>
              <span className="text-xs font-mono text-blue-400">{alert.mitre}</span>
            </td>
            <td>
              <span className={SEVERITY_BADGE[alert.severity] ?? "badge"}>
                {alert.severity}
              </span>
            </td>
            <td className="text-xs text-[var(--color-text-muted)]">{alert.time}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
