import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Activity, ShieldAlert, Network, ServerCrash } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { ProtocolChart } from '../components/ProtocolChart';
import { AlertFeed, type AlertData } from '../components/AlertFeed';
import { apiClient } from '../api/client';
import { useWebSocket } from '../hooks/useWebSocket';
import { ConnectionStatus } from '../components/ConnectionStatus';
import { NotificationHistory } from '../components/NotificationHistory';
import { MLStatusCard } from '../components/MLStatusCard';
import { MLAnomalyChart } from '../components/MLAnomalyChart';
import { MLMetricsWidget } from '../components/MLMetricsWidget';
import { MLAlertsFeed } from '../components/MLAlertsFeed';


export function Dashboard() {
  const [liveAlerts, setLiveAlerts] = useState<AlertData[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  
  // Connect to WebSocket stream
  const { lastMessage } = useWebSocket();
  
  // Fetch initial stats
  const { data: statsResponse, isLoading: isLoadingStats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => apiClient.get('/stats').then(res => res.data),
    refetchInterval: 5000, // Refresh every 5 seconds as fallback
  });

  const { data: protocolsResponse, isLoading: isLoadingProtocols } = useQuery({
    queryKey: ['protocols'],
    queryFn: () => apiClient.get('/protocols').then(res => res.data),
    refetchInterval: 10000,
  });

  // Handle live WebSocket alerts
  useEffect(() => {
    if (lastMessage && lastMessage.topic === 'alert') {
      setLiveAlerts(prev => {
        // Keep only the 50 most recent alerts in memory for the live feed
        const newAlerts = [lastMessage.data, ...prev].slice(0, 50);
        return newAlerts;
      });
    }
  }, [lastMessage]);

  const stats = statsResponse?.data || {};
  const protocols = protocolsResponse?.data || {};

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-foreground tracking-tight">Security Dashboard</h1>
          <p className="text-sm text-muted mt-1">Real-time overview of network health and active threats.</p>
        </div>
        <div className="hidden sm:block">
          <ConnectionStatus />
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          label="Total Packets" 
          value={(stats.total_packets || 0).toLocaleString()} 
          icon={<Activity />} 
          isLoading={isLoadingStats}
        />
        <StatCard 
          label="Active Connections" 
          value={(stats.active_connections || 0).toLocaleString()} 
          icon={<Network />} 
          isLoading={isLoadingStats}
        />
        <StatCard 
          label="Total Alerts" 
          value={(stats.total_alerts || 0).toLocaleString()} 
          icon={<ShieldAlert />} 
          trend={stats.total_alerts > 0 ? "Threats detected" : "All clear"}
          trendUp={stats.total_alerts === 0}
          isLoading={isLoadingStats}
        />
        <StatCard 
          label="Blocked IPs" 
          value={(stats.blocked_ips || 0).toLocaleString()} 
          icon={<ServerCrash />} 
          isLoading={isLoadingStats}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Charts */}
        <div className="lg:col-span-2 space-y-6">
          <ProtocolChart data={protocols} isLoading={isLoadingProtocols} />
        </div>
        
        {/* Right Column - Live Feed */}
        <div className="lg:col-span-1">
          <AlertFeed 
            alerts={liveAlerts} 
            onViewHistory={() => setIsHistoryOpen(true)} 
          />
        </div>
      </div>

      <div className="pt-6 pb-2">
        <div className="border-t border-border"></div>
      </div>

      <div>
        <h2 className="text-xl font-bold text-foreground tracking-tight mb-6">Machine Learning Analysis</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 flex flex-col gap-6 h-full">
            <MLStatusCard />
            <div className="flex-1 min-h-[300px]">
              <MLAlertsFeed />
            </div>
          </div>
          
          <div className="lg:col-span-2 flex flex-col gap-6">
            <MLMetricsWidget />
            <div className="flex-1">
              <MLAnomalyChart />
            </div>
          </div>
        </div>
      </div>
      
      <NotificationHistory 
        isOpen={isHistoryOpen} 
        onClose={() => setIsHistoryOpen(false)} 
      />
    </div>
  );
}
