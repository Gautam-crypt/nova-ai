"use client";
import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Home, Users, CreditCard, BarChart2, AlertTriangle, FileText, Settings, LogOut, Shield } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!user || user.role !== 'admin') {
      router.push('/login');
    }
  }, [user, router]);

  if (!mounted || !user || user.role !== 'admin') return null;

  const links = [
    { name: 'Dashboard', path: '/admin/dashboard', icon: Home },
    { name: 'Users', path: '/admin/users', icon: Users },
    { name: 'Billing', path: '/admin/billing', icon: CreditCard },
    { name: 'Analytics', path: '/admin/analytics', icon: BarChart2 },
    { name: 'Errors', path: '/admin/errors', icon: AlertTriangle },
    { name: 'Logs', path: '/admin/logs', icon: FileText },
    { name: 'Settings', path: '/admin/settings', icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-[#0A0A0F] overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r border-[#1E1E2E] flex flex-col bg-[#12121A] justify-between">
        <div>
          <div className="p-6 border-b border-[#1E1E2E]">
            <span className="text-xl font-extrabold tracking-widest text-[#D4A017] flex items-center">
              <Shield className="w-6 h-6 mr-2" /> NOVA ADMIN
            </span>
          </div>
          
          <nav className="p-4 space-y-1">
            {links.map(l => {
              const isActive = pathname === l.path || pathname.startsWith(`${l.path}/`);
              return (
                <Link key={l.path} href={l.path} className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition ${isActive ? 'bg-[#D4A017] text-black font-bold' : 'text-[#6B6B80] hover:bg-[#1E1E2E] hover:text-white'}`}>
                  <l.icon className="w-5 h-5" />
                  <span>{l.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="p-4 border-t border-[#1E1E2E]">
          <div className="flex items-center space-x-3 px-4 py-3 mb-2">
            <div className="w-10 h-10 rounded-full bg-[#D4A017] flex items-center justify-center text-black font-bold uppercase">
              {user.full_name.charAt(0)}
            </div>
            <div>
              <p className="text-[#E8E8F0] text-sm font-bold truncate">{user.full_name}</p>
              <span className="bg-[#D4A017] text-black text-[10px] font-bold px-2 py-0.5 rounded uppercase">Admin</span>
            </div>
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
