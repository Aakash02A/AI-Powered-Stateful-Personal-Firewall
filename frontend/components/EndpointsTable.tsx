const MOCK_ENDPOINTS = [
  { id: "e1", hostname: "DESKTOP-A1B2C3", os: "Windows 11", ip: "192.168.1.42", score: 78, status: "active", lastSeen: "Just now" },
  { id: "e2", hostname: "LAPTOP-XY9812", os: "Windows 10", ip: "192.168.1.67", score: 45, status: "active", lastSeen: "1 min ago" },
  { id: "e3", hostname: "SERVER-PROD-01", os: "Ubuntu 22.04", ip: "10.0.0.5", score: 12, status: "active", lastSeen: "3 min ago" },
  { id: "e4", hostname: "WORKSTATION-003", os: "macOS 14", ip: "192.168.1.88", score: 55, status: "isolated", lastSeen: "5 min ago" },
  { id: "e5", hostname: "DEVBOX-007", os: "Ubuntu 20.04", ip: "192.168.1.99", score: 5, status: "inactive", lastSeen: "2h ago" },
];

function ScoreBar({ score }: { score: number }) {
  const color =
    score >= 81 ? "#ef4444" :
    score >= 51 ? "#f97316" :
    score >= 21 ? "#eab308" :
    "#22c55e";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 rounded-full bg-[var(--color-bg-elevated)]">
        <div
          className="h-1.5 rounded-full transition-all duration-700"
          style={{ width: `${score}%`, background: color }}
        />
      </div>
      <span className="text-xs tabular-nums" style={{ color }}>{score}</span>
    </div>
  );
}

const STATUS_BADGE: Record<string, string> = {
  active: "text-emerald-400 bg-emerald-500/10 border border-emerald-500/20",
  isolated: "text-orange-400 bg-orange-500/10 border border-orange-500/20",
  inactive: "text-slate-500 bg-slate-500/10 border border-slate-500/20",
};

export default function EndpointsTable() {
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Hostname</th>
          <th>OS</th>
          <th>Status</th>
          <th>Threat Score</th>
          <th>Last Seen</th>
        </tr>
      </thead>
      <tbody>
        {MOCK_ENDPOINTS.map((ep) => (
          <tr key={ep.id} className="cursor-pointer">
            <td>
              <div className="text-xs font-mono text-white">{ep.hostname}</div>
              <div className="text-[10px] text-[var(--color-text-muted)]">{ep.ip}</div>
            </td>
            <td className="text-xs">{ep.os}</td>
            <td>
              <span className={`badge text-[10px] ${STATUS_BADGE[ep.status]}`}>
                {ep.status}
              </span>
            </td>
            <td className="min-w-[120px]">
              <ScoreBar score={ep.score} />
            </td>
            <td className="text-xs text-[var(--color-text-muted)]">{ep.lastSeen}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
