import { render, screen } from '@testing-library/react';
import { Analytics } from './Analytics';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({ data: { status: 'success', data: [
      { ip: '1.1.1.1', bytes: 1024, incidents: 5 }
    ] } })
  }
}));

describe('Analytics Page', () => {
  it('renders analytics charts', async () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <Analytics />
      </QueryClientProvider>
    );
    expect(await screen.findByText('Analytics & Intelligence')).toBeInTheDocument();
  });
});
