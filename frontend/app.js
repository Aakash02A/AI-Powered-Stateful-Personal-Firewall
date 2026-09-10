// Minimalist API fetching for Firewall Dashboard
const API_BASE = window.FIREWALL_API_BASE || localStorage.getItem('firewall_api_base') || 'http://localhost:8000/api/v1';
const WS_URL = window.FIREWALL_WS_URL || localStorage.getItem('firewall_ws_url') || 'ws://localhost:8000/api/v1/ws';
const API_KEY = window.FIREWALL_API_KEY || localStorage.getItem('firewall_api_key') || '';
let currentAlerts = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    fetchAlerts();
    fetchRules();
    fetchAnalytics();
    fetchSettings();
    setupWebSocket();

    const refreshButton = document.getElementById('refresh-btn');
    if (refreshButton) refreshButton.addEventListener('click', refreshPageData);
    const addRuleButton = document.getElementById('add-rule-btn');
    if (addRuleButton) addRuleButton.addEventListener('click', addRule);
    const severityFilter = document.getElementById('severity-filter');
    if (severityFilter) severityFilter.addEventListener('change', () => fetchAlerts(severityFilter.value));
    const searchFilter = document.getElementById('alert-search');
    if (searchFilter) searchFilter.addEventListener('input', () => renderAlerts(currentAlerts));
    const exportButton = document.getElementById('export-alerts-btn');
    if (exportButton) exportButton.addEventListener('click', exportAlerts);
    const saveSettingsButton = document.getElementById('save-settings-btn');
    if (saveSettingsButton) saveSettingsButton.addEventListener('click', saveSettings);
    const blockingToggle = document.getElementById('blocking-toggle');
    if (blockingToggle) blockingToggle.addEventListener('click', () => setToggle(blockingToggle, !blockingToggle.classList.contains('active')));
    const mlToggle = document.getElementById('ml-toggle');
    if (mlToggle) mlToggle.addEventListener('click', () => setToggle(mlToggle, !mlToggle.classList.contains('active')));
    const analyticsRefresh = document.getElementById('analytics-refresh-btn');
    if (analyticsRefresh) analyticsRefresh.addEventListener('click', refreshPageData);
    document.querySelectorAll('.notifications').forEach(notification => {
        notification.addEventListener('click', () => { window.location.href = 'logs.html'; });
    });
});

function refreshPageData() {
    fetchStats();
    fetchAlerts(document.getElementById('severity-filter')?.value || '');
    fetchRules();
    fetchAnalytics();
}

async function apiGet(path) {
    const res = await fetch(`${API_BASE}${path}`, {
        headers: { 'X-API-Key': API_KEY },
    });
    if (!res.ok) throw new Error(`API request failed: ${res.status}`);
    return res.json();
}

async function fetchStats() {
    try {
        // Analytics endpoint provides general stats
        const res = await fetch(`${API_BASE}/stats`, { headers: { 'X-API-Key': API_KEY } });
        if (!res.ok) throw new Error('API Error');
        const json = await res.json();
        const data = json.data || {};
        
        const connections = document.getElementById('stat-connections');
        const threat = document.getElementById('stat-threat');
        const blocked = document.getElementById('stat-blocked');
        if (connections) connections.innerText = data.active_connections ?? '0';
        if (threat) threat.innerText = data.average_threat_score?.toFixed(1) ?? '0.0';
        if (blocked) blocked.innerText = data.blocked_connections ?? '0';
    } catch (e) {
        console.error('Failed to fetch stats:', e);
        ['stat-connections', 'stat-threat', 'stat-blocked'].forEach(id => {
            const element = document.getElementById(id);
            if (element) element.innerText = 'Unavailable';
        });
    }
}

async function fetchAlerts(severity = '') {
    try {
        const query = severity ? `&severity=${encodeURIComponent(severity)}` : '';
        const responseData = await apiGet(`/alerts?limit=100${query}`);
        currentAlerts = responseData.data || [];
        renderAlerts(currentAlerts);
    } catch (e) {
        console.error('Failed to fetch alerts:', e);
        const tbody = document.getElementById('alerts-table-body') || document.getElementById('logs-table-body');
        if (tbody) tbody.innerHTML = `<tr><td colspan="${tbody.id === 'logs-table-body' ? 6 : 5}" class="text-center text-danger py-4">Live alert data unavailable</td></tr>`;
    }
}

