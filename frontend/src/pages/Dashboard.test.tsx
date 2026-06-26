import { render, screen, waitFor, act } from '@testing-library/react';
import React from 'react';
import { Dashboard } from './Dashboard';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useWebSocket } from '../hooks/useWebSocket';

vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({ isConnected: true, lastMessage: null, lastMessageTime: null }))
}));

// We mock Recharts to prevent ResizeObserver errors and speed up tests
vi.mock('recharts', async (importOriginal) => {
  const actual = await importOriginal<typeof import('recharts')>();
  return {
    ...actual,
    ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  };
});

describe('Dashboard Integration', () => {
  const createTestQueryClient = () => new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  it('loads and displays stats on mount', async () => {
    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <Dashboard />
      </QueryClientProvider>
    );

    expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    
    // Wait for the data fetch (from MSW) to complete
    await waitFor(() => {
      // 1234 is from our MSW handler for total_packets, rendered as 1,234
      expect(screen.getByText('1,234')).toBeInTheDocument(); 
      // 8 is blocked connections
      expect(screen.getByText('8')).toBeInTheDocument();
    });
  });

  it('updates dashboard on WebSocket alert', async () => {
    let mockSetMessage: (msg: any) => void;
    
    let currentMessage: any = null;
    let messageListeners: any[] = [];
    
    mockSetMessage = (msg: any) => {
      currentMessage = msg;
      messageListeners.forEach(listener => listener(msg));
    };
    
    vi.mocked(useWebSocket).mockImplementation(() => {
      const [lastMessage, setLastMessage] = React.useState(currentMessage);
      const [lastMessageTime] = React.useState(currentMessage ? new Date().toISOString() : null);
      
      React.useEffect(() => {
        messageListeners.push(setLastMessage);
        return () => {
          messageListeners = messageListeners.filter((l: any) => l !== setLastMessage);
        };
      }, []);
      
      return { isConnected: true, lastMessage, lastMessageTime };
    });

    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <Dashboard />
      </QueryClientProvider>
    );

    // Initial MSW state
    await waitFor(() => {
      expect(screen.getByText('1,234')).toBeInTheDocument();
    });

    // Simulate WS message by updating the hook state
    act(() => {
      mockSetMessage!({
        topic: 'alert',
        data: {
          id: 99,
          alert_type: 'Test_Alert',
          severity: 'HIGH',
          src_ip: '9.9.9.9',
          dst_ip: '8.8.8.8',
          timestamp: new Date().toISOString(),
          description: 'Injected via WS',
          action_taken: 'Blocked'
        }
      });
    });

    // Verify it updates AlertFeed
    await waitFor(() => {
      expect(screen.getByText('TEST ALERT')).toBeInTheDocument();
      expect(screen.getByText(/9\.9\.9\.9/)).toBeInTheDocument();
    });
  });

  it('displays error gracefully if stats API fails', async () => {
    // Override MSW handler for this test
    const { server } = await import('../mocks/server');
    const { http, HttpResponse } = await import('msw');
    server.use(
      http.get('*/api/v1/stats', () => {
        return HttpResponse.json({ error: 'Server Error' }, { status: 500 });
      })
    );

    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <Dashboard />
      </QueryClientProvider>
    );

    // Should still render dashboard, but stats might be 0 or empty depending on error handling
    await waitFor(() => {
      // If error occurs, stats default to empty object in Dashboard.tsx
      expect(screen.getAllByText('0').length).toBeGreaterThan(0); // total packets default 0
    });
  });
});
