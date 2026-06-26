import { render, screen } from '@testing-library/react';
import { AlertFeed } from './AlertFeed';
import { describe, it, expect } from 'vitest';

describe('AlertFeed', () => {
  it('renders empty state', () => {
    render(<AlertFeed alerts={[]} />);
    expect(screen.getByText('No active threats detected in this session')).toBeInTheDocument();
  });

  it('renders alerts in order (assuming parent handles order, feed just displays)', () => {
    render(<AlertFeed alerts={[
      { timestamp: '2026-06-26T10:00:00Z', severity: 'HIGH', alert_type: 'Scan', src_ip: '1.2.3.4', dst_ip: '5.6.7.8', description: 'Alert 1', action_taken: 'Blocked' },
      { timestamp: '2026-06-26T10:01:00Z', severity: 'MEDIUM', alert_type: 'Flood', src_ip: '1.2.3.5', dst_ip: '5.6.7.8', description: 'Alert 2', action_taken: 'Allowed' }
    ]} />);
    
    // Check if both descriptions are present
    expect(screen.getByText('Alert 1')).toBeInTheDocument();
    expect(screen.getByText('Alert 2')).toBeInTheDocument();
    expect(screen.getByText('SCAN')).toBeInTheDocument();
    expect(screen.getByText('FLOOD')).toBeInTheDocument();
  });

  it('color-codes by severity', () => {
    render(<AlertFeed alerts={[
      { timestamp: '2026-06-26T10:00:00Z', severity: 'HIGH', alert_type: 'Scan', src_ip: '1.2.3.4', dst_ip: '5.6.7.8', description: 'Critical alert', action_taken: 'Blocked' },
    ]} />);
    
    const alertIcon = screen.getByText('SCAN').closest('div')?.querySelector('svg');
    const container = screen.getByText('Critical alert').closest('div.flex.items-start');
    expect(container).toHaveClass('border-warning/20');
  });

  it('updates on new alerts', () => {
    const { rerender } = render(<AlertFeed alerts={[]} />);
    expect(screen.getByText('No active threats detected in this session')).toBeInTheDocument();
    
    rerender(<AlertFeed alerts={[{ timestamp: '2026-06-26T10:00:00Z', severity: 'LOW', alert_type: 'Ping', src_ip: '1.2.3.4', dst_ip: '5.6.7.8', description: 'New alert', action_taken: 'Allowed' }]} />);
    expect(screen.getByText('New alert')).toBeInTheDocument();
  });
});