function renderAlerts(alerts) {
        const tbody = document.getElementById('alerts-table-body') || document.getElementById('logs-table-body');
        if (!tbody) return;
        const search = document.getElementById('alert-search')?.value.trim().toLowerCase() || '';
        alerts = alerts.filter(alert => !search || JSON.stringify(alert).toLowerCase().includes(search));
        tbody.innerHTML = '';
        
        if (alerts.length === 0) {
            const columns = tbody.id === 'logs-table-body' ? 6 : 5;
            tbody.innerHTML = `<tr><td colspan="${columns}" class="text-center text-muted py-4">No live alerts</td></tr>`;
            return;
        }

        alerts.forEach(alert => {
            const tr = document.createElement('tr');
            let badgeClass = 'bg-secondary';
            if (alert.severity === 'high') badgeClass = 'bg-danger';
            if (alert.severity === 'medium') badgeClass = 'bg-warning text-dark';
            const cells = tbody.id === 'logs-table-body'
                ? [new Date(alert.timestamp).toLocaleString(), `<span class="badge ${badgeClass}">${alert.severity}</span>`, alert.src_ip, alert.dst_ip, alert.description, alert.action_taken]
                : [new Date(alert.timestamp).toLocaleTimeString(), `<span class="badge ${badgeClass}">${alert.severity}</span>`, alert.src_ip, alert.dst_ip, alert.description];
            cells.forEach((value, index) => {
                const cell = document.createElement('td');
                if (index === 1) cell.innerHTML = value || '-';
                else cell.textContent = value || '-';
                tr.appendChild(cell);
            });
            tbody.appendChild(tr);
        });
}

async function fetchRules() {
    const tbody = document.getElementById('rules-table-body');
    if (!tbody) return;
    try {
        const responseData = await apiGet('/rules/');
        const rules = responseData.rules || [];
        tbody.innerHTML = rules.length ? '' : '<tr><td colspan="7" class="empty-state">No live firewall rules configured</td></tr>';
        rules.forEach(rule => {
            const row = document.createElement('tr');
            const values = [rule.enabled ? 'Active' : 'Disabled', rule.description || rule.rule_id, rule.action, rule.protocol, rule.dst_port, rule.direction];
            values.forEach((value, index) => {
                const cell = document.createElement('td');
                cell.textContent = value || '-';
                if (index === 0) cell.className = `rule-status ${rule.enabled ? 'active' : 'inactive'}`;
                row.appendChild(cell);
            });
            const actions = document.createElement('td');
            actions.innerHTML = `<button class="btn btn-outline" data-action="edit"><i class="fa-solid fa-pen"></i></button> <button class="btn btn-outline text-danger" data-action="delete"><i class="fa-solid fa-trash"></i></button>`;
            actions.querySelector('[data-action="edit"]').addEventListener('click', () => editRule(rule));
            actions.querySelector('[data-action="delete"]').addEventListener('click', () => deleteRule(rule));
            row.appendChild(actions);
            tbody.appendChild(row);
        });
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Live rule data unavailable</td></tr>';
    }
}

async function addRule() {
    const description = prompt('Rule description:');
    if (description === null) return;
    const response = await fetch(`${API_BASE}/rules/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': API_KEY },
        body: JSON.stringify({ description, action: 'allow' }),
    });
    if (!response.ok) return alert('Could not create rule.');
    fetchRules();
}

async function editRule(rule) {
    const description = prompt('Rule description:', rule.description || '');
    if (description === null) return;
    const response = await fetch(`${API_BASE}/rules/${encodeURIComponent(rule.rule_id)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': API_KEY },
        body: JSON.stringify({ ...rule, description }),
    });
    if (!response.ok) return alert('Could not update rule.');
    fetchRules();
}

async function deleteRule(rule) {
    if (!confirm(`Delete rule ${rule.description || rule.rule_id}?`)) return;
    const response = await fetch(`${API_BASE}/rules/${encodeURIComponent(rule.rule_id)}`, {
        method: 'DELETE',
        headers: { 'X-API-Key': API_KEY },
    });
    if (!response.ok) return alert('Could not delete rule.');
    fetchRules();
}

