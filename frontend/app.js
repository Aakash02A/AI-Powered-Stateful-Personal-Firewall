// Minimalist API fetching for Firewall Dashboard
const API_BASE = 'http://localhost:8000/api/v1';
const WS_URL = 'ws://localhost:8000/api/v1/ws';
const API_KEY = 'default_dev_key'; // Update this if backend .env uses a different key

document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    fetchAlerts();
    setupWebSocket();

    document.getElementById('refresh-btn').addEventListener('click', () => {
        fetchStats();
        fetchAlerts();
    });
});

async function fetchStats() {
    try {
        // Analytics endpoint provides general stats
        const res = await fetch(`${API_BASE}/stats`, { headers: { 'X-API-Key': API_KEY } });
        if (!res.ok) throw new Error('API Error');
        const json = await res.json();
        const data = json.data || {};
        
        document.getElementById('stat-connections').innerText = data.active_connections || '0';
        document.getElementById('stat-threat').innerText = data.average_threat_score?.toFixed(1) || '0.0';
        document.getElementById('stat-blocked').innerText = data.blocked_connections || '0';
    } catch (e) {
        console.error('Failed to fetch stats:', e);
        document.getElementById('stat-connections').innerText = 'Err';
        document.getElementById('stat-threat').innerText = 'Err';
        document.getElementById('stat-blocked').innerText = 'Err';
    }
}

async function fetchAlerts() {
    try {
        const res = await fetch(`${API_BASE}/logs/alerts?limit=10`, { headers: { 'X-API-Key': API_KEY } });
        if (!res.ok) throw new Error('API Error');
        const responseData = await res.json();
        const alerts = responseData.data || [];
        
        const tbody = document.getElementById('alerts-table-body');
        tbody.innerHTML = '';
        
        if (alerts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">No recent alerts</td></tr>';
            return;
        }

        alerts.forEach(alert => {
            const tr = document.createElement('tr');
            
            // Format severity badge
            let badgeClass = 'bg-secondary';
            if (alert.severity === 'high') badgeClass = 'bg-danger';
            if (alert.severity === 'medium') badgeClass = 'bg-warning text-dark';
            
            tr.innerHTML = `
                <td>${new Date(alert.timestamp).toLocaleTimeString()}</td>
                <td><span class="badge ${badgeClass}">${alert.severity}</span></td>
                <td>${alert.src_ip || '-'}</td>
                <td>${alert.dst_ip || '-'}</td>
                <td>${alert.description || '-'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error('Failed to fetch alerts:', e);
        document.getElementById('alerts-table-body').innerHTML = '<tr><td colspan="5" class="text-center text-danger py-4">Failed to load alerts</td></tr>';
    }
}

function setupWebSocket() {
    const statusBadge = document.getElementById('connection-status').querySelector('.badge');
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
