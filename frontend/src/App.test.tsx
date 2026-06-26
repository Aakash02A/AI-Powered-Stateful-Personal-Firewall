import { render, screen, waitFor } from '@testing-library/react';
import App from './App';
import { describe, it, expect, vi } from 'vitest';

vi.mock('./store/themeStore', () => ({
  useThemeStore: () => ({ isDark: true, toggleTheme: vi.fn() })
}));

describe('App', () => {
  it('renders without crashing and displays the dashboard', async () => {
    render(<App />);
    
    // Using Suspense, it might show LoadingSpinner initially, then the Dashboard
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    
    // App sets up routing, so Dashboard should render at '/'
    await waitFor(() => {
      expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    }, { timeout: 3000 });
  });
});
