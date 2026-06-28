import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { DataTable, type Column } from '../components/DataTable';
import { apiClient } from '../api/client';
import { type AlertData } from '../components/AlertFeed';

export function Alerts() {
  const [severityFilter, setSeverityFilter] = useState<string>('');

  const { data: response, isLoading, refetch } = useQuery({
    queryKey: ['alerts', severityFilter],
    queryFn: () => {
      const params = new URLSearchParams();
      params.append('limit', '500');
      if (severityFilter) params.append('severity', severityFilter);
      return apiClient.get(`/alerts?${params.toString()}`).then(res => res.data);
    },
    refetchInterval: 10000,
  });

  const alerts: AlertData[] = response?.data || [];

  const markFalsePositive = async (id: number) => {
    try {
      await apiClient.post(`/alerts/${id}/false-positive`);
      refetch();
    } catch (e) {
      console.error("Failed to mark false positive", e);
    }
  };

  const columns: Column<AlertData>[] = [
    {
      key: 'timestamp',
      header: 'Time',
      sortable: true,
      render: (row) => format(new Date(row.timestamp), 'yyyy-MM-dd HH:mm:ss')
    },
    {
      key: 'severity',
      header: 'Severity',
      sortable: true,
      render: (row) => {
        const colors = {
          CRITICAL: 'bg-danger/20 text-danger border-danger/30',
          HIGH: 'bg-warning/20 text-warning border-warning/30',
          MEDIUM: 'bg-primary/20 text-primary border-primary/30',
          LOW: 'bg-success/20 text-success border-success/30',
        };
        const colorClass = colors[row.severity as keyof typeof colors] || colors.LOW;
        return (
          <span className={`px-2 py-1 rounded text-xs font-bold border ${colorClass}`}>
            {row.severity}
          </span>
        );
      }
    },
    { key: 'alert_type', header: 'Type', sortable: true },
    { key: 'src_ip', header: 'Source IP', sortable: true },
    { key: 'dst_ip', header: 'Dest IP', sortable: true },
    { key: 'description', header: 'Description', sortable: false },
    { 
      key: 'action_taken', 
      header: 'Action', 
      sortable: true,
      render: (row) => (
        <div className="flex items-center space-x-2">
          <span className="uppercase text-xs tracking-wider text-muted bg-panel px-2 py-1 rounded">
            {row.action_taken}
          </span>
          {row.alert_type === 'ml_anomaly' && row.action_taken !== 'false_positive' && (
            <button
              onClick={() => markFalsePositive(row.id!)}
              className="px-2 py-1 bg-panel-hover hover:bg-panel-hover text-foreground text-xs rounded transition-colors"
            >
              Mark False Positive
            </button>
          )}
        </div>
      )
    },
  ];

  return (
    <div className="h-full flex flex-col space-y-4">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-foreground tracking-tight">Security Alerts</h1>
          <p className="text-sm text-muted mt-1">Historical log of all detected network threats and anomalies.</p>
        </div>
        
        <div className="flex space-x-2">
          <select 
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-background border border-border text-foreground rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <DataTable 
          data={alerts} 
          columns={columns} 
          isLoading={isLoading} 
          searchPlaceholder="Search IP or description..."
        />
      </div>
    </div>
  );
}
