import { useQuery } from '@tanstack/react-query';
import { useWebSocket } from '../hooks/useWebSocket';
import { Activity, Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { apiClient } from '../api/client';

export function ConnectionStatus() {
  const { isConnected: isWsConnected, lastMessageTime } = useWebSocket();
  
  const { data: healthData, isError: isRestError } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.get('/health/ready').then(res => res.data),
    refetchInterval: 10000,
    retry: 3,
  });

  const isRestConnected = !isRestError && healthData?.status === 'ready';

  return (
    <div className="flex items-center space-x-6 text-sm">
      <div className="flex items-center space-x-2">
        <span className="text-muted">REST API:</span>
        {isRestConnected ? (
          <span className="flex items-center text-success bg-success/10 px-2 py-0.5 rounded-full font-medium">
            <Wifi className="w-3.5 h-3.5 mr-1" /> Online
          </span>
        ) : (
          <span className="flex items-center text-danger bg-danger/10 px-2 py-0.5 rounded-full font-medium">
            <WifiOff className="w-3.5 h-3.5 mr-1" /> Offline
          </span>
        )}
      </div>

      <div className="flex items-center space-x-2">
        <span className="text-muted">Live Feed:</span>
        {isWsConnected ? (
          <span className="flex items-center text-primary bg-primary/10 px-2 py-0.5 rounded-full font-medium" title={lastMessageTime ? `Last message at ${new Date(lastMessageTime).toLocaleTimeString()}` : 'Connected'}>
            <Activity className="w-3.5 h-3.5 mr-1 animate-pulse" /> Connected
          </span>
        ) : (
          <span className="flex items-center text-warning bg-warning/10 px-2 py-0.5 rounded-full font-medium">
            <AlertCircle className="w-3.5 h-3.5 mr-1" /> Reconnecting...
          </span>
        )}
      </div>
    </div>
  );
}
