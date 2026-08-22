"use client";
import React, { useEffect, useState } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { userAPI } from '@/api/client';
import Link from 'next/link';
import { MessageSquare, UploadCloud, Brain, ArrowRight } from 'lucide-react';
import { PlanBadge } from '@/components/billing/PlanBadge';

export default function UserDashboardPage() {
  const { user } = useAuthStore();
  const [usage, setUsage] = useState({ current: 0, limit: 50 });
  const [recentChats, setRecentChats] = useState<any[]>([]);

  useEffect(() => {
    userAPI.getUsage().then(res => setUsage(res.data)).catch(() => {
      setUsage({ current: 12, limit: user?.plan_id?.includes('pro') ? 500 : user?.plan_id?.includes('ent') ? -1 : 50 });
    });
    // Mock recent chats
    setRecentChats([
      { id: '1', title: 'Python debugging help', text: 'You need to check your indentation...', time: '10 mins ago' },
      { id: '2', title: 'React Hooks explanation', text: 'useEffect runs after render...', time: 'Yesterday' },
      { id: '3', title: 'Stripe integration', text: 'First, create a checkout session...', time: '2 days ago' }
    ]);
  }, [user]);

  if (!user) return null;

  const isFree = user.plan_id?.includes('free') || !user.plan_id;
  const percent = usage.limit === -1 ? 100 : Math.min((usage.current / usage.limit) * 100, 100);

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-extrabold">
          {user.nova_name ? `Hey ${user.nova_name}! 👋` : `Welcome, ${user.full_name}`}
        </h1>
        <Link href="/dashboard" className="bg-[#7F77DD] hover:brightness-110 text-white font-bold py-2 px-6 rounded-lg shadow-lg flex items-center transition">
          <MessageSquare className="w-5 h-5 mr-2" /> Start Chatting
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Usage Card */}
        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6">
          <h2 className="text-[#6B6B80] font-bold text-sm uppercase tracking-wider mb-6">Messages Today</h2>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-[#E8E8F0]">Usage</span>
            <span className="font-bold">{usage.limit === -1 ? 'Unlimited' : `${usage.current} / ${usage.limit}`}</span>
          </div>
          <div className="h-3 w-full bg-[#1E1E2E] rounded-full overflow-hidden">
            <div 
              className={`h-full ${usage.limit === -1 ? 'bg-[#1D9E75]' : percent > 80 ? 'bg-red-500' : 'bg-[#7F77DD]'} transition-all duration-500`} 
              style={{ width: `${percent}%` }}
            ></div>
          </div>
          <p className="text-right text-[#6B6B80] text-xs mt-2">Resets at midnight</p>
        </div>

        {/* Plan Card */}
        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-[#6B6B80] font-bold text-sm uppercase tracking-wider">Current Plan</h2>
              <PlanBadge plan={isFree ? 'free' : user.plan_id.includes('ent') ? 'enterprise' : 'pro'} />
            </div>
            <p className="text-[#E8E8F0] text-sm">
              {isFree ? "You are on the free tier. Upgrade to unlock long-term memory, file uploads, and higher limits." : "You have access to all NOVA subsystems and advanced memory."}
            </p>
          </div>
          {isFree ? (
            <Link href="/pricing" className="mt-4 text-[#7F77DD] font-bold text-sm hover:underline flex items-center">
              Upgrade to Pro <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          ) : (
            <p className="mt-4 text-[#6B6B80] text-sm">Next billing date: <span className="text-[#E8E8F0]">12 Jun 2026</span></p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/dashboard" className="bg-[#0A0A0F] border border-[#1E1E2E] hover:border-[#7F77DD] rounded-xl p-6 transition flex flex-col items-center justify-center text-center group">
          <MessageSquare className="w-8 h-8 text-[#7F77DD] mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-bold">Chat with NOVA</h3>
        </Link>
        <Link href="/dashboard/files" className="bg-[#0A0A0F] border border-[#1E1E2E] hover:border-[#378ADD] rounded-xl p-6 transition flex flex-col items-center justify-center text-center group">
          <UploadCloud className="w-8 h-8 text-[#378ADD] mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-bold">Upload a File</h3>
        </Link>
        <Link href="/dashboard/memory" className="bg-[#0A0A0F] border border-[#1E1E2E] hover:border-[#D4A017] rounded-xl p-6 transition flex flex-col items-center justify-center text-center group">
          <Brain className="w-8 h-8 text-[#D4A017] mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-bold">View Memory</h3>
        </Link>
      </div>

      <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl overflow-hidden">
        <div className="p-6 border-b border-[#1E1E2E] flex justify-between items-center">
          <h2 className="font-bold">Recent Conversations</h2>
          <Link href="/dashboard/conversations" className="text-[#7F77DD] text-sm hover:underline">View All</Link>
        </div>
        <div>
          {recentChats.map(chat => (
            <div key={chat.id} className="p-4 border-b border-[#1E1E2E] hover:bg-[#0A0A0F] transition cursor-pointer flex justify-between items-center">
              <div>
                <h4 className="font-bold text-[#E8E8F0] mb-1">{chat.title}</h4>
                <p className="text-sm text-[#6B6B80] truncate max-w-md">{chat.text}</p>
              </div>
              <span className="text-xs text-[#6B6B80] whitespace-nowrap">{chat.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
