import { render, screen, fireEvent } from '@testing-library/react';
import { ConfirmDialog } from './ConfirmDialog';
import { describe, it, expect, vi } from 'vitest';

describe('ConfirmDialog', () => {
  it('renders title and message', () => {
    render(
      <ConfirmDialog 
        isOpen={true} 
        onClose={() => {}} 
        onConfirm={() => {}} 
        title="Delete Item" 
        message="Are you sure you want to delete this?" 
      />
    );
    expect(screen.getByText('Delete Item')).toBeInTheDocument();
    expect(screen.getByText('Are you sure you want to delete this?')).toBeInTheDocument();
  });

  it('calls onConfirm and onClose when confirm is clicked', () => {
    const handleClose = vi.fn();
    const handleConfirm = vi.fn();
    
    render(
      <ConfirmDialog 
        isOpen={true} 
        onClose={handleClose} 
        onConfirm={handleConfirm} 
        title="Test" 
        message="Msg" 
        confirmText="Yes, Delete"
      />
    );
    
    const confirmBtn = screen.getByRole('button', { name: 'Yes, Delete' });
    fireEvent.click(confirmBtn);
    
    expect(handleConfirm).toHaveBeenCalledTimes(1);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
