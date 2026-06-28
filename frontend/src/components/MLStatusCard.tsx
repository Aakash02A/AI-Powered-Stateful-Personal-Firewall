import { useQuery } from '@tanstack/react-query';
import { Brain, CheckCircle2, XCircle } from 'lucide-react';
import { apiClient } from '../api/client';

export function MLStatusCard() {
  const { data: mlStatusResponse, isLoading } = useQuery({
    queryKey: ['ml-status'],
    queryFn: () => apiClient.get('/ml/status').then(res => res.data),
    refetchInterval: 30000,
  });
  
  const { data: mlMetricsResponse } = useQuery({
    queryKey: ['ml-metrics'],
    queryFn: () => apiClient.get('/ml/metrics').then(res => res.data),
    refetchInterval: 60000,
  });

  const status = mlStatusResponse;
  const metrics = mlMetricsResponse?.data;
  
  if (isLoading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm flex items-center justify-center">
        <div className="animate-pulse flex items-center gap-2">
          <Brain className="w-5 h-5 text-slate-500" />
          <span className="text-slate-400">Loading ML Status...</span>
        </div>
      </div>
    );
  }

  const isEnabled = status?.enabled;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${isEnabled ? 'bg-indigo-500/10 text-indigo-400' : 'bg-slate-800 text-slate-500'}`}>
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-slate-300">ML Anomaly Detector</h3>
            <div className="flex items-center gap-1.5 mt-0.5">
              {isEnabled ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
              ) : (
                <XCircle className="w-3.5 h-3.5 text-rose-500" />
              )}
              <span className={`text-xs ${isEnabled ? 'text-emerald-500' : 'text-rose-500'}`}>
                {isEnabled ? 'Active & Monitoring' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>
        {status?.model_version && (
          <span className="px-2 py-1 bg-slate-800 rounded text-xs font-mono text-slate-400">
            {status.model_version}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 mt-6">
        <div>
          <div className="text-xs text-slate-500 mb-1">Detection Rate</div>
          <div className="text-lg font-semibold text-slate-200">
            {metrics?.anomaly_detection_rate ? `${(metrics.anomaly_detection_rate * 100).toFixed(1)}%` : '--'}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-500 mb-1">False Positive Rate</div>
          <div className="text-lg font-semibold text-slate-200">
            {metrics?.false_positive_rate ? `${(metrics.false_positive_rate * 100).toFixed(1)}%` : '--'}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-500 mb-1">Inference Latency</div>
          <div className="text-lg font-semibold text-slate-200">
            {metrics?.average_latency_ms ? `${metrics.average_latency_ms.toFixed(1)}ms` : '--'}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-500 mb-1">Engine Status</div>
          <div className="text-lg font-semibold text-slate-200 capitalize">
            {status?.status || 'Unknown'}
          </div>
        </div>
      </div>
    </div>
  );
}
