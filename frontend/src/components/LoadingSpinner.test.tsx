import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from './LoadingSpinner';
import { describe, it, expect } from 'vitest';

describe('LoadingSpinner', () => {
  it('renders correctly', () => {
    render(<LoadingSpinner />);
    expect(screen.getByText('Initializing Security Modules...')).toBeInTheDocument();
  });
});
