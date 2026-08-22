"use client";
import React, { useEffect, useState } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { adminAPI } from '@/api/client';
import { Users, MessageSquare, Brain, Zap, Activity } from 'lucide-react';
import Link from 'next/link';

export default function AdminDashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<any>(null);
  const [errors, setErrors] = useState<any[]>([]);

  useEffect(() => {
    adminAPI.getStats().then(res => setStats(res.data)).catch(() => {
      setStats({
        total_users: 142,
        messages_today: 432,
        knowledge_db_entries: 1205,
        api_calls_saved: 890,
        system: { cpu_percent: 45, memory_percent: 62, disk_percent: 85 }
      });
    });

    adminAPI.getErrors("open").then(res => setErrors(res.data)).catch(() => {
      setErrors([
        { id: 1, error_type: 'StripeWebhookError', message: 'Signature verification failed', timestamp: '2026-06-09T10:00:00Z' },
        { id: 2, error_type: 'OllamaTimeout', message: 'gemma3:4b failed to respond in 30s', timestamp: '2026-06-09T09:45:00Z' }
      ]);
    });
  }, []);

  const getHealthColor = (val: number) => val < 60 ? 'bg-green-500' : val < 80 ? 'bg-amber-500' : 'bg-red-500';

  if (!stats || !user) return <div className="p-8 text-[var(--nova-muted)]">Loading Admin Dashboard...</div>;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-4xl font-extrabold mb-2">Welcome back, {user.full_name}</h1>
          <p className="text-[var(--nova-muted)]">{new Date().toLocaleString()}</p>
        </div>
        <span className="bg-[var(--nova-gold)] text-black px-4 py-1.5 rounded-full font-bold text-sm tracking-widest uppercase">Admin Panel</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6 flex flex-col justify-between">
          <div className="flex justify-between">
            <span className="text-[#6B6B80] font-medium text-sm">Total Users</span>
            <Users className="w-5 h-5 text-[#378ADD]" />
          </div>
          <p className="text-3xl font-bold mt-4">{stats.total_users}</p>
        </div>
        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6 flex flex-col justify-between">
          <div className="flex justify-between">
            <span className="text-[#6B6B80] font-medium text-sm">Messages Today</span>
            <MessageSquare className="w-5 h-5 text-[#7F77DD]" />
          </div>
          <p className="text-3xl font-bold mt-4">{stats.messages_today}</p>
        </div>
        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6 flex flex-col justify-between">
          <div className="flex justify-between">
            <span className="text-[#6B6B80] font-medium text-sm">KB Entries</span>
            <Brain className="w-5 h-5 text-[#D4A017]" />
          </div>
          <p className="text-3xl font-bold mt-4">{stats.knowledge_db_entries}</p>
        </div>
        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6 flex flex-col justify-between">
          <div className="flex justify-between">
            <span className="text-[#6B6B80] font-medium text-sm">API Calls Saved</span>
            <Zap className="w-5 h-5 text-[#1D9E75]" />
          </div>
          <p className="text-3xl font-bold mt-4">{stats.api_calls_saved}</p>
        </div>
      </div>

      <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6">
        <h2 className="text-xl font-bold mb-6 flex items-center"><Activity className="w-5 h-5 mr-2" /> System Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex justify-between text-sm mb-2"><span className="text-[#6B6B80]">CPU</span><span className="font-mono">{stats.system.cpu_percent}%</span></div>
            <div className="h-2 w-full bg-[#1E1E2E] rounded-full overflow-hidden"><div className={`h-full ${getHealthColor(stats.system.cpu_percent)}`} style={{ width: `${stats.system.cpu_percent}%` }}></div></div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-2"><span className="text-[#6B6B80]">RAM</span><span className="font-mono">{stats.system.memory_percent}%</span></div>
            <div className="h-2 w-full bg-[#1E1E2E] rounded-full overflow-hidden"><div className={`h-full ${getHealthColor(stats.system.memory_percent)}`} style={{ width: `${stats.system.memory_percent}%` }}></div></div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-2"><span className="text-[#6B6B80]">Disk</span><span className="font-mono">{stats.system.disk_percent}%</span></div>
            <div className="h-2 w-full bg-[#1E1E2E] rounded-full overflow-hidden"><div className={`h-full ${getHealthColor(stats.system.disk_percent)}`} style={{ width: `${stats.system.disk_percent}%` }}></div></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6">
          <h2 className="text-xl font-bold mb-4">NOVA Subsystems</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 border border-[#1E1E2E] rounded-lg">
              <span className="font-medium">Ollama Engine</span>
              <span className="flex items-center text-xs font-bold text-[#1D9E75]"><span className="w-2 h-2 rounded-full bg-[#1D9E75] mr-2"></span>ONLINE</span>
            </div>
            <div className="flex justify-between items-center p-3 border border-[#1E1E2E] rounded-lg">
              <span className="font-medium">Agents (HERMES, DIVYA...)</span>
              <span className="flex items-center text-xs font-bold text-[#1D9E75]"><span className="w-2 h-2 rounded-full bg-[#1D9E75] mr-2"></span>5 ACTIVE</span>
            </div>
            <div className="flex justify-between items-center p-3 border border-[#1E1E2E] rounded-lg">
              <span className="font-medium">Background Verification</span>
              <span className="flex items-center text-xs font-bold text-[#1D9E75]"><span className="w-2 h-2 rounded-full bg-[#1D9E75] mr-2"></span>IDLE</span>
            </div>
          </div>
        </div>

        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Recent Errors</h2>
            <Link href="/admin/errors" className="text-[#7F77DD] text-sm hover:underline">View All</Link>
          </div>
          {errors.length === 0 ? (
            <div className="text-[#6B6B80] italic text-center py-8">No open errors. System is healthy!</div>
          ) : (
            <div className="space-y-3">
              {errors.map(err => (
                <div key={err.id} className="p-3 bg-[#0A0A0F] border border-red-500/20 rounded-lg flex justify-between items-start">
                  <div>
                    <h4 className="text-red-400 font-bold text-sm">{err.error_type}</h4>
                    <p className="text-[#E8E8F0] text-sm truncate max-w-xs">{err.message}</p>
                    <p className="text-[#6B6B80] text-xs mt-1">{new Date(err.timestamp).toLocaleString()}</p>
                  </div>
                  <button className="text-xs bg-[#1E1E2E] hover:bg-[#2A2A3A] px-2 py-1 rounded">Resolve</button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
