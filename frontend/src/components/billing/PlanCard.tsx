import React from 'react';
import { Check, X } from 'lucide-react';

export interface PlanData {
  id: string;
  name: string;
  price_monthly: number;
  price_yearly: number;
  features: { name: string; included: boolean }[];
}

interface PlanCardProps {
  plan: PlanData;
  isCurrentPlan?: boolean;
  billingCycle: 'monthly' | 'yearly';
  onSelect: (planId: string) => void;
  buttonText: string;
}

export const PlanCard: React.FC<PlanCardProps> = ({ plan, isCurrentPlan, billingCycle, onSelect, buttonText }) => {
  const price = billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  const isPro = plan.name.toLowerCase() === 'pro';

  return (
    <div className={`relative p-6 rounded-xl flex flex-col h-full transition-transform duration-200 hover:scale-[1.02] bg-[var(--nova-card)] border ${isCurrentPlan || isPro ? 'border-[var(--nova-purple)]' : 'border-[var(--nova-border)]'}`}>
      
      {isCurrentPlan && (
        <div className="absolute top-0 right-0 transform translate-x-2 -translate-y-3">
          <span className="bg-[var(--nova-green)] text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">Current Plan</span>
        </div>
      )}
      
      {isPro && !isCurrentPlan && (
        <div className="absolute top-0 right-0 transform translate-x-2 -translate-y-3">
          <span className="bg-gradient-to-r from-purple-500 to-[var(--nova-purple)] text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">Most Popular</span>
        </div>
      )}

      <h3 className="text-2xl font-bold uppercase tracking-wider mb-2">{plan.name}</h3>
      
      <div className="mb-6">
        <span className="text-4xl font-extrabold">₹{price}</span>
        <span className="text-[var(--nova-muted)] ml-1">/{billingCycle === 'monthly' ? 'mo' : 'yr'}</span>
      </div>

      <ul className="flex-1 space-y-3 mb-8">
        {plan.features.map((feat, idx) => (
          <li key={idx} className="flex items-start">
            {feat.included ? (
              <Check className="w-5 h-5 text-[var(--nova-green)] mr-2 flex-shrink-0" />
            ) : (
              <X className="w-5 h-5 text-[var(--nova-muted)] mr-2 flex-shrink-0" />
            )}
            <span className={feat.included ? "text-white" : "text-[var(--nova-muted)]"}>{feat.name}</span>
          </li>
        ))}
      </ul>

      <button 
        onClick={() => onSelect(plan.id)}
        disabled={isCurrentPlan}
        className={`w-full py-3 rounded-lg font-bold transition-all ${
          isCurrentPlan 
            ? 'bg-[var(--nova-border)] text-[var(--nova-muted)] cursor-not-allowed'
            : isPro 
              ? 'bg-[var(--nova-purple)] hover:brightness-110 text-white shadow-lg shadow-purple-500/20'
              : 'bg-white text-black hover:bg-gray-200'
        }`}
      >
        {isCurrentPlan ? 'Active' : buttonText}
      </button>
    </div>
  );
};
