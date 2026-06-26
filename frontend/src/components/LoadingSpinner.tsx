import { Shield } from 'lucide-react';

export function LoadingSpinner() {
  return (
    <div className="flex h-screen items-center justify-center bg-background" data-testid="loading-spinner">
      <div className="relative">
        <Shield className="w-12 h-12 text-primary opacity-20" />
        <div className="absolute inset-0 border-t-2 border-primary rounded-full animate-spin"></div>
      </div>
      <p className="mt-4 text-xs text-slate-500 font-medium tracking-widest uppercase animate-pulse">
        Initializing Security Modules...
      </p>
    </div>
  );
}
