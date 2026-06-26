import { render, screen } from '@testing-library/react';
import { Connections } from './Connections';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({ data: { status: 'success', data: [
      { creation_time: '2026-06-26T12:00:00Z', src_ip: '1.1.1.1', src_port: 80, dst_ip: '2.2.2.2', dst_port: 443, protocol: 'TCP', state: 'ESTABLISHED', duration: 10, bytes_in: 500, bytes_out: 500 }
    ] } })
  }
}));

describe('Connections Page', () => {
  it('renders connections table', async () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <Connections />
      </QueryClientProvider>
    );
    expect(await screen.findByText('Active Connections')).toBeInTheDocument();
    expect(await screen.findByText('1.1.1.1:80')).toBeInTheDocument();
  });
});
