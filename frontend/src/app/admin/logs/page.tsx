"use client";
import React, { useEffect, useState } from 'react';
import { FileText, RefreshCw, Terminal } from 'lucide-react';

export default function AdminLogsPage() {
  const [logs, setLogs] = useState<string[]>([
    "[2026-06-09 10:12:45] INFO: Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)",
    "[2026-06-09 10:13:12] INFO: 127.0.0.1:54322 - 'POST /auth/login HTTP/1.1' 200 OK",
    "[2026-06-09 10:13:15] INFO: 127.0.0.1:54325 - 'GET /users/me HTTP/1.1' 200 OK",
    "[2026-06-09 10:15:02] WARNING: Ollama model gemma3:4b response time > 5s",
    "[2026-06-09 10:16:30] INFO: Background task 'FindingScan' completed successfully."
  ]);

  return (
    <div className="max-w-7xl mx-auto space-y-6 h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-3xl font-extrabold flex items-center"><FileText className="w-8 h-8 mr-3 text-[#D4A017]" /> System Logs</h1>
          <p className="text-[#6B6B80] mt-1">Live streaming terminal output</p>
        </div>
        <button className="bg-[#1E1E2E] hover:bg-[#2A2A3A] text-white px-4 py-2 rounded-lg flex items-center transition">
          <RefreshCw className="w-4 h-4 mr-2" /> Refresh
        </button>
      </div>

      <div className="flex-1 bg-[#050505] border border-[#1E1E2E] rounded-xl p-6 font-mono text-sm overflow-y-auto">
        <div className="flex items-center text-[#6B6B80] mb-4 border-b border-[#1E1E2E] pb-4">
          <Terminal className="w-4 h-4 mr-2" /> <span>Connected to production stream...</span>
        </div>
        {logs.map((log, i) => (
          <div key={i} className={`mb-1 ${log.includes('WARNING') ? 'text-amber-400' : log.includes('ERROR') ? 'text-red-400' : 'text-[#A3A3A3]'}`}>
            {log}
          </div>
        ))}
      </div>
    </div>
  );
}
