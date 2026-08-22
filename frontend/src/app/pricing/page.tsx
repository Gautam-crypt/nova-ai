"use client";
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { PlanCard, PlanData } from '@/components/billing/PlanCard';
import { billingAPI } from '@/api/client';
import { useAuthStore } from '@/stores/authStore';

const DEFAULT_PLANS: PlanData[] = [
  {
    id: "plan_free", name: "Free", price_monthly: 0, price_yearly: 0,
    features: [
      { name: "50 messages/day", included: true },
      { name: "Basic NOVA chat", included: true },
      { name: "Web search (HERMES)", included: true },
      { name: "Long-term memory", included: false },
      { name: "File uploads", included: false },
      { name: "Priority support", included: false }
    ]
  },
  {
    id: "plan_pro", name: "Pro", price_monthly: 499, price_yearly: 4999,
    features: [
      { name: "500 messages/day", included: true },
      { name: "Full memory (RAG)", included: true },
      { name: "All 5 agents", included: true },
      { name: "File uploads (10MB)", included: true },
      { name: "Streaming responses", included: true },
      { name: "Priority support", included: false }
    ]
  },
  {
    id: "plan_ent", name: "Enterprise", price_monthly: 1999, price_yearly: 19999,
    features: [
      { name: "Unlimited messages", included: true },
      { name: "Everything in Pro", included: true },
      { name: "Custom personality", included: true },
      { name: "API access + API keys", included: true },
      { name: "Priority support", included: true },
      { name: "Usage analytics", included: true }
    ]
  }
];

export default function PricingPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [plans, setPlans] = useState<PlanData[]>(DEFAULT_PLANS);

  useEffect(() => {
    // In a real scenario, we'd fetch plans:
    billingAPI.getPlans().then(res => {
      if (res.data && res.data.length > 0) {
        // Map API data if available, else keep defaults
      }
    }).catch(err => console.log("Using default plans", err));
  }, []);

  const handleSelect = (planId: string) => {
    if (planId.includes('free')) {
      router.push('/register');
    } else if (planId.includes('ent')) {
      window.location.href = "mailto:sales@nova.ai";
    } else {
      if (user) {
        router.push(`/checkout?plan=${planId}&cycle=${billingCycle}`);
      } else {
        router.push('/login');
      }
    }
  };

  return (
    <div className="min-h-screen bg-[var(--nova-bg)] text-white py-20 px-4">
      <div className="max-w-7xl mx-auto text-center mb-16">
        <h1 className="text-5xl font-extrabold mb-4 tracking-tight">Choose Your <span className="text-[var(--nova-purple)]">NOVA</span> Plan</h1>
        <p className="text-xl text-[var(--nova-muted)] max-w-2xl mx-auto">Get the personal AI assistant that fits your needs. Upgrade anytime.</p>
        
        <div className="mt-10 inline-flex items-center p-1 bg-[var(--nova-card)] border border-[var(--nova-border)] rounded-lg">
          <button 
            onClick={() => setBillingCycle('monthly')}
            className={`px-6 py-2 rounded-md text-sm font-bold transition ${billingCycle === 'monthly' ? 'bg-[var(--nova-purple)] text-white' : 'text-[var(--nova-muted)] hover:text-white'}`}
          >
            Monthly
          </button>
          <button 
            onClick={() => setBillingCycle('yearly')}
            className={`px-6 py-2 rounded-md text-sm font-bold transition flex items-center ${billingCycle === 'yearly' ? 'bg-[var(--nova-purple)] text-white' : 'text-[var(--nova-muted)] hover:text-white'}`}
          >
            Yearly <span className="ml-2 bg-[var(--nova-green)] text-white text-[10px] px-2 py-0.5 rounded-full">20% OFF</span>
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map(p => (
          <PlanCard 
            key={p.id}
            plan={p}
            billingCycle={billingCycle}
            isCurrentPlan={user?.plan_id === p.id}
            onSelect={handleSelect}
            buttonText={p.id.includes('free') ? 'Get Started' : p.id.includes('ent') ? 'Contact Us' : 'Upgrade to Pro'}
          />
        ))}
      </div>
    </div>
  );
}
