import React from 'react';

interface UsageBarProps {
  current: number;
  limit: number;
  label: string;
}

export const UsageBar: React.FC<UsageBarProps> = ({ current, limit, label }) => {
  if (limit === -1) {
    return (
      <div className="w-full">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-[var(--nova-muted)]">{label}</span>
          <span className="font-semibold">Unlimited</span>
        </div>
        <div className="w-full bg-[var(--nova-border)] rounded-full h-2.5">
          <div className="bg-[var(--nova-green)] h-2.5 rounded-full" style={{ width: '100%' }}></div>
        </div>
      </div>
    );
  }

  const percent = Math.min((current / limit) * 100, 100);
  
  let colorClass = "bg-[var(--nova-green)]";
  if (percent > 60 && percent <= 80) colorClass = "bg-[var(--nova-amber)]";
  else if (percent > 80) colorClass = "bg-[var(--nova-red)]";

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-[var(--nova-muted)]">{label}</span>
        <span className="font-semibold">{current} / {limit}</span>
      </div>
      <div className="w-full bg-[var(--nova-border)] rounded-full h-2.5">
        <div className={`${colorClass} h-2.5 rounded-full transition-all duration-300`} style={{ width: `${percent}%` }}></div>
      </div>
    </div>
  );
};
