"use client";
import React from 'react';
import { useToastStore } from '@/stores/toastStore';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';

export default function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  return (
    <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => {
        let bgColor = "bg-[#12121A]";
        let borderColor = "border-[var(--nova-border)]";
        let Icon = Info;
        let iconColor = "text-[var(--nova-purple)]";

        if (toast.type === "success") {
          borderColor = "border-[var(--nova-green)]";
          Icon = CheckCircle;
          iconColor = "text-[var(--nova-green)]";
        } else if (toast.type === "error") {
          borderColor = "border-[var(--nova-red)]";
          Icon = AlertCircle;
          iconColor = "text-[var(--nova-red)]";
        }

        return (
          <div 
            key={toast.id} 
            className={`pointer-events-auto flex items-center p-4 rounded-lg shadow-2xl border bg-[#12121A] ${borderColor} animate-in slide-in-from-right-8 duration-300`}
            style={{ minWidth: '300px' }}
          >
            <Icon className={`w-5 h-5 mr-3 flex-shrink-0 ${iconColor}`} />
            <p className="flex-1 text-sm font-medium text-white">{toast.message}</p>
            <button 
              onClick={() => removeToast(toast.id)}
              className="ml-4 text-[var(--nova-muted)] hover:text-white transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
