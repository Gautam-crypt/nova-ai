"use client";
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Cpu, Activity, Database, AlertTriangle } from 'lucide-react';

const API_BASE_URL = 'http://192.168.1.130:8080';

export default function ConsolePage() {
  const [messages, setMessages] = useState<{role: 'user' | 'nova', text: string}[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/status`);
      setStatus(res.data);
    } catch (e) {
      console.error(e);
      setStatus({ status: 'offline' });
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const sendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputText.trim()) return;
    
    const userText = inputText;
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setInputText('');
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE_URL}/chat`, { message: userText });
      setMessages(prev => [...prev, { role: 'nova', text: res.data.reply }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'nova', text: "Error: Connection failed. Ensure main.py is running." }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-extrabold text-[#E8E8F0]">Command Console</h1>
        <div className={`px-4 py-2 rounded-full font-bold text-sm flex items-center ${status?.status === 'online' ? 'bg-[#1D9E75]/20 text-[#1D9E75]' : 'bg-red-500/20 text-red-500'}`}>
          <div className={`w-2 h-2 rounded-full mr-2 ${status?.status === 'online' ? 'bg-[#1D9E75] animate-pulse' : 'bg-red-500'}`}></div>
          NOVA {status?.status === 'online' ? 'ONLINE' : 'OFFLINE'}
        </div>
      </div>

      {/* Main Terminal Window */}
      <div className="flex-1 bg-[#12121A] border border-[#1E1E2E] rounded-xl flex flex-col overflow-hidden shadow-2xl relative backdrop-blur-md bg-opacity-80">
        
        {/* Terminal Header */}
        <div className="h-10 bg-[#0A0A0F] border-b border-[#1E1E2E] flex items-center px-4 space-x-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span className="text-[#6B6B80] text-xs font-mono ml-4">root@nova-core:~</span>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 font-mono">
          <div className="text-[#7F77DD] text-sm mb-8 whitespace-pre-line">
            {`Initializing NOVA Console v2.0...
[OK] ReAct Engine Loaded
[OK] OS Controller Bound
Waiting for user input...`}
          </div>
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`text-xs mb-1 ${msg.role === 'user' ? 'text-[#378ADD]' : 'text-[#7F77DD]'}`}>
                {msg.role === 'user' ? 'YOU' : 'NOVA'}
              </div>
              <div className={`max-w-[80%] p-4 rounded-xl text-sm leading-relaxed
                ${msg.role === 'user' 
                  ? 'bg-[#378ADD]/10 border border-[#378ADD]/30 text-[#E8E8F0] rounded-tr-none' 
                  : 'bg-[#1E1E2E]/50 border border-[#1E1E2E] text-[#E8E8F0] rounded-tl-none'}`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex flex-col items-start">
              <div className="text-xs mb-1 text-[#7F77DD]">NOVA</div>
              <div className="bg-[#1E1E2E]/50 border border-[#1E1E2E] p-4 rounded-xl rounded-tl-none">
                <div className="flex space-x-2 items-center">
                  <div className="w-2 h-2 bg-[#7F77DD] rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-[#7F77DD] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-[#7F77DD] rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-[#0A0A0F] border-t border-[#1E1E2E]">
          <form onSubmit={sendMessage} className="relative flex items-center">
            <span className="absolute left-4 text-[#7F77DD] font-mono">{'>'}</span>
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter command for NOVA..."
              className="w-full bg-[#12121A] border border-[#1E1E2E] text-[#E8E8F0] font-mono pl-10 pr-12 py-4 rounded-lg focus:outline-none focus:border-[#7F77DD] transition"
              disabled={loading}
            />
            <button 
              type="submit" 
              disabled={loading || !inputText.trim()}
              className="absolute right-3 p-2 bg-[#7F77DD] hover:bg-[#6860C4] text-white rounded-md disabled:opacity-50 transition"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
