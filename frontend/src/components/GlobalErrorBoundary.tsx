import { ErrorBoundary } from 'react-error-boundary';
import { ServerCrash } from 'lucide-react';

function ErrorFallback({ error, resetErrorBoundary }: any) {
  return (
    <div className="h-screen w-full flex flex-col items-center justify-center bg-background text-foreground">
      <div className="glass-panel p-8 max-w-md w-full flex flex-col items-center text-center shadow-2xl shadow-danger/20">
        <div className="p-4 bg-danger/10 rounded-full mb-4">
          <ServerCrash className="w-10 h-10 text-danger" />
        </div>
        <h2 className="text-xl font-bold mb-2 tracking-tight text-foreground">System Dashboard Error</h2>
        <div className="text-sm text-muted mb-6 bg-background p-4 rounded-md overflow-x-auto w-full text-left font-mono border border-border">
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
