import React from 'react';
import { Download } from 'lucide-react';

export interface InvoiceData {
  id: string;
  date: string;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
  url: string;
}

interface InvoiceRowProps {
  invoice: InvoiceData;
}

export const InvoiceRow: React.FC<InvoiceRowProps> = ({ invoice }) => {
  const statusColors = {
    paid: 'bg-green-900 text-green-300',
    pending: 'bg-amber-900 text-amber-300',
    failed: 'bg-red-900 text-red-300',
  };

  return (
    <tr className="border-b border-[var(--nova-border)] hover:bg-[var(--nova-bg)] transition">
      <td className="py-4 px-4 text-sm">{invoice.date}</td>
      <td className="py-4 px-4 font-mono font-bold">₹{invoice.amount}</td>
      <td className="py-4 px-4">
        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${statusColors[invoice.status]}`}>
          {invoice.status}
        </span>
      </td>
      <td className="py-4 px-4 text-right">
        {invoice.url ? (
          <a href={invoice.url} target="_blank" rel="noreferrer" className="inline-flex items-center text-[var(--nova-blue)] hover:text-blue-400">
            <Download className="w-4 h-4 mr-1" /> PDF
          </a>
        ) : (
          <span className="text-[var(--nova-muted)] text-sm">N/A</span>
        )}
      </td>
    </tr>
  );
};
