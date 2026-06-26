import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { DashboardLayout } from './DashboardLayout';
import { describe, it, expect } from 'vitest';

describe('DashboardLayout', () => {
  it('renders sidebar navigation', () => {
    render(
      <BrowserRouter>
        <DashboardLayout />
      </BrowserRouter>
    );
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Active Connections')).toBeInTheDocument();
  });
});
