import { render, screen } from '@testing-library/react';
import { StatCard } from './StatCard';
import { describe, it, expect } from 'vitest';

describe('StatCard', () => {
  it('renders correctly with required props', () => {
    render(<StatCard label="Total Alerts" value={100} />);
    expect(screen.getByText('Total Alerts')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('updates when props change', () => {
    const { rerender } = render(<StatCard label="Test" value={100} />);
    expect(screen.getByText('100')).toBeInTheDocument();
    
    rerender(<StatCard label="Test" value={200} />);
    expect(screen.getByText('200')).toBeInTheDocument();
  });

  it('renders trend when provided', () => {
    render(<StatCard label="Total Alerts" value={100} trend="Up 5%" trendUp={false} />);
    const trendEl = screen.getByText('Up 5%');
    expect(trendEl).toBeInTheDocument();
    expect(trendEl.className).toMatch(/text-red|text-danger/i);
  });

  it('renders positive trend when provided', () => {
    render(<StatCard label="Total Alerts" value={100} trend="Down 5%" trendUp={true} />);
    const trendEl = screen.getByText('Down 5%');
    expect(trendEl).toBeInTheDocument();
    expect(trendEl.className).toMatch(/text-emerald|text-green|text-success/i);
  });

});
