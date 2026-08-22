import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  danger?: boolean;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({ isOpen, title, message, onConfirm, onCancel, danger = false }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-[var(--nova-card)] border border-[var(--nova-border)] w-full max-w-md rounded-xl shadow-2xl p-6 relative animate-in fade-in zoom-in-95 duration-200">
        <button onClick={onCancel} className="absolute top-4 right-4 text-[var(--nova-muted)] hover:text-white transition">
          <X className="w-5 h-5" />
        </button>
        
        <div className="flex items-center space-x-3 mb-4">
          {danger && <AlertTriangle className="w-6 h-6 text-[var(--nova-red)]" />}
          <h3 className="text-xl font-bold">{title}</h3>
        </div>
        
        <p className="text-[var(--nova-text)] mb-8 opacity-80">{message}</p>
        
        <div className="flex justify-end space-x-3">
          <button 
            onClick={onCancel}
            className="px-4 py-2 rounded-lg bg-[var(--nova-bg)] border border-[var(--nova-border)] hover:bg-gray-800 transition"
          >
            Cancel
          </button>
          <button 
            onClick={onConfirm}
            className={`px-4 py-2 rounded-lg font-bold transition ${danger ? 'bg-[var(--nova-red)] hover:brightness-110 text-white' : 'bg-[var(--nova-purple)] hover:brightness-110 text-white'}`}
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};
