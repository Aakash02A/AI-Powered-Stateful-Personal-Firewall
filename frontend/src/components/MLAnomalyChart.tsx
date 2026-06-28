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

interface AnomalyScore {
  timestamp: string;
  score: number;
  src_ip: string;
  dst_ip: string;
}

export function MLAnomalyChart() {
  const { data: scoresResponse, isLoading } = useQuery({
    queryKey: ['ml-anomaly-scores'],
    queryFn: () => apiClient.get('/ml/anomaly-scores').then(res => res.data),
    refetchInterval: 10000,
  });

  const scores: AnomalyScore[] = scoresResponse?.data || [];
  
  // Format data for chart
  const chartData = scores.map(item => {
    const date = new Date(item.timestamp);
    return {
      time: `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`,
      score: Number(item.score.toFixed(3)),
      raw: item
    };
  });

  if (isLoading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm h-80 flex items-center justify-center">
        <div className="text-slate-500 animate-pulse">Loading anomaly data...</div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm h-full flex flex-col">
      <div className="flex items-center gap-2 mb-6">
        <BrainCircuit className="w-5 h-5 text-indigo-400" />
        <h3 className="text-lg font-medium text-slate-100">ML Anomaly Scores</h3>
      </div>
      
      {scores.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
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
                formatter={(value: any) => {
                  return [`${value}`, `Anomaly Score`];
                }}
                labelFormatter={(label, payload) => {
                  if (payload && payload.length > 0) {
                    const item = payload[0].payload.raw;
                    return `${label} (${item.src_ip} → ${item.dst_ip})`;
                  }
                  return label;
                }}
              />
              <ReferenceLine y={0.7} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Threat Threshold', fill: '#ef4444', fontSize: 10 }} />
              <Line 
                type="monotone" 
                dataKey="score" 
                stroke="#818cf8" 
                strokeWidth={2}
                dot={{ r: 3, fill: '#312e81', stroke: '#818cf8', strokeWidth: 1 }}
                activeDot={{ r: 5, fill: '#818cf8', stroke: '#c7d2fe' }}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
