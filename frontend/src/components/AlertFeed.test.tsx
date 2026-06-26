import { render, screen } from '@testing-library/react';
import { AlertFeed } from './AlertFeed';
import { describe, it, expect } from 'vitest';

describe('AlertFeed', () => {
  it('renders empty state', () => {
    render(<AlertFeed alerts={[]} />);
    expect(screen.getByText('No active threats detected in this session')).toBeInTheDocument();
  });

  it('renders alerts', () => {
    render(<AlertFeed alerts={[{
      timestamp: new Date().toISOString(),
      severity: 'HIGH',
      alert_type: 'Scan',
      src_ip: '1.2.3.4',
      dst_ip: '5.6.7.8',
      description: 'Test',
      action_taken: 'Blocked'
    }]} />);
    expect(screen.getByText('SCAN')).toBeInTheDocument();
    expect(screen.getByText(/1\.2\.3\.4/i)).toBeInTheDocument();
  });
});
