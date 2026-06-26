import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('*/api/v1/stats', () => {
    return HttpResponse.json({
      data: {
        active_connections: 142,
        blocked_ips: 8,
        total_packets: 1234,
        total_alerts: 5
      }
    });
  }),
  
  http.get('*/api/v1/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      version: '1.0.0'
    });
  }),
  
  http.get('*/api/v1/connections', () => {
    return HttpResponse.json([
      { id: '1', src_ip: '192.168.1.1', dst_ip: '8.8.8.8', protocol: 'TCP', bytes: 1024, status: 'ALLOWED' },
    ]);
  }),

  http.get('*/api/v1/protocols', () => {
    return HttpResponse.json({
      data: { TCP: 50, UDP: 30, ICMP: 20 }
    });
  }),
  
  http.get('*/api/v1/alerts', () => {
    return HttpResponse.json({
      status: 'success',
      data: [
        { id: '1', alert_type: 'SCAN', severity: 'HIGH', src_ip: '1.2.3.4', dst_ip: '5.6.7.8', timestamp: '2026-06-26T10:00:00Z', description: 'Port scan' },
      ]
    });
  }),
];
