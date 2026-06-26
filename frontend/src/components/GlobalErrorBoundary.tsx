import { ErrorBoundary } from 'react-error-boundary';
import { ServerCrash } from 'lucide-react';

function ErrorFallback({ error, resetErrorBoundary }: any) {
  return (
    <div className="h-screen w-full flex flex-col items-center justify-center bg-background text-slate-200">
      <div className="glass-panel p-8 max-w-md w-full flex flex-col items-center text-center shadow-2xl shadow-danger/20">
        <div className="p-4 bg-danger/10 rounded-full mb-4">
          <ServerCrash className="w-10 h-10 text-danger" />
        </div>
        <h2 className="text-xl font-bold mb-2 tracking-tight text-slate-100">System Dashboard Error</h2>
        <div className="text-sm text-slate-400 mb-6 bg-slate-900/50 p-4 rounded-md overflow-x-auto w-full text-left font-mono border border-slate-700/50">
          {error.message}
        </div>
        <button 
          onClick={resetErrorBoundary}
          className="px-6 py-2 bg-primary/20 border border-primary/50 hover:bg-primary/30 text-primary font-medium tracking-wide rounded-md transition-all w-full"
        >
          Reboot Dashboard
        </button>
      </div>
    </div>
  );
}

export function GlobalErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      {children}
    </ErrorBoundary>
  );
}
