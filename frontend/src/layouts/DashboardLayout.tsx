import { Outlet, NavLink } from 'react-router-dom';
import { useUIStore } from '../store/uiStore';
import { Shield, LayoutDashboard, Activity, AlertTriangle, Network, ShieldAlert, Settings, Menu } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

const NAVIGATION = [
  { name: 'Dashboard', to: '/', icon: LayoutDashboard },
  { name: 'Active Connections', to: '/connections', icon: Network },
  { name: 'Alerts & Incidents', to: '/alerts', icon: AlertTriangle },
  { name: 'Analytics', to: '/analytics', icon: Activity },
  { name: 'Firewall Rules', to: '/rules', icon: ShieldAlert },
  { name: 'Settings', to: '/settings', icon: Settings },
];

export function DashboardLayout() {
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const { isConnected } = useWebSocket(); // Initialize global WS connection

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar */}
      <aside 
        className={`${sidebarOpen ? 'w-64' : 'w-20'} 
        transition-all duration-300 ease-in-out border-r border-slate-700/50 bg-slate-900/50 backdrop-blur-xl flex flex-col`}
      >
        <div className="h-16 flex items-center justify-center border-b border-slate-700/50">
          <Shield className="w-8 h-8 text-primary" />
          {sidebarOpen && <span className="ml-3 font-bold text-lg tracking-wider text-slate-100">AI-NGFW</span>}
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-2 px-3">
            {NAVIGATION.map((item) => (
              <li key={item.name}>
                <NavLink
                  to={item.to}
                  className={({ isActive }) => 
                    `flex items-center px-3 py-2 rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-primary/20 text-primary border border-primary/30' 
                        : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
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
        <header className="h-16 flex items-center justify-between px-6 border-b border-slate-700/50 bg-slate-900/30 backdrop-blur-sm">
          <div className="flex items-center">
            <button 
              onClick={toggleSidebar}
              className="p-2 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex items-center space-x-4">
             <div className="flex items-center space-x-2">
                <span className="text-sm text-slate-400">System Status:</span>
                <span className="relative flex h-3 w-3">
                  {isConnected && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>}
                  <span className={`relative inline-flex rounded-full h-3 w-3 ${isConnected ? 'bg-success' : 'bg-danger'}`}></span>
                </span>
                <span className="text-sm font-medium text-slate-300">
                  {isConnected ? 'Online' : 'Disconnected'}
                </span>
             </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
