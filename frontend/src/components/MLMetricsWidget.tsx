import { useQuery } from '@tanstack/react-query';
import { Target, AlertTriangle, Zap, ArrowRightLeft } from 'lucide-react';
import { apiClient } from '../api/client';

export function MLMetricsWidget() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['ml-metrics'],
    queryFn: () => apiClient.get('/ml/metrics').then(res => res.data),
    refetchInterval: 60000,
  });

  if (isLoading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm flex items-center justify-center">
        <span className="text-slate-500 animate-pulse">Loading Metrics...</span>
      </div>
    );
  }

  const detection = metrics?.detection_metrics || {};
  const performance = metrics?.performance || {};

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {/* TP Rate Card (Green) */}
      <div className="bg-emerald-950/20 border border-emerald-900/30 rounded-xl p-4">
        <div className="flex items-center gap-2 text-emerald-500/70 mb-2">
          <Target className="w-4 h-4" />
          <span className="text-xs font-medium uppercase tracking-wider">True Positive</span>
        </div>
        <div className="text-2xl font-bold text-emerald-400">
          {detection.true_positive_rate ? `${(detection.true_positive_rate * 100).toFixed(1)}%` : '--'}
        </div>
      </div>

      {/* FP Rate Card (Red) */}
      <div className="bg-rose-950/20 border border-rose-900/30 rounded-xl p-4">
        <div className="flex items-center gap-2 text-rose-500/70 mb-2">
          <AlertTriangle className="w-4 h-4" />
          <span className="text-xs font-medium uppercase tracking-wider">False Positive</span>
        </div>
        <div className="text-2xl font-bold text-rose-400">
          {detection.false_positive_rate ? `${(detection.false_positive_rate * 100).toFixed(1)}%` : '--'}
        </div>
      </div>

      {/* Latency Card (Blue) */}
      <div className="bg-blue-950/20 border border-blue-900/30 rounded-xl p-4">
        <div className="flex items-center gap-2 text-blue-500/70 mb-2">
          <Zap className="w-4 h-4" />
          <span className="text-xs font-medium uppercase tracking-wider">Avg Latency</span>
        </div>
        <div className="text-2xl font-bold text-blue-400">
          {performance.average_latency_ms ? `${performance.average_latency_ms.toFixed(1)}ms` : '--'}
        </div>
      </div>

      {/* Throughput Card (Purple) */}
      <div className="bg-purple-950/20 border border-purple-900/30 rounded-xl p-4">
        <div className="flex items-center gap-2 text-purple-500/70 mb-2">
          <ArrowRightLeft className="w-4 h-4" />
          <span className="text-xs font-medium uppercase tracking-wider">Throughput</span>
        </div>
        <div className="text-2xl font-bold text-purple-400">
          {performance.throughput_per_second ? `${performance.throughput_per_second.toFixed(1)}/s` : '--'}
        </div>
      </div>
    </div>
  );
}
