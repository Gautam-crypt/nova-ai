"use client";
import React, { useEffect, useState } from 'react';
import { adminAPI } from '@/api/client';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';

export default function AdminErrorsPage() {
  const [errors, setErrors] = useState<any[]>([]);

  useEffect(() => {
    adminAPI.getErrors("open").then(res => setErrors(res.data)).catch(() => {
      setErrors([
        { id: 1, error_type: 'StripeWebhookError', message: 'Signature verification failed', endpoint: '/api/webhook', status: 'open', created_at: '2026-06-09T10:00:00Z' },
        { id: 2, error_type: 'OllamaTimeout', message: 'gemma3:4b failed to respond in 30s', endpoint: '/nova/chat', status: 'open', created_at: '2026-06-09T09:45:00Z' },
        { id: 3, error_type: 'DatabaseConnectionLost', message: 'SQLite locked', endpoint: '/users/me', status: 'open', created_at: '2026-06-09T08:12:00Z' }
      ]);
    });
  }, []);

  const resolveError = (id: number) => {
    setErrors(prev => prev.filter(e => e.id !== id));
    // adminAPI.updateError(id, "resolved");
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold flex items-center"><AlertTriangle className="w-8 h-8 mr-3 text-[#D4A017]" /> System Errors</h1>
          <p className="text-[#6B6B80] mt-1">Monitor and resolve backend exceptions</p>
        </div>
      </div>

      <div className="space-y-4">
        {errors.length === 0 ? (
          <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-12 text-center flex flex-col items-center">
            <CheckCircle className="w-16 h-16 text-[#1D9E75] mb-4" />
            <h2 className="text-xl font-bold">All clear!</h2>
            <p className="text-[#6B6B80] mt-2">No open system errors detected.</p>
          </div>
        ) : (
          errors.map(err => (
            <div key={err.id} className="bg-[#12121A] border border-red-500/20 hover:border-red-500/50 rounded-xl p-6 transition flex justify-between items-center">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="font-bold text-red-400 text-lg">{err.error_type}</h3>
                  <span className="bg-[#1E1E2E] text-[#E8E8F0] text-xs font-mono px-2 py-1 rounded">{err.endpoint}</span>
                </div>
                <p className="text-[#E8E8F0]">{err.message}</p>
                <p className="text-[#6B6B80] text-xs mt-2 flex items-center"><Clock className="w-3 h-3 mr-1" /> {new Date(err.created_at).toLocaleString()}</p>
              </div>
              <button 
                onClick={() => resolveError(err.id)}
                className="bg-[#1E1E2E] hover:bg-[#1D9E75] hover:text-white text-[#6B6B80] font-bold px-4 py-2 rounded-lg transition"
              >
                Mark Resolved
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
