import { render, screen } from '@testing-library/react';
import { ConnectionStatus } from './ConnectionStatus';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock useWebSocket
vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    isConnected: true,
    lastMessageTime: new Date().toISOString()
  })
}));

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe('ConnectionStatus', () => {
  it('renders online statuses when connected', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ConnectionStatus />
      </QueryClientProvider>
    );
    
    expect(screen.getByText('REST API:')).toBeInTheDocument();
    expect(screen.getByText('Live Feed:')).toBeInTheDocument();
    
    // It should say Connected for live feed
    expect(screen.getByText('Connected')).toBeInTheDocument();
    
    // Since we mock API in handlers.ts as healthy, it should say Online
    expect(await screen.findByText('Online')).toBeInTheDocument();
  });
});
