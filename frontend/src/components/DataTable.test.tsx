import { render, screen } from '@testing-library/react';
import { DataTable } from './DataTable';
import { describe, it, expect } from 'vitest';
import userEvent from '@testing-library/user-event';

// Mock moved to setupTests.ts

describe('DataTable', () => {
  const columns = [
    { key: 'name', header: 'Name', sortable: true },
    { key: 'value', header: 'Value', sortable: false }
  ];
  const data = [
    { name: 'Alpha', value: 10 },
    { name: 'Beta', value: 20 },
    { name: 'Gamma', value: 30 }
  ];

  it('renders columns and data', () => {
    render(<DataTable columns={columns} data={data} />);
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Alpha')).toBeInTheDocument();
    expect(screen.getByText('Beta')).toBeInTheDocument();
    expect(screen.getByText('Gamma')).toBeInTheDocument();
  });

  it('filters data based on search input', async () => {
    const user = userEvent.setup();
    render(<DataTable columns={columns} data={data} />);
    const input = screen.getByPlaceholderText('Search...');
    await user.type(input, 'Beta');
    expect(screen.queryByText('Alpha')).not.toBeInTheDocument();
    expect(screen.getByText('Beta')).toBeInTheDocument();
  });

  it('sorts by column click', async () => {
    const user = userEvent.setup();
    render(<DataTable columns={columns} data={data} />);
    
    const headerCell = screen.getByText('Name');
    
    // Sort ascending first click
    await user.click(headerCell);
    let rowsAsc = screen.getAllByRole('row');
    expect(rowsAsc[1]).toHaveTextContent('Alpha');
    
    // Sort descending second click
    await user.click(headerCell);
    let rowsDesc = screen.getAllByRole('row');
    expect(rowsDesc[1]).toHaveTextContent('Gamma');
  });

  it('renders loading state', () => {
    render(<DataTable columns={columns} data={[]} isLoading={true} />);
    // Loading state hides "No data found"
    expect(screen.queryByText('No data found')).not.toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(<DataTable columns={columns} data={[]} />);
    expect(screen.getByText('No data found')).toBeInTheDocument();
  });
});
