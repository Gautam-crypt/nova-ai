import React from 'react';

interface PlanBadgeProps {
  plan: 'free' | 'pro' | 'enterprise';
}

export const PlanBadge: React.FC<PlanBadgeProps> = ({ plan }) => {
  const normalized = plan.toLowerCase();
  
  const colors: Record<string, string> = {
    free: 'bg-gray-800 text-gray-300 border-gray-600',
    pro: 'bg-[var(--nova-purple)] text-white border-purple-400',
    enterprise: 'bg-[var(--nova-gold)] text-black border-yellow-500',
  };

  const style = colors[normalized] || colors.free;

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${style}`}>
      {plan}
    </span>
  );
};
