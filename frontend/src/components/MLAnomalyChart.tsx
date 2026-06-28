import { useQuery } from '@tanstack/react-query';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { BrainCircuit } from 'lucide-react';
import { apiClient } from '../api/client';

interface AnomalyWindow {
  timestamp: string;
  average_score: number;
  max_score: number;
  anomaly_count: number;
}

export function MLAnomalyChart() {
  const { data: scoresResponse, isLoading } = useQuery({
    queryKey: ['ml-anomaly-scores-v2'],
    queryFn: () => apiClient.get('/ml/anomaly-scores?hours=24').then(res => res.data),
    refetchInterval: 60000,
  });

  const scores: AnomalyWindow[] = scoresResponse?.anomaly_scores || [];
  
  // Format data for chart
  const chartData = scores.map(item => {
    const date = new Date(item.timestamp);
    return {
      time: `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`,
      avg: item.average_score,
      max: item.max_score,
      raw: item
    };
  });

  if (isLoading) {
    return (
      <div className="bg-background border border-border rounded-xl p-6 shadow-sm min-h-[400px] flex items-center justify-center">
        <div className="text-muted animate-pulse">Loading anomaly trend data...</div>
      </div>
    );
  }

  return (
    <div className="bg-background border border-border rounded-xl p-6 shadow-sm min-h-[400px] flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-medium text-foreground">Anomaly Score Trend (24h)</h3>
        </div>
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-purple-500"></div> Avg Score</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div> Max Score</div>
        </div>
      </div>
      
      {scores.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-muted">
          <BrainCircuit className="w-12 h-12 mb-3 opacity-20" />
          <p>No anomalies detected recently</p>
        </div>
      ) : (
        <div className="flex-1 min-h-0">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis 
                dataKey="time" 
                stroke="#64748b" 
                fontSize={12}
                tickLine={false}
                axisLine={false}
                minTickGap={30}
              />
              <YAxis 
                stroke="#64748b" 
                fontSize={12}
                tickLine={false}
                axisLine={false}
                domain={[0, 1]}
                ticks={[0, 0.25, 0.5, 0.75, 1]}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#0f172a', 
                  border: '1px solid #1e293b',
                  borderRadius: '0.5rem',
                  color: '#f8fafc'
                }}
                labelStyle={{ color: '#94a3b8', marginBottom: '0.25rem' }}
                itemStyle={{ color: '#818cf8' }}
                formatter={(value: any, name: any) => {
                  return [`${value}`, name === 'avg' ? 'Average Score' : 'Max Score'];
                }}
                labelFormatter={(label, payload) => {
                  if (payload && payload.length > 0) {
                    const item = payload[0].payload.raw;
                    return `${label} (${item.anomaly_count} anomalies)`;
                  }
                  return label;
                }}
              />
              <ReferenceLine y={0.7} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Threat Threshold', fill: '#ef4444', fontSize: 10 }} />
              
              <Line 
                type="monotone" 
                dataKey="avg" 
                stroke="#a855f7" 
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: '#a855f7' }}
                isAnimationActive={false}
              />
              
              <Line 
                type="monotone" 
                dataKey="max" 
                stroke="#ef4444" 
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                activeDot={{ r: 4, fill: '#ef4444' }}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
