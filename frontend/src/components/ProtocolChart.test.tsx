import { render, screen } from '@testing-library/react';
import { ProtocolChart } from './ProtocolChart';
import { describe, it, expect, vi } from 'vitest';

vi.mock('recharts', async (importOriginal) => {
  const actual = await importOriginal<typeof import('recharts')>();
  return {
    ...actual,
    ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  };
});

describe('ProtocolChart', () => {
  it('renders empty state when no data provided', () => {
    render(<ProtocolChart data={{}} />);
    expect(screen.getByText('No protocol data available')).toBeInTheDocument();
  });

  it('renders chart when data is provided', () => {
    render(<ProtocolChart data={{ TCP: 100, UDP: 50 }} />);
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
  });
});
