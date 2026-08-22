"use client";
import React, { useEffect, useState } from 'react';
import { adminAPI } from '@/api/client';
import { CreditCard, Edit3, TrendingUp, DollarSign } from 'lucide-react';
import { PlanBadge } from '@/components/billing/PlanBadge';

export default function AdminBillingPage() {
  const [plans, setPlans] = useState<any[]>([]);

  useEffect(() => {
    adminAPI.getPlans().then(res => setPlans(res.data)).catch(() => {
      setPlans([
        { id: '1', name: 'Free', price_monthly: 0, messages_per_day: 50, is_active: true },
        { id: '2', name: 'Pro', price_monthly: 1000, messages_per_day: 500, is_active: true },
        { id: '3', name: 'Enterprise', price_monthly: 5000, messages_per_day: -1, is_active: true }
      ]);
    });
  }, []);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold flex items-center"><CreditCard className="w-8 h-8 mr-3 text-[#D4A017]" /> Billing & Plans</h1>
          <p className="text-[#6B6B80] mt-1">Manage subscription tiers and revenue</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6">
          <div className="flex justify-between items-center mb-4"><span className="text-[#6B6B80] font-medium text-sm">Monthly Revenue</span><DollarSign className="w-5 h-5 text-[#1D9E75]" /></div>
          <p className="text-3xl font-bold">₹15,000</p>
          <p className="text-[#1D9E75] text-xs font-bold mt-2 flex items-center"><TrendingUp className="w-3 h-3 mr-1" /> +12% from last month</p>
        </div>
        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6">
          <div className="flex justify-between items-center mb-4"><span className="text-[#6B6B80] font-medium text-sm">Active Subscriptions</span><CreditCard className="w-5 h-5 text-[#378ADD]" /></div>
          <p className="text-3xl font-bold">124</p>
          <p className="text-[#378ADD] text-xs font-bold mt-2 flex items-center">88% retention rate</p>
        </div>
      </div>

      <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl overflow-hidden">
        <div className="p-6 border-b border-[#1E1E2E] flex justify-between items-center">
          <h2 className="text-xl font-bold">Subscription Tiers</h2>
          <button className="text-sm bg-[#1E1E2E] hover:bg-[#2A2A3A] text-white px-4 py-2 rounded-lg transition">Create Plan</button>
        </div>
        <div className="divide-y divide-[#1E1E2E]">
          {plans.map(plan => (
            <div key={plan.id} className="p-6 flex justify-between items-center hover:bg-[#1A1A24] transition">
              <div>
                <div className="flex items-center space-x-3 mb-1">
                  <h3 className="font-bold text-lg">{plan.name}</h3>
                  <PlanBadge plan={plan.name.toLowerCase()} />
                  {!plan.is_active && <span className="bg-red-500/20 text-red-400 text-xs px-2 py-0.5 rounded font-bold">INACTIVE</span>}
                </div>
                <p className="text-[#6B6B80] text-sm">₹{plan.price_monthly}/mo • {plan.messages_per_day === -1 ? 'Unlimited' : plan.messages_per_day} msgs/day</p>
              </div>
              <button className="text-[#6B6B80] hover:text-[#D4A017] transition p-2 bg-[#0A0A0F] rounded-lg border border-[#1E1E2E] hover:border-[#D4A017]">
                <Edit3 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
