import { useQuery } from '@tanstack/react-query';
import { Brain, CheckCircle2, XCircle, Clock, Activity, AlertTriangle } from 'lucide-react';
import { apiClient } from '../api/client';

export function MLStatusCard() {
  const { data: status, isLoading } = useQuery({
    queryKey: ['ml-status'],
    queryFn: () => apiClient.get('/ml/status').then(res => res.data),
    refetchInterval: 30000,
  });
  
  if (isLoading) {
    return (
      <div className="bg-gradient-to-br from-purple-900/50 to-purple-800/50 border border-purple-800/50 rounded-xl p-6 shadow-sm flex items-center justify-center">
        <div className="animate-pulse flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-400" />
          <span className="text-purple-300">Loading Status...</span>
        </div>
      </div>
    );
  }

  const isEnabled = status?.enabled;

  return (
    <div className="bg-gradient-to-br from-purple-900/40 to-purple-800/40 border border-purple-700/50 rounded-xl p-6 shadow-sm">
      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-xl ${isEnabled ? 'bg-emerald-500/10 text-emerald-400' : 'bg-panel text-muted'}`}>
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-purple-200">ML Engine Status</h3>
            <div className="flex items-center gap-1.5 mt-1">
              {isEnabled ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <XCircle className="w-4 h-4 text-rose-500" />
              )}
              <span className={`text-xs font-semibold uppercase tracking-wider ${isEnabled ? 'text-emerald-400' : 'text-rose-500'}`}>
                {isEnabled ? 'Active & Ready' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-black/20 rounded-lg p-3 border border-purple-800/30">
          <div className="flex items-center gap-1.5 text-xs text-purple-300/70 mb-1">
            <Activity className="w-3.5 h-3.5" /> Model Version
          </div>
          <div className="text-sm font-mono font-semibold text-purple-100">
            {status?.model_version || 'N/A'}
          </div>
        </div>
        
        <div className="bg-black/20 rounded-lg p-3 border border-purple-800/30">
          <div className="flex items-center gap-1.5 text-xs text-purple-300/70 mb-1">
            <Clock className="w-3.5 h-3.5" /> Uptime
          </div>
          <div className="text-sm font-semibold text-purple-100">
            {status?.uptime_seconds ? `${Math.floor(status.uptime_seconds / 60)} mins` : 'N/A'}
          </div>
        </div>

        <div className="bg-black/20 rounded-lg p-3 border border-purple-800/30">
          <div className="flex items-center gap-1.5 text-xs text-purple-300/70 mb-1">
            <Activity className="w-3.5 h-3.5" /> Connections Eval
          </div>
          <div className="text-sm font-semibold text-purple-100">
            {status?.total_connections_evaluated?.toLocaleString() || '0'}
          </div>
        </div>

        <div className="bg-black/20 rounded-lg p-3 border border-purple-800/30">
          <div className="flex items-center gap-1.5 text-xs text-purple-300/70 mb-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Anomalies
          </div>
          <div className="text-sm font-semibold text-rose-300">
            {status?.total_anomalies_detected?.toLocaleString() || '0'}
          </div>
        </div>
      </div>
    </div>
  );
}
