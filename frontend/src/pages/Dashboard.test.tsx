import { render, screen } from '@testing-library/react';
import { Dashboard } from './Dashboard';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: () => ({ isConnected: true, lastMessage: null })
}));

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({ data: { status: 'success', data: { total_packets: 100, total_alerts: 5, active_connections: 10 } } })
  }
}));

describe('Dashboard', () => {
  it('renders dashboard components', () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <Dashboard />
      </QueryClientProvider>
    );
    expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Total Packets')).toBeInTheDocument();
    expect(screen.getByText('Total Alerts')).toBeInTheDocument();
  });
});
