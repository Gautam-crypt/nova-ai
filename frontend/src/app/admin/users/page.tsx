"use client";
import React, { useEffect, useState } from 'react';
import { adminAPI } from '@/api/client';
import { Users, Search, MoreVertical, Shield, User as UserIcon } from 'lucide-react';
import { PlanBadge } from '@/components/billing/PlanBadge';

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminAPI.getUsers(1, 50)
      .then(res => { setUsers(res.data.users); setLoading(false); })
      .catch(() => {
        // Fallback mock data if API is not fully implemented yet
        setUsers([
          { id: '1', full_name: 'Gautam Tiwari', email: 'admin@example.com', role: 'admin', plan_id: 'enterprise_plan', subscription_status: 'active', messages_total: 15420, created_at: '2026-06-01T10:00:00Z' },
          { id: '2', full_name: 'Beta Tester', email: 'tester@example.com', role: 'user', plan_id: 'pro_plan', subscription_status: 'active', messages_total: 432, created_at: '2026-06-05T14:30:00Z' },
          { id: '3', full_name: 'John Doe', email: 'john@example.com', role: 'user', plan_id: 'free_plan', subscription_status: 'active', messages_total: 12, created_at: '2026-06-09T08:15:00Z' },
        ]);
        setLoading(false);
      });
  }, []);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold flex items-center"><Users className="w-8 h-8 mr-3 text-[#D4A017]" /> User Management</h1>
          <p className="text-[#6B6B80] mt-1">Manage all registered users across the NOVA platform</p>
        </div>
        <button className="bg-[#D4A017] hover:brightness-110 text-black font-bold py-2 px-6 rounded-lg shadow-lg transition">
          Create User
        </button>
      </div>

      <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl overflow-hidden">
        <div className="p-4 border-b border-[#1E1E2E] flex justify-between items-center bg-[#0A0A0F]">
          <div className="relative w-64">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#6B6B80]" />
            <input type="text" placeholder="Search users..." className="w-full bg-[#12121A] border border-[#1E1E2E] text-white rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:border-[#D4A017] transition" />
          </div>
          <div className="text-[#6B6B80] text-sm">Showing {users.length} users</div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#12121A] border-b border-[#1E1E2E] text-[#6B6B80] text-sm uppercase tracking-wider">
                <th className="p-4 font-medium">User</th>
                <th className="p-4 font-medium">Role</th>
                <th className="p-4 font-medium">Plan</th>
                <th className="p-4 font-medium">Usage</th>
                <th className="p-4 font-medium">Joined</th>
                <th className="p-4 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E1E2E]">
              {loading ? (
                <tr><td colSpan={6} className="p-8 text-center text-[#6B6B80]">Loading users...</td></tr>
              ) : users.map(u => (
                <tr key={u.id} className="hover:bg-[#1A1A24] transition">
                  <td className="p-4">
                    <div className="flex items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 font-bold text-xs ${u.role === 'admin' ? 'bg-[#D4A017] text-black' : 'bg-[#1E1E2E] text-white'}`}>
                        {u.full_name.charAt(0)}
                      </div>
                      <div>
                        <p className="font-bold text-[#E8E8F0]">{u.full_name}</p>
                        <p className="text-xs text-[#6B6B80]">{u.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    {u.role === 'admin' ? (
                      <span className="flex items-center text-xs font-bold text-[#D4A017]"><Shield className="w-3 h-3 mr-1" /> ADMIN</span>
                    ) : (
                      <span className="flex items-center text-xs text-[#6B6B80]"><UserIcon className="w-3 h-3 mr-1" /> USER</span>
                    )}
                  </td>
                  <td className="p-4"><PlanBadge plan={u.plan_id?.split('_')[0] || 'free'} /></td>
                  <td className="p-4 text-sm text-[#E8E8F0]">{u.messages_total.toLocaleString()} msgs</td>
                  <td className="p-4 text-sm text-[#6B6B80]">{new Date(u.created_at).toLocaleDateString()}</td>
                  <td className="p-4 text-right">
                    <button className="text-[#6B6B80] hover:text-white transition"><MoreVertical className="w-5 h-5" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
