"use client";
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, ShieldAlert, Activity, RefreshCw } from 'lucide-react';

const API_BASE_URL = 'http://192.168.1.130:8080';

export default function SecurityPage() {
  const [findings, setFindings] = useState<any[]>([]);
  const [status, setStatus] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    setRefreshing(true);
    try {
      const fRes = await axios.get(`${API_BASE_URL}/findings`);
      setFindings(fRes.data.findings || []);
      const sRes = await axios.get(`${API_BASE_URL}/status`);
      setStatus(sRes.data);
    } catch (e) {
      console.error(e);
    }
    setRefreshing(false);
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Auto-refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const highPriority = findings.filter(f => f.priority === 3);
  const isSecure = highPriority.length === 0;

  return (
    <div className="flex flex-col h-full space-y-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-[#E8E8F0] flex items-center">
            <Shield className="w-8 h-8 mr-3 text-[#7F77DD]" />
            KAVACH Dashboard
          </h1>
          <p className="text-[#6B6B80] mt-2">Live monitoring of system integrity and threats.</p>
        </div>
        <button 
          onClick={loadData}
          className="flex items-center space-x-2 bg-[#1E1E2E] hover:bg-[#2A2A3C] border border-[#333] px-4 py-2 rounded-lg transition"
        >
          <RefreshCw className={`w-4 h-4 text-[#E8E8F0] ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Main Status Panel */}
      <div className={`p-8 rounded-2xl border flex items-center justify-between transition-colors
        ${isSecure 
          ? 'bg-[#1D9E75]/10 border-[#1D9E75]/30' 
          : 'bg-red-500/10 border-red-500/30'}`}>
        <div className="flex items-center space-x-6">
          <div className={`p-4 rounded-full ${isSecure ? 'bg-[#1D9E75]/20 text-[#1D9E75]' : 'bg-red-500/20 text-red-500'}`}>
            {isSecure ? <Shield className="w-12 h-12" /> : <ShieldAlert className="w-12 h-12 animate-pulse" />}
          </div>
          <div>
            <h2 className={`text-2xl font-bold ${isSecure ? 'text-[#1D9E75]' : 'text-red-500'}`}>
              {isSecure ? 'System Secure' : 'Threats Detected'}
            </h2>
            <p className="text-[#E8E8F0] mt-1">
              {isSecure 
                ? 'Network Sentinel and Process Guardian are running smoothly.'
                : `${highPriority.length} high-priority alerts require your immediate attention.`}
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-[#6B6B80] text-sm font-bold uppercase tracking-wider">Agents Status</div>
          <div className="flex items-center mt-2 space-x-2 justify-end">
            <span className="w-3 h-3 bg-[#1D9E75] rounded-full animate-pulse"></span>
            <span className="text-[#E8E8F0] font-mono">ONLINE</span>
          </div>
        </div>
      </div>

      {/* Alerts Grid */}
      <div>
        <h3 className="text-xl font-bold text-[#E8E8F0] mb-6 flex items-center">
          <Activity className="w-5 h-5 mr-2 text-[#7F77DD]" /> 
          Live Findings ({findings.length})
        </h3>
        
        {findings.length === 0 ? (
          <div className="p-12 border border-dashed border-[#1E1E2E] rounded-xl flex flex-col items-center justify-center text-center">
            <Shield className="w-12 h-12 text-[#6B6B80] mb-4 opacity-50" />
            <p className="text-[#6B6B80] text-lg">No findings in the queue. Everything is quiet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {findings.map((finding, idx) => (
              <div 
                key={idx} 
                className="bg-[#12121A] border border-[#1E1E2E] p-6 rounded-xl relative overflow-hidden group hover:border-[#7F77DD] transition-colors"
              >
                {/* Accent line for priority */}
                <div className={`absolute top-0 left-0 w-1 h-full 
                  ${finding.priority === 3 ? 'bg-red-500' : 
                    finding.priority === 2 ? 'bg-yellow-500' : 'bg-blue-500'}`}>
                </div>
                
                <div className="flex justify-between items-start mb-4">
                  <span className={`px-3 py-1 text-xs font-bold rounded-full
                    ${finding.priority === 3 ? 'bg-red-500/20 text-red-500' : 
                      finding.priority === 2 ? 'bg-yellow-500/20 text-yellow-500' : 'bg-blue-500/20 text-blue-500'}`}>
                    {finding.priority === 3 ? 'HIGH' : finding.priority === 2 ? 'MEDIUM' : 'LOW'}
                  </span>
                  <span className="text-[#6B6B80] text-xs font-mono">
                    {new Date(finding.timestamp * 1000).toLocaleTimeString()}
                  </span>
                </div>
                
                <h4 className="text-lg font-bold text-[#E8E8F0] mb-2">{finding.title}</h4>
                <p className="text-[#6B6B80] text-sm leading-relaxed">{finding.detail}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
