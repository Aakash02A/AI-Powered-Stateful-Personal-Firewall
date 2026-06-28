import { useQuery } from '@tanstack/react-query';
import { ShieldAlert, AlertTriangle, Info, AlertOctagon } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { apiClient } from '../api/client';

interface Alert {
  id: number;
  timestamp: string;
  alert_type: string;
  severity: string;
  src_ip: string;
  dst_ip: string;
  description: string;
}

const getSeverityIcon = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return <AlertOctagon className="w-5 h-5 text-red-500" />;
    case 'high':
      return <ShieldAlert className="w-5 h-5 text-orange-500" />;
    case 'medium':
      return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    default:
      return <Info className="w-5 h-5 text-blue-500" />;
  }
};

const getSeverityColor = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-red-500/10 text-red-500 border-red-500/20';
    case 'high':
      return 'bg-orange-500/10 text-orange-500 border-orange-500/20';
    case 'medium':
      return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
    default:
      return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
  }
};

export function MLAlertsFeed() {
  const { data: alertsResponse, isLoading } = useQuery({
    queryKey: ['ml-alerts'],
    queryFn: () => apiClient.get('/alerts?alert_type=ml_anomaly&limit=10').then(res => res.data),
    refetchInterval: 5000,
  });

  const alerts: Alert[] = alertsResponse?.data || [];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-sm flex flex-col h-full max-h-[400px]">
      <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50 rounded-t-xl">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-purple-400" />
          Recent ML Anomalies
        </h3>
        <span className="text-xs font-medium text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full">
          Live
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {isLoading ? (
          <div className="flex flex-col gap-2 p-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="animate-pulse flex gap-3 p-3 bg-slate-800/50 rounded-lg">
                <div className="w-8 h-8 rounded-full bg-slate-700"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-3 bg-slate-700 rounded w-1/4"></div>
                  <div className="h-3 bg-slate-700 rounded w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        ) : alerts.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 p-6 text-center space-y-3">
            <ShieldAlert className="w-10 h-10 opacity-20" />
            <p className="text-sm">No recent ML anomalies detected.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-2 p-2">
            {alerts.map((alert) => (
              <div 
                key={alert.id}
                className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-800/50 transition-colors border border-transparent hover:border-slate-700"
              >
                <div className="shrink-0 mt-0.5">
                  {getSeverityIcon(alert.severity)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                    <span className="text-[11px] text-slate-500 whitespace-nowrap">
                      {formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                  <div className="text-sm font-medium text-slate-300 truncate font-mono">
                    {alert.src_ip} <span className="text-slate-500">→</span> {alert.dst_ip}
                  </div>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                    {alert.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
