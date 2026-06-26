import { render, screen } from '@testing-library/react';
import { Alerts } from './Alerts';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({ data: { status: 'success', data: [
      { timestamp: '2026-06-26T12:00:00Z', severity: 'HIGH', alert_type: 'scan', src_ip: '1.1.1.1', dst_ip: '2.2.2.2', description: 'test', action_taken: 'block' }
    ] } })
  }
}));

describe('Alerts Page', () => {
  it('renders alerts table', async () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <Alerts />
      </QueryClientProvider>
    );
    expect(await screen.findByText('Security Alerts')).toBeInTheDocument();
    expect(await screen.findByText('1.1.1.1')).toBeInTheDocument();
  });
});
