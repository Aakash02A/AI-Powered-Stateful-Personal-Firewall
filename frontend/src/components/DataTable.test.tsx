import { render, screen, fireEvent } from '@testing-library/react';
import { DataTable } from './DataTable';
import { describe, it, expect } from 'vitest';

describe('DataTable', () => {
  const columns = [
    { key: 'name', header: 'Name', sortable: true },
    { key: 'value', header: 'Value', sortable: false }
  ];
  const data = [
    { name: 'Alpha', value: 10 },
    { name: 'Beta', value: 20 }
  ];

  it('renders columns and data', () => {
    render(<DataTable columns={columns} data={data} />);
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Alpha')).toBeInTheDocument();
  });

  it('filters data based on search input', () => {
    render(<DataTable columns={columns} data={data} />);
    const input = screen.getByPlaceholderText('Search...');
    fireEvent.change(input, { target: { value: 'Beta' } });
    expect(screen.queryByText('Alpha')).not.toBeInTheDocument();
    expect(screen.getByText('Beta')).toBeInTheDocument();
  });

  it('renders loading state', () => {
    render(<DataTable columns={columns} data={[]} isLoading={true} />);
    // Loading state hides "No data found"
    expect(screen.queryByText('No data found')).not.toBeInTheDocument();
  });
});
