import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { DashboardLayout } from './layouts/DashboardLayout';

import { Dashboard } from './pages/Dashboard';
import { Connections } from './pages/Connections';
import { Alerts } from './pages/Alerts';
import { Analytics } from './pages/Analytics';

// Mock empty pages for now
const Rules = () => <div className="text-2xl font-bold">Rules (WIP)</div>;
const Settings = () => <div className="text-2xl font-bold">Settings (WIP)</div>;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/connections" element={<Connections />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster 
        position="top-right" 
        toastOptions={{ 
          className: 'bg-slate-800 text-slate-100 border border-slate-700',
          style: { background: '#1E293B', color: '#F1F5F9', borderColor: '#334155' }
        }} 
      />
    </QueryClientProvider>
  );
}

export default App;
