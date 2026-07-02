import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

import { EmptyState, LoadingSkeleton } from './UIStates';

interface ProtocolChartProps {
  data: Record<string, number>;
  isLoading?: boolean;
}

const COLORS = ['var(--color-primary)', 'var(--color-secondary)', 'var(--color-success)', 'var(--color-warning)', 'var(--color-danger)', '#A78BFA'];

export function ProtocolChart({ data, isLoading }: ProtocolChartProps) {
  if (isLoading) {
    return <LoadingSkeleton type="chart" />;
  }

  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="fui-panel p-6 h-80 flex flex-col relative">
        <h3 className="text-primary font-bold text-sm tracking-widest uppercase mb-4 border-b border-primary/30 pb-2">Protocol Distribution</h3>
        <EmptyState title="No Protocol Data" description="No traffic has been recorded yet." />
      </div>
    );
  }

  // Convert Record<string, number> to array format for Recharts
  const chartData = Object.entries(data)
    .map(([name, value]) => ({ name: name.toUpperCase(), value }))
    .sort((a, b) => b.value - a.value);

  return (
    <div className="fui-panel p-6 h-80 flex flex-col relative">
      <h3 className="text-primary font-bold text-sm tracking-widest uppercase mb-4 border-b border-primary/30 pb-2">Protocol Distribution</h3>
      <div className="flex-1 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={5}
              dataKey="value"
              stroke="none"
            >
              {chartData.map((_entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--bg-panel)', border: '1px solid var(--color-primary)', borderRadius: '0', color: 'var(--text-foreground)', boxShadow: '0 0 10px rgba(0, 240, 255, 0.2)' }}
              itemStyle={{ color: 'var(--color-primary)', fontFamily: 'monospace' }}
            />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
