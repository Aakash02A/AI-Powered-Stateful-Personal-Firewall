import React from 'react';
import { AlertCircle, type LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon: Icon = AlertCircle, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[200px] p-6 text-center">
      <div className="w-12 h-12 rounded-full bg-panel flex items-center justify-center mb-4 text-muted">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-lg font-medium text-foreground">{title}</h3>
      <p className="text-sm text-muted mt-2 max-w-sm">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}

export function LoadingSkeleton({ lines = 3, type = 'list' }: { lines?: number; type?: 'list' | 'card' | 'chart' }) {
  if (type === 'card') {
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

  if (type === 'chart') {
    return (
      <div className="bg-panel border border-border rounded-xl p-6 shadow-sm animate-pulse h-full min-h-[300px] flex flex-col">
        <div className="h-6 bg-panel-hover rounded w-1/4 mb-6"></div>
        <div className="flex-1 flex items-end space-x-2">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="flex-1 bg-panel-hover rounded-t" style={{ height: `${Math.max(20, Math.random() * 100)}%` }}></div>
          ))}
        </div>
      </div>
    );
  }

  // list
  return (
    <div className="space-y-4 w-full">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="animate-pulse flex gap-4 bg-panel p-4 rounded-lg border border-border">
          <div className="w-10 h-10 bg-panel-hover rounded-full shrink-0"></div>
          <div className="flex-1 space-y-2 py-1">
            <div className="h-4 bg-panel-hover rounded w-3/4"></div>
            <div className="h-3 bg-panel-hover rounded w-1/2"></div>
          </div>
        </div>
      ))}
    </div>
  );
}
