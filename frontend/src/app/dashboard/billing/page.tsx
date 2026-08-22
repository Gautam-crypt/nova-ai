"use client";
import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { CreditCard, ExternalLink, AlertTriangle } from 'lucide-react';
import { PlanBadge } from '@/components/billing/PlanBadge';
import { UsageBar } from '@/components/billing/UsageBar';
import { InvoiceRow, InvoiceData } from '@/components/billing/InvoiceRow';
import { ConfirmModal } from '@/components/billing/ConfirmModal';
import { useAuthStore } from '@/stores/authStore';
import { billingAPI, userAPI } from '@/api/client';

function BillingDashboardContent() {
  const { user } = useAuthStore();
  const searchParams = useSearchParams();
  const [usage, setUsage] = useState({ current: 0, limit: 50 });
  const [invoices, setInvoices] = useState<InvoiceData[]>([]);
  const [isCancelModalOpen, setCancelModalOpen] = useState(false);
  
  useEffect(() => {
    // Fetch real usage
    userAPI.getUsage().then(res => setUsage(res.data)).catch(() => {
      // Mock fallback
      setUsage({ current: 12, limit: user?.plan_id?.includes('pro') ? 500 : user?.plan_id?.includes('ent') ? -1 : 50 });
    });

    // Fetch invoices
    billingAPI.getInvoices().then(res => setInvoices(res.data)).catch(() => {
      // Mock fallback
      setInvoices([
        { id: 'inv_1', date: '12 May 2026', amount: 499, status: 'paid', url: '#' },
        { id: 'inv_2', date: '12 Apr 2026', amount: 499, status: 'paid', url: '#' }
      ]);
    });
  }, [user]);

  const handleCancelPlan = async () => {
    try {
      await billingAPI.cancel();
      setCancelModalOpen(false);
      alert('Plan cancelled. Access continues until end of billing cycle.');
    } catch (err) {
      alert('Failed to cancel plan.');
    }
  };

  const handlePortal = async () => {
    try {
      const res = await billingAPI.getPortal();
      if (res.data?.url) window.location.href = res.data.url;
      else alert('Portal not configured in beta mode.');
    } catch (err) {
      alert('Failed to open billing portal.');
    }
  };

  const isFree = user?.plan_id?.includes('free') || !user?.plan_id;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {searchParams.get('success') && (
        <div className="bg-[var(--nova-green)] text-white p-4 rounded-lg shadow-lg flex items-center mb-6">
          <CreditCard className="w-5 h-5 mr-2" />
          Payment successful! Your NOVA plan has been upgraded.
        </div>
      )}

      <h1 className="text-3xl font-extrabold mb-8">Billing & Usage</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Current Plan Card */}
        <div className="bg-[var(--nova-card)] border border-[var(--nova-border)] rounded-xl p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-[var(--nova-muted)] text-sm uppercase tracking-wider mb-2">Current Plan</h2>
              <PlanBadge plan={isFree ? 'free' : user?.plan_id?.includes('ent') ? 'enterprise' : 'pro'} />
            </div>
            {!isFree && (
              <div className="text-right">
                <span className="text-[var(--nova-muted)] text-sm">Next billing date</span>
                <p className="font-bold">12 Jun 2026</p>
              </div>
            )}
          </div>
          
          <div className="flex space-x-3 mt-8">
            <Link href="/pricing" className="flex-1 bg-[var(--nova-purple)] hover:brightness-110 text-white text-center py-2 rounded-lg font-bold transition">
              Upgrade Plan
            </Link>
            {!isFree && (
              <button onClick={() => setCancelModalOpen(true)} className="flex-1 bg-transparent border border-[var(--nova-border)] hover:bg-[var(--nova-bg)] text-[var(--nova-muted)] py-2 rounded-lg font-bold transition">
                Cancel
              </button>
            )}
          </div>
        </div>

        {/* Usage Card */}
        <div className="bg-[var(--nova-card)] border border-[var(--nova-border)] rounded-xl p-6">
          <h2 className="text-[var(--nova-muted)] text-sm uppercase tracking-wider mb-6">Usage Today</h2>
          <UsageBar current={usage.current} limit={usage.limit} label="Messages Sent" />
          <div className="mt-6 flex justify-between text-sm text-[var(--nova-muted)]">
            <span>Messages this month: <strong className="text-white">342</strong></span>
            <span>Resets in 6h 23m</span>
          </div>
        </div>
      </div>

      {/* Payment Method */}
      <div className="bg-[var(--nova-card)] border border-[var(--nova-border)] rounded-xl p-6 flex justify-between items-center">
        <div>
          <h3 className="font-bold mb-1">Payment Methods</h3>
          <p className="text-[var(--nova-muted)] text-sm">Manage your cards and billing info securely via Stripe.</p>
        </div>
        <button onClick={handlePortal} className="flex items-center px-4 py-2 bg-[var(--nova-bg)] border border-[var(--nova-border)] hover:bg-gray-800 rounded-lg transition">
          <ExternalLink className="w-4 h-4 mr-2" />
          Manage Portal
        </button>
      </div>

      {/* Invoices */}
      <div className="bg-[var(--nova-card)] border border-[var(--nova-border)] rounded-xl overflow-hidden">
        <div className="p-6 border-b border-[var(--nova-border)]">
          <h3 className="font-bold">Billing History</h3>
        </div>
        <table className="w-full text-left">
          <thead className="bg-[#0A0A0F] text-[var(--nova-muted)] text-xs uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4 font-medium">Date</th>
              <th className="py-3 px-4 font-medium">Amount</th>
              <th className="py-3 px-4 font-medium">Status</th>
              <th className="py-3 px-4 font-medium text-right">Invoice</th>
            </tr>
          </thead>
          <tbody>
            {invoices.length > 0 ? (
              invoices.map(inv => <InvoiceRow key={inv.id} invoice={inv} />)
            ) : (
              <tr><td colSpan={4} className="py-8 text-center text-[var(--nova-muted)]">No invoices found.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Danger Zone */}
      {!isFree && (
        <div className="mt-12 border border-[var(--nova-red)] rounded-xl p-6 bg-red-900/10">
          <h3 className="text-[var(--nova-red)] font-bold flex items-center mb-2">
            <AlertTriangle className="w-5 h-5 mr-2" />
            Danger Zone
          </h3>
          <p className="text-[var(--nova-muted)] text-sm mb-4">Cancelling your subscription will downgrade you to the Free plan at the end of your current billing cycle. You will lose access to memory, agents, and higher usage limits.</p>
          <button onClick={() => setCancelModalOpen(true)} className="px-4 py-2 bg-[var(--nova-red)] hover:brightness-110 text-white rounded-lg font-bold transition">
            Cancel Subscription
          </button>
        </div>
      )}

      <ConfirmModal 
        isOpen={isCancelModalOpen}
        title="Cancel Subscription"
        message="Are you sure you want to cancel your NOVA Pro subscription? You will retain access until the end of the current billing period (12 Jun 2026)."
        onConfirm={handleCancelPlan}
        onCancel={() => setCancelModalOpen(false)}
        danger
      />
    </div>
  );
}
export default function BillingDashboard() {
  return (
    <React.Suspense fallback={<div className="p-8 text-center text-[var(--nova-muted)]">Loading billing...</div>}>
      <BillingDashboardContent />
    </React.Suspense>
  );
}
