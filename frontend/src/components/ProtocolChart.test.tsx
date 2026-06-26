import { render, screen } from '@testing-library/react';
import { ProtocolChart } from './ProtocolChart';
import { describe, it, expect } from 'vitest';

describe('ProtocolChart', () => {
  it('renders empty state when no data provided', () => {
    render(<ProtocolChart data={{}} />);
    expect(screen.getByText('No protocol data available')).toBeInTheDocument();
  });

  it('renders chart when data is provided', () => {
    const { container } = render(<ProtocolChart data={{ TCP: 100, UDP: 50 }} />);
    expect(container.querySelector('.recharts-responsive-container')).toBeInTheDocument();
  });
});
