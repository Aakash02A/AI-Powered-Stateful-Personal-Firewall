import { ShieldAlert, AlertTriangle, Info, ShieldCheck } from 'lucide-react';
import { format } from 'date-fns';
import { EmptyState } from './UIStates';

export interface AlertData {
  id?: number;
  timestamp: string;
  alert_type: string;
  severity: string;
  src_ip: string;
  dst_ip: string;
  description: string;
  action_taken: string;
}

interface AlertFeedProps {
  alerts: AlertData[];
  onViewHistory?: () => void;
}

const SEVERITY_CONFIG = {
  CRITICAL: { icon: ShieldAlert, color: 'text-danger', bg: 'bg-danger/10 border-danger/20' },
  HIGH: { icon: AlertTriangle, color: 'text-warning', bg: 'bg-warning/10 border-warning/20' },
  MEDIUM: { icon: Info, color: 'text-primary', bg: 'bg-primary/10 border-primary/20' },
  LOW: { icon: ShieldCheck, color: 'text-success', bg: 'bg-success/10 border-success/20' },
};

export function AlertFeed({ alerts, onViewHistory }: AlertFeedProps) {
  return (
    <div className="glass-panel flex flex-col h-[400px]">
      <div className="p-6 border-b border-border flex justify-between items-center">
        <div className="flex flex-col">
          <h3 className="text-muted font-medium text-sm tracking-wider uppercase">Live Threat Feed</h3>
          <span className="flex items-center text-xs text-muted mt-1">
            <span className="relative flex h-2 w-2 mr-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            Live Monitoring
          </span>
        </div>
        {onViewHistory && (
          <button 
            onClick={onViewHistory}
            className="text-xs bg-panel hover:bg-panel-hover border border-border text-foreground px-3 py-1.5 rounded transition-colors"
          >
            History
          </button>
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {alerts.length === 0 ? (
          <EmptyState 
            icon={ShieldCheck} 
            title="All Clear" 
            description="No active threats detected in this session." 
          />
        ) : (
          alerts.map((alert, index) => {
            const config = SEVERITY_CONFIG[alert.severity as keyof typeof SEVERITY_CONFIG] || SEVERITY_CONFIG.LOW;
            const Icon = config.icon;
            
            return (
              <div 
                key={alert.id || `live-${index}`} 
                className={`flex items-start p-3 rounded-lg border ${config.bg} animate-in slide-in-from-top-2 fade-in duration-300`}
              >
                <div className={`${config.color} mt-0.5 mr-3 flex-shrink-0`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start mb-1">
                    <p className="text-sm font-medium text-foreground truncate">{alert.alert_type.replace(/_/g, ' ').toUpperCase()}</p>
                    <span className="text-xs text-muted whitespace-nowrap ml-2">
                      {format(new Date(alert.timestamp), 'HH:mm:ss')}
                    </span>
                  </div>
                  <p className="text-xs text-muted truncate mb-1">
                    {alert.src_ip} <span className="mx-1 text-slate-600">→</span> {alert.dst_ip}
                  </p>
                  <div className="flex justify-between items-center">
                    <p className="text-xs text-foreground truncate pr-2">{alert.description}</p>
                    <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-panel text-foreground border border-border">
                      {alert.action_taken}
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
