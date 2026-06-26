import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Modal } from './Modal';
import { apiClient } from '../api/client';
import { ShieldAlert, Info, AlertTriangle, AlertOctagon } from 'lucide-react';
import { format } from 'date-fns';

interface NotificationHistoryProps {
  isOpen: boolean;
  onClose: () => void;
}

export function NotificationHistory({ isOpen, onClose }: NotificationHistoryProps) {
  const [limit, setLimit] = useState(50);

  const { data: response, isLoading } = useQuery({
    queryKey: ['alerts-history', limit],
    queryFn: () => apiClient.get(`/alerts?limit=${limit}`).then(res => res.data),
    enabled: isOpen, // Only fetch when modal is open
  });

  const alerts = response?.data || [];

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return <AlertOctagon className="w-5 h-5 text-danger" />;
      case 'HIGH': return <AlertTriangle className="w-5 h-5 text-warning" />;
      case 'MEDIUM': return <ShieldAlert className="w-5 h-5 text-secondary" />;
      default: return <Info className="w-5 h-5 text-primary" />;
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Notification History" maxWidth="max-w-2xl">
      <div className="flex flex-col h-[60vh]">
        <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
          {isLoading ? (
            <div className="flex justify-center items-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : alerts.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <ShieldAlert className="w-12 h-12 mb-2 opacity-20" />
              <p>No historical alerts found</p>
            </div>
          ) : (
            alerts.map((alert: any) => (
              <div key={alert.id} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50 hover:border-slate-600 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="mt-1">{getSeverityIcon(alert.severity)}</div>
                    <div>
                      <h4 className="text-slate-200 font-medium">{alert.alert_type?.replace(/_/g, ' ')}</h4>
                      <p className="text-sm text-slate-400 mt-1">{alert.description}</p>
                      <div className="flex items-center space-x-3 mt-2 text-xs font-mono text-slate-500">
                        <span>{alert.src_ip}</span>
                        <span>→</span>
                        <span>{alert.dst_ip}</span>
                      </div>
                    </div>
                  </div>
                  <span className="text-xs text-slate-500 whitespace-nowrap">
                    {format(new Date(alert.timestamp), 'MMM d, HH:mm:ss')}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
        {alerts.length >= limit && (
          <div className="pt-4 mt-2 border-t border-slate-700/50 text-center">
            <button 
              onClick={() => setLimit(l => l + 50)}
              className="text-sm text-primary hover:text-primary/80 transition-colors"
            >
              Load more...
            </button>
          </div>
        )}
      </div>
    </Modal>
  );
}