function exportAlerts() {
    const headers = ['timestamp', 'severity', 'src_ip', 'dst_ip', 'description', 'action_taken'];
    const rows = currentAlerts.map(alert => headers.map(header => JSON.stringify(alert[header] ?? '')).join(','));
    const blob = new Blob([[headers.join(','), ...rows].join('\n')], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'firewall-alerts.csv';
    link.click();
    URL.revokeObjectURL(link.href);
}

function setToggle(element, enabled) {
    element.classList.toggle('active', enabled);
    element.setAttribute('aria-checked', String(enabled));
    const label = element.nextElementSibling;
    if (label) label.textContent = enabled ? 'Enabled' : 'Disabled';
}

async function fetchSettings() {
    const blockingToggle = document.getElementById('blocking-toggle');
    if (!blockingToggle) return;
    try {
        const response = await apiGet('/settings');
        const data = response.data || {};
        setToggle(blockingToggle, !data.monitor_only);
        setToggle(document.getElementById('ml-toggle'), Boolean(data.ml_enabled));
        document.getElementById('rate-limit').value = data.rate_limit || 'Not configured';
        document.getElementById('threat-intel-status').value = data.threat_intel_configured ? 'Configured' : 'Not configured';
    } catch (e) {
        document.getElementById('blocking-status').textContent = 'Unavailable';
        document.getElementById('ml-status').textContent = 'Unavailable';
        document.getElementById('rate-limit').value = 'Unavailable';
        document.getElementById('threat-intel-status').value = 'Unavailable';
    }
}

async function saveSettings() {
    const response = await fetch(`${API_BASE}/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': API_KEY },
        body: JSON.stringify({
            monitor_only: !document.getElementById('blocking-toggle').classList.contains('active'),
            rate_limit: document.getElementById('rate-limit').value,
        }),
    });
    if (!response.ok) return alert('Could not save settings.');
    fetchSettings();
}

function renderProgress(container, values, emptyMessage) {
    if (!container) return;
    const entries = Object.entries(values || {});
    if (!entries.length) {
        container.innerHTML = `<p class="text-muted">${emptyMessage}</p>`;
        return;
    }
    const total = entries.reduce((sum, [, value]) => sum + Number(value || 0), 0);
    container.innerHTML = entries.map(([label, value]) => {
        const percent = total ? (Number(value || 0) / total) * 100 : 0;
        return `<div class="progress-item"><div class="progress-label"><span>${label}</span><span>${percent.toFixed(1)}%</span></div><div class="progress-track"><div class="progress-fill" style="width: ${percent}%;"></div></div></div>`;
    }).join('');
}

async function fetchAnalytics() {
    const blockedSources = document.getElementById('blocked-sources');
    const protocolBreakdown = document.getElementById('protocol-breakdown');
    if (!blockedSources && !protocolBreakdown) return;
    try {
        const [attackers, protocols, stats] = await Promise.all([
            apiGet('/top-attackers'),
            apiGet('/protocols'),
            apiGet('/stats'),
        ]);
        const talkerValues = {};
        (attackers.data || []).forEach(item => {
            const label = item.src_ip || item.ip || item.source_ip;
            const value = item.alert_count ?? item.count ?? item.connections ?? item.total_bytes;
            if (label && value !== undefined) talkerValues[label] = value;
        });
        renderProgress(blockedSources, talkerValues, 'No blocked-source data available');
        renderProgress(protocolBreakdown, protocols.data || {}, 'No protocol data available');
        const trafficChart = document.getElementById('traffic-chart');
        if (trafficChart) trafficChart.querySelector('span').innerHTML = `<i class="fa-solid fa-chart-line fa-2x mb-2 text-muted"></i><br>${stats.data?.total_connections ?? 0} persisted connections`;
        const threatChart = document.getElementById('threat-chart');
        if (threatChart) threatChart.querySelector('span').innerHTML = `<i class="fa-solid fa-chart-pie fa-2x mb-2 text-muted"></i><br>${stats.data?.total_alerts ?? 0} persisted alerts`;
    } catch (e) {
        if (blockedSources) blockedSources.innerHTML = '<p class="text-danger">Live analytics unavailable</p>';
        if (protocolBreakdown) protocolBreakdown.innerHTML = '<p class="text-danger">Live analytics unavailable</p>';
    }
}

function setupWebSocket() {
    const connectionStatus = document.getElementById('connection-status');
    if (!connectionStatus) return;
    const statusBadge = connectionStatus.querySelector('.badge');
    const ws = new WebSocket(`${WS_URL}/stream?api_key=${API_KEY}`);
    
    ws.onopen = () => {
        statusBadge.className = 'badge bg-success';
        statusBadge.innerText = 'Connected';
    };
    
    ws.onmessage = (event) => {
        // Handle incoming live alerts if needed
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'alert') {
                fetchAlerts(); // simple re-fetch
            }
        } catch(e) {}
    };
    
    ws.onclose = () => {
        statusBadge.className = 'badge bg-danger';
        statusBadge.innerText = 'Disconnected';
        setTimeout(setupWebSocket, 5000); // Reconnect
    };
    
    ws.onerror = () => {
        statusBadge.className = 'badge bg-danger';
        statusBadge.innerText = 'Error';
    };
}
