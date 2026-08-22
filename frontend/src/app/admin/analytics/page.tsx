"use client";
import React from 'react';
import { BarChart2 } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function AdminAnalyticsPage() {
  const data = [
    { name: 'Mon', API_Calls: 4000, Messages: 2400 },
    { name: 'Tue', API_Calls: 3000, Messages: 1398 },
    { name: 'Wed', API_Calls: 2000, Messages: 9800 },
    { name: 'Thu', API_Calls: 2780, Messages: 3908 },
    { name: 'Fri', API_Calls: 1890, Messages: 4800 },
    { name: 'Sat', API_Calls: 2390, Messages: 3800 },
    { name: 'Sun', API_Calls: 3490, Messages: 4300 },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold flex items-center"><BarChart2 className="w-8 h-8 mr-3 text-[#D4A017]" /> Analytics</h1>
          <p className="text-[#6B6B80] mt-1">Platform usage and metric tracking</p>
        </div>
      </div>

      <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6 h-[500px]">
        <h2 className="text-xl font-bold mb-6">Traffic Overview</h2>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2E" vertical={false} />
            <XAxis dataKey="name" stroke="#6B6B80" tick={{fill: '#6B6B80'}} />
            <YAxis stroke="#6B6B80" tick={{fill: '#6B6B80'}} />
            <Tooltip contentStyle={{ backgroundColor: '#12121A', borderColor: '#1E1E2E', color: '#fff' }} />
            <Bar dataKey="API_Calls" fill="#D4A017" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Messages" fill="#7F77DD" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
