"use client";
import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { MessageSquare, Brain, FolderOpen, CreditCard, Key, Settings, LogOut, Sparkles } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { PlanBadge } from '@/components/billing/PlanBadge';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  if (!mounted || !user) return null;

  const links = [
    { name: 'Console', path: '/dashboard/console', icon: MessageSquare },
    { name: 'Security', path: '/dashboard/security', icon: Key },
    { name: 'Chat', path: '/dashboard/chat', icon: MessageSquare },
    { name: 'Memory', path: '/dashboard/memory', icon: Brain },
    { name: 'Files', path: '/dashboard/files', icon: FolderOpen },
    { name: 'Billing', path: '/dashboard/billing', icon: CreditCard },
    { name: 'API Keys', path: '/dashboard/api-keys', icon: Key },
    { name: 'Settings', path: '/dashboard/settings', icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-[#0A0A0F] overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r border-[#1E1E2E] flex flex-col bg-[#12121A] justify-between">
        <div>
          <div className="p-6 border-b border-[#1E1E2E]">
            <span className="text-xl font-extrabold tracking-widest text-[#7F77DD] flex items-center">
              <Sparkles className="w-5 h-5 mr-2" /> NOVA
            </span>
          </div>
          
          <nav className="p-4 space-y-1">
            {links.map(l => {
              const isActive = pathname === l.path || pathname.startsWith(`${l.path}/`);
              return (
                <Link key={l.path} href={l.path} className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition ${isActive ? 'bg-[#7F77DD] text-white font-bold shadow-lg' : 'text-[#6B6B80] hover:bg-[#1E1E2E] hover:text-[#E8E8F0]'}`}>
                  <l.icon className="w-5 h-5" />
                  <span>{l.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="p-4 border-t border-[#1E1E2E]">
          <div className="px-4 py-3 mb-2 bg-[#0A0A0F] border border-[#1E1E2E] rounded-lg">
            <p className="text-[#E8E8F0] text-sm font-bold truncate mb-1">{user.full_name}</p>
            <PlanBadge plan={user.plan_id?.includes('free') ? 'free' : user.plan_id?.includes('ent') ? 'enterprise' : 'pro'} />
          </div>
          <button onClick={logout} className="w-full flex items-center space-x-3 text-[#6B6B80] hover:text-[#E24B4A] hover:bg-red-500/10 px-4 py-3 rounded-lg transition">
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-8">
        {children}
      </div>
    </div>
  );
}
