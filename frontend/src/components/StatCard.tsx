import React from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: string;
  trendUp?: boolean;
  isLoading?: boolean;
}

export function StatCard({ label, value, icon, trend, trendUp, isLoading }: StatCardProps) {
  if (isLoading) {
    return (
      <div className="bg-panel border border-border rounded-xl p-6 shadow-sm animate-pulse flex flex-col justify-between h-[120px]">
        <div className="flex justify-between items-start">
          <div className="h-4 bg-panel-hover rounded w-1/3"></div>
          <div className="h-8 w-8 bg-panel-hover rounded-lg"></div>
        </div>
        <div className="h-8 bg-panel-hover rounded w-1/2 mt-4"></div>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 flex flex-col relative overflow-hidden group hover:scale-[1.02] transition-transform duration-300">
      <div className="flex justify-between items-start mb-4 relative z-10">
        <h3 className="text-muted font-medium text-sm tracking-wider uppercase">{label}</h3>
        {icon && <div className="text-primary/70 group-hover:text-primary transition-colors">{icon}</div>}
      </div>
      <div className="flex items-baseline space-x-2 relative z-10">
        <span className="text-3xl font-bold text-foreground">{value}</span>
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
