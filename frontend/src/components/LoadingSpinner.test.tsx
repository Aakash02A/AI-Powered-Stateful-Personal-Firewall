import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from './LoadingSpinner';
import { describe, it, expect } from 'vitest';

describe('LoadingSpinner', () => {
  it('renders correctly', () => {
    const { container } = render(<LoadingSpinner />);
    expect(screen.getByText('Initializing Security Modules...')).toBeInTheDocument();
    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });
});
