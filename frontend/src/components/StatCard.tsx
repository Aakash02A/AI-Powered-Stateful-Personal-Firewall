import React from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: string;
  trendUp?: boolean;
}

export function StatCard({ label, value, icon, trend, trendUp }: StatCardProps) {
  return (
    <div className="glass-panel p-6 flex flex-col relative overflow-hidden group">
      <div className="flex justify-between items-start mb-4 relative z-10">
        <h3 className="text-slate-400 font-medium text-sm tracking-wider uppercase">{label}</h3>
        {icon && <div className="text-primary/70 group-hover:text-primary transition-colors">{icon}</div>}
      </div>
      <div className="flex items-baseline space-x-2 relative z-10">
        <span className="text-3xl font-bold text-slate-100">{value}</span>
        {trend && (
          <span className={`text-sm font-medium ${trendUp ? 'text-success' : 'text-danger'}`}>
            {trend}
          </span>
        )}
      </div>
      {/* Background glow effect */}
      <div className="absolute -bottom-8 -right-8 w-32 h-32 bg-primary/5 rounded-full blur-2xl group-hover:bg-primary/10 transition-colors" />
    </div>
  );
}
