"use client";
import React from 'react';
import { Settings, Save, Server, Database, BrainCircuit } from 'lucide-react';

export default function AdminSettingsPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold flex items-center"><Settings className="w-8 h-8 mr-3 text-[#D4A017]" /> Platform Settings</h1>
          <p className="text-[#6B6B80] mt-1">Configure global NOVA configurations</p>
        </div>
        <button className="bg-[#D4A017] hover:brightness-110 text-black font-bold py-2 px-6 rounded-lg shadow-lg flex items-center transition">
          <Save className="w-5 h-5 mr-2" /> Save Changes
        </button>
      </div>

      <div className="space-y-6">
        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6">
          <h2 className="text-lg font-bold mb-4 flex items-center"><BrainCircuit className="w-5 h-5 mr-2 text-[#7F77DD]" /> Inference Engine</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[#6B6B80] mb-1">Ollama Host URL</label>
              <input type="text" defaultValue="http://localhost:11434" className="w-full bg-[#0A0A0F] border border-[#1E1E2E] rounded-lg px-4 py-2 focus:border-[#D4A017] outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#6B6B80] mb-1">Default Model</label>
              <input type="text" defaultValue="gemma3:4b" className="w-full bg-[#0A0A0F] border border-[#1E1E2E] rounded-lg px-4 py-2 focus:border-[#D4A017] outline-none" />
            </div>
            <div className="flex items-center justify-between py-2">
              <div>
                <p className="font-medium">Background Agent Scanning</p>
                <p className="text-sm text-[#6B6B80]">Allow agents to proactively monitor context.</p>
              </div>
              <input type="checkbox" defaultChecked className="w-5 h-5 accent-[#D4A017]" />
            </div>
          </div>
        </div>

        <div className="bg-[#12121A] border border-[#1E1E2E] rounded-xl p-6">
          <h2 className="text-lg font-bold mb-4 flex items-center"><Database className="w-5 h-5 mr-2 text-[#378ADD]" /> Database & Memory</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[#6B6B80] mb-1">ChromaDB Path</label>
              <input type="text" defaultValue="./data/chroma" className="w-full bg-[#0A0A0F] border border-[#1E1E2E] rounded-lg px-4 py-2 focus:border-[#D4A017] outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#6B6B80] mb-1">Max Retained Memories per User</label>
              <input type="number" defaultValue={5000} className="w-full bg-[#0A0A0F] border border-[#1E1E2E] rounded-lg px-4 py-2 focus:border-[#D4A017] outline-none" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
