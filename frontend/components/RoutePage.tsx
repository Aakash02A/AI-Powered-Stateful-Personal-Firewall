import type { ReactNode } from "react";

type RoutePageProps = {
  title: string;
  description: string;
  children?: ReactNode;
};

export default function RoutePage({ title, description, children }: RoutePageProps) {
  return (
    <div className="space-y-6 animate-fade-in-up">
      <div>
        <h1 className="text-xl font-bold text-white">{title}</h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-0.5">{description}</p>
      </div>

      <div className="glass-card p-6 space-y-4">
        <div className="text-sm text-[var(--color-text-secondary)]">
          This section is wired into the dashboard shell and ready for live data.
        </div>
        {children}
      </div>
    </div>
  );
}