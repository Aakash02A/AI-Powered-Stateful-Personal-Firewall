import { useState, useEffect } from 'react'
import './index.css'

function App() {
  const [stats, setStats] = useState({ active_agents: 0, total_logs: 0, total_threats: 0, recent_threats: [] });
  const [agents, setAgents] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const API_URL = 'http://localhost:8000/api';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsRes = await fetch(`${API_URL}/stats`);
        const statsData = await statsRes.json();
        setStats(statsData);

        const agentsRes = await fetch(`${API_URL}/agents`);
        const agentsData = await agentsRes.json();
        setAgents(agentsData);

        const logsRes = await fetch(`${API_URL}/logs?limit=5`);
        const logsData = await logsRes.json();
        setLogs(logsData);
        
        setLoading(false);
      } catch (error) {
        console.error("Error fetching data:", error);
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000); // Poll every 3 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh'}}>Loading GuardianWeb Cloud...</div>;
  }

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="logo">GuardianWeb</div>
        <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
          <span style={{color: 'var(--text-muted)'}}><span className="live-indicator"></span>System Live</span>
          <button className="btn">Download Agent</button>
        </div>
      </nav>

      <main className="main-content">
        <div className="dashboard-grid">
          
          <div className="stats-container">
            <div className="glass-panel stat-card">
              <span className="stat-title">Active Agents</span>
              <span className="stat-value">{stats.active_agents}</span>
            </div>
            <div className="glass-panel stat-card">
              <span className="stat-title">Total Logs Processed</span>
              <span className="stat-value">{stats.total_logs}</span>
            </div>
            <div className="glass-panel stat-card danger">
              <span className="stat-title">Critical Threats</span>
              <span className="stat-value">{stats.recent_threats.length}</span>
            </div>
            <div className="glass-panel stat-card success">
              <span className="stat-title">Total Threats Blocked</span>
              <span className="stat-value">{stats.total_threats}</span>
            </div>
          </div>

          <div className="glass-panel table-container">
            <h2 className="table-title">Recent Threat Detections</h2>
            {stats.recent_threats.length === 0 ? (
              <p style={{color: 'var(--text-muted)'}}>No critical threats detected recently. System is secure.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Agent ID</th>
                    <th>Source IP</th>
                    <th>Threat Type</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recent_threats.map((threat, i) => (
                    <tr key={i}>
                      <td>{new Date(threat.timestamp).toLocaleString()}</td>
                      <td style={{fontFamily: 'monospace', color: 'var(--accent-primary)'}}>{threat.agent_id.substring(0,8)}...</td>
                      <td>{threat.source_ip}</td>
                      <td>{threat.threat_type}</td>
                      <td><span className={`badge ${threat.severity}`}>{threat.severity}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="glass-panel table-container">
            <h2 className="table-title">Connected Agents</h2>
            {agents.length === 0 ? (
              <p style={{color: 'var(--text-muted)'}}>No agents connected. Download the agent to start monitoring.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Hostname</th>
                    <th>OS Info</th>
                    <th>IP Address</th>
                    <th>Last Seen</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {agents.map((agent, i) => (
                    <tr key={i}>
                      <td>{agent.hostname}</td>
                      <td>{agent.os_info}</td>
                      <td>{agent.ip_address}</td>
                      <td>{new Date(agent.last_seen).toLocaleString()}</td>
                      <td><span className="badge active">Active</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

        </div>
      </main>
    </div>
  )
}

export default App
