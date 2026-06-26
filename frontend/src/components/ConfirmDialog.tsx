import { Modal } from './Modal';
import { AlertTriangle } from 'lucide-react';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDestructive?: boolean;
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isDestructive = false
}: ConfirmDialogProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <div className="flex items-start space-x-4 mb-6">
        {isDestructive && (
          <div className="bg-danger/10 p-2 rounded-full flex-shrink-0">
            <AlertTriangle className="w-6 h-6 text-danger" />
          </div>
        )}
        <p className="text-slate-300 mt-1">{message}</p>
      </div>

      <div className="flex justify-end space-x-3 mt-4">
        <button
          onClick={onClose}
          className="px-4 py-2 text-sm font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-md transition-colors"
        >
          {cancelText}
        </button>
        <button
          onClick={() => {
            onConfirm();
            onClose();
          }}
          className={`px-4 py-2 text-sm font-medium text-white rounded-md transition-colors ${
            isDestructive 
              ? 'bg-danger hover:bg-danger/80' 
              : 'bg-primary hover:bg-primary/80'
          }`}
        >
          {confirmText}
        </button>
      </div>
    </Modal>
  );
}
