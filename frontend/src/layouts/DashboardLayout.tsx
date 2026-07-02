import { Outlet, NavLink } from 'react-router-dom';
import { useUIStore } from '../store/uiStore';

import { ShieldCheck, Activity, AlertTriangle, Network, Settings, BarChart2, BookOpen, Menu } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

const NAVIGATION = [
  { name: 'Dashboard', to: '/', icon: BarChart2 },
  { name: 'Active Connections', to: '/connections', icon: Network },
  { name: 'Alerts & Incidents', to: '/alerts', icon: AlertTriangle },
  { name: 'Analytics', to: '/analytics', icon: Activity },
  { name: 'Firewall Rules', to: '/rules', icon: ShieldCheck },
  { name: 'Documentation', to: '/docs', icon: BookOpen },
  { name: 'Settings', to: '/settings', icon: Settings },
];

export function DashboardLayout() {
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const { isConnected } = useWebSocket(); // Initialize global WS connection

  return (
    <div className="flex h-screen overflow-hidden bg-background font-sans">
      {/* Sidebar */}
      <aside 
        className={`${sidebarOpen ? 'w-64' : 'w-20'} 
        transition-all duration-300 ease-in-out border-r border-border bg-background backdrop-blur-xl flex flex-col`}
      >
        <div className="h-16 flex items-center justify-center border-b border-primary/30">
          <ShieldCheck className="w-8 h-8 text-primary drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]" />
          {sidebarOpen && <span className="ml-3 font-bold text-lg tracking-wider text-primary neon-text">HUD_SYS</span>}
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-2 px-3">
            {NAVIGATION.map((item) => (
              <li key={item.name}>
                <NavLink
                  to={item.to}
                  className={({ isActive }) => 
                    `flex items-center px-3 py-2 transition-all duration-300 ${
                      isActive 
                        ? 'text-primary border-l-2 border-primary bg-primary/10 shadow-[inset_4px_0_10px_rgba(0,240,255,0.1)]' 
                        : 'text-muted hover:text-primary hover:bg-panel-hover'
                    }`
                  }
                  title={!sidebarOpen ? item.name : undefined}
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  {sidebarOpen && <span className="ml-3">{item.name}</span>}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative z-10">
        <header className="h-16 border-b border-primary/30 bg-background/80 backdrop-blur-md flex items-center justify-between px-4 lg:px-8 z-10">
          <div className="flex items-center">
            <button onClick={toggleSidebar} className="lg:hidden p-2 mr-3 text-primary hover:text-foreground">
              <Menu className="w-6 h-6" />
            </button>
            <h2 className="text-sm font-medium text-muted uppercase tracking-widest hidden sm:block">
              SYS.OP_MODE: <span className="text-primary font-bold neon-text">TACTICAL</span>
            </h2>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
                <span className="text-sm text-muted">System Status:</span>
                <span className="relative flex h-3 w-3">
                  {isConnected && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>}
                  <span className={`relative inline-flex rounded-full h-3 w-3 ${isConnected ? 'bg-success' : 'bg-danger'}`}></span>
                </span>
                <span className="text-sm font-medium text-foreground">
                  {isConnected ? 'Online' : 'Disconnected'}
                </span>
             </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 transition-colors duration-300">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
