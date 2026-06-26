import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { lazy, Suspense, useEffect } from 'react';
import { DashboardLayout } from './layouts/DashboardLayout';
import { GlobalErrorBoundary } from './components/GlobalErrorBoundary';
import { LoadingSpinner } from './components/LoadingSpinner';
import { useThemeStore } from './store/themeStore';

const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const Connections = lazy(() => import('./pages/Connections').then(m => ({ default: m.Connections })));
const Alerts = lazy(() => import('./pages/Alerts').then(m => ({ default: m.Alerts })));
const Analytics = lazy(() => import('./pages/Analytics').then(m => ({ default: m.Analytics })));

// Mock empty pages for now
const Rules = () => <div className="text-2xl font-bold p-6">Rules (WIP)</div>;
const Settings = () => <div className="text-2xl font-bold p-6">Settings (WIP)</div>;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const { isDark } = useThemeStore();

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.add('light');
    }
  }, [isDark]);

  return (
    <GlobalErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Suspense fallback={<LoadingSpinner />}>
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
          </Suspense>
        </BrowserRouter>
        <Toaster 
          position="top-right" 
          toastOptions={{ 
            className: 'bg-slate-800 text-slate-100 border border-slate-700',
            style: { background: '#1E293B', color: '#F1F5F9', borderColor: '#334155' }
          }} 
        />
      </QueryClientProvider>
    </GlobalErrorBoundary>
  );
}

export default App;
