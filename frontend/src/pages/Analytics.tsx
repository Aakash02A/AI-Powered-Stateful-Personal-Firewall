import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { apiClient } from '../api/client';

export function Analytics() {
  const { data: topTalkersRes } = useQuery({
    queryKey: ['top-talkers'],
    queryFn: () => apiClient.get('/top-talkers').then(res => res.data),
    refetchInterval: 15000,
  });

  const { data: topAttackersRes } = useQuery({
    queryKey: ['top-attackers'],
    queryFn: () => apiClient.get('/top-attackers').then(res => res.data),
    refetchInterval: 15000,
  });

  const topTalkers = topTalkersRes?.data || [];
  const topAttackers = topAttackersRes?.data || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Analytics & Intelligence</h1>
          <p className="text-sm text-slate-400 mt-1">Deep dive into network traffic origins and threat sources.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Talkers */}
        <div className="glass-panel p-6 h-[450px] flex flex-col">
          <h3 className="text-slate-400 font-medium text-sm tracking-wider uppercase mb-6">Top Talkers (By Volume)</h3>
          {topTalkers.length === 0 ? (
            <div className="flex-1 flex items-center justify-center text-slate-500">No talker data available</div>
          ) : (
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topTalkers} layout="vertical" margin={{ top: 0, right: 0, left: 40, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={true} vertical={false} />
                  <XAxis type="number" stroke="#94A3B8" fontSize={12} tickFormatter={(val) => `${(val / 1024 / 1024).toFixed(1)}MB`} />
                  <YAxis dataKey="ip" type="category" stroke="#94A3B8" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '0.5rem', color: '#F1F5F9' }}
                    cursor={{ fill: '#334155', opacity: 0.4 }}
                    formatter={(val: any) => [`${(val / 1024 / 1024).toFixed(2)} MB`, 'Volume']}
                  />
                  <Bar dataKey="bytes" fill="#38BDF8" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Top Attackers */}
        <div className="glass-panel p-6 h-[450px] flex flex-col">
          <h3 className="text-slate-400 font-medium text-sm tracking-wider uppercase mb-6 text-danger">Top Attackers (By Incidents)</h3>
          {topAttackers.length === 0 ? (
            <div className="flex-1 flex items-center justify-center text-slate-500">No attacker data available</div>
          ) : (
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topAttackers} layout="vertical" margin={{ top: 0, right: 0, left: 40, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={true} vertical={false} />
                  <XAxis type="number" stroke="#94A3B8" fontSize={12} />
                  <YAxis dataKey="ip" type="category" stroke="#94A3B8" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '0.5rem', color: '#F1F5F9' }}
                    cursor={{ fill: '#334155', opacity: 0.4 }}
                    formatter={(val: any) => [val, 'Incidents']}
                  />
                  <Bar dataKey="incidents" fill="#F87171" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
