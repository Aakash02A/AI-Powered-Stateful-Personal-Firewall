import { render, screen } from '@testing-library/react';
import { NotificationHistory } from './NotificationHistory';
import { describe, it, expect } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe('NotificationHistory', () => {
  it('renders historical alerts when open', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <NotificationHistory isOpen={true} onClose={() => {}} />
      </QueryClientProvider>
    );
    
    expect(screen.getByText('Notification History')).toBeInTheDocument();
    
    // Wait for the mock API response to render
    // MSW mock returns "Port scan" and "SCAN"
    expect(await screen.findByText('SCAN')).toBeInTheDocument();
    expect(screen.getByText('Port scan')).toBeInTheDocument();
  });
});
