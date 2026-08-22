"use client"

import React, { useEffect, useState } from 'react'
import { Mic, Cpu, Volume2, Activity, Zap, ShieldCheck } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface HUDProps {
  status: 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING';
  text?: string;
}

export default function HUD({ status, text }: HUDProps) {
  const [time, setTime] = useState('')

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setTime(now.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none font-mono text-cyan-400 select-none overflow-hidden">
      
      {/* ── TOP BAR ───────────────────────────────────── */}
      <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-start pointer-events-none">
        <div className="flex gap-4 items-center">
          <div>
            <h1 className="text-2xl font-bold tracking-widest text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.5)]">
              N.O.V.A. OS v5.0
            </h1>
            <div className="flex gap-4 text-[10px] text-cyan-500/70 font-mono">
              <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" /> CPU: STABLE</span>
              <span>UPLINK: ACTIVE</span>
              <span>{time}</span>
            </div>
          </div>
        </div>

        {/* Subtitles / Transcription in Top Center */}
        <div className="absolute left-1/2 -translate-x-1/2 top-0 w-full max-w-xl text-center">
            <AnimatePresence mode="wait">
              {text && (
                <motion.p 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="text-sm font-light italic text-cyan-100/90 tracking-wide leading-relaxed bg-black/20 backdrop-blur-sm p-3 rounded-lg border-x border-cyan-500/20"
                >
                  {text}
                </motion.p>
              )}
            </AnimatePresence>
        </div>

        <div className="flex flex-col items-end gap-1 text-[10px] opacity-60">
            <span>ENCRYPTION: AES-256</span>
            <span>LATENCY: 38ms</span>
        </div>
      </div>

      {/* ── CENTER HOLOGRAPHIC RINGS ──────────────────────── */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] flex items-center justify-center opacity-20 pointer-events-none">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 border-[1px] border-cyan-500/40 rounded-full"
        />
        <motion.div 
          animate={{ rotate: -360 }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          className="absolute inset-10 border-[1px] border-dashed border-cyan-400/30 rounded-full"
        />
        <motion.div 
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 4, repeat: Infinity }}
          className="absolute inset-20 border-[2px] border-cyan-500/20 rounded-full shadow-[0_0_30px_rgba(34,211,238,0.1)]"
        />
      </div>

      {/* ── SIDE STATS (Right) ───────────────────────────── */}
      <div className="absolute right-10 top-1/2 -translate-y-1/2 flex flex-col gap-10 items-end">
        <div className="flex flex-col items-end gap-2">
            <div className="text-[10px] uppercase tracking-tighter opacity-50">Neural Link</div>
            <div className="text-2xl font-light">98.4%</div>
            <div className="w-32 h-1 bg-cyan-900/50 rounded-full overflow-hidden">
                <motion.div 
                    animate={{ width: ["90%", "98%", "95%"] }}
                    transition={{ duration: 5, repeat: Infinity }}
                    className="h-full bg-cyan-400 shadow-[0_0_8px_cyan]" 
                />
            </div>
        </div>

        <div className="flex flex-col items-end gap-2">
            <div className="text-[10px] uppercase tracking-tighter opacity-50">Vocal Sync</div>
            <div className="text-2xl font-light">100%</div>
            <div className="flex gap-1">
                {[1,2,3,4,5].map(i => (
                    <div key={i} className="w-1.5 h-4 bg-cyan-400/80 rounded-sm shadow-[0_0_5px_cyan]" />
                ))}
            </div>
        </div>

        <div className="flex flex-col items-end gap-2">
            <div className="text-[10px] uppercase tracking-tighter opacity-50">System Core</div>
            <div className="flex gap-3">
                <Zap className="w-4 h-4 text-yellow-400" />
                <ShieldCheck className="w-4 h-4" />
                <Activity className="w-4 h-4 animate-pulse" />
            </div>
        </div>
      </div>

      {/* ── BOTTOM CONTROLS ──────────────────────────────── */}
      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex items-center gap-16">
        <div className={`flex flex-col items-center gap-2 transition-all duration-500 ${status === 'LISTENING' ? 'text-cyan-400 scale-110' : 'text-cyan-400/30'}`}>
            <div className={`p-4 rounded-full border ${status === 'LISTENING' ? 'border-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.4)]' : 'border-cyan-400/20'}`}>
                <Mic className="w-6 h-6" />
            </div>
            <span className="text-[10px] font-bold tracking-widest">LISTEN</span>
        </div>

        {/* Dynamic Waveform in Center */}
        <div className="flex items-end gap-1 h-12 w-48 justify-center">
            {[1,2,3,4,5,6,7,8,9,10,11,12].map(i => (
                <motion.div 
                    key={i}
                    animate={{ 
                        height: status === 'SPEAKING' ? [10, 40, 10] : 
                                status === 'LISTENING' ? [10, 25, 10] : 10 
                    }}
                    transition={{ 
                        duration: 0.5, 
                        repeat: Infinity, 
                        delay: i * 0.05 
                    }}
                    className="w-1 bg-cyan-400/60 rounded-full"
                />
            ))}
        </div>

        <div className={`flex flex-col items-center gap-2 transition-all duration-500 ${status === 'THINKING' ? 'text-cyan-400 scale-110' : 'text-cyan-400/30'}`}>
            <div className={`p-4 rounded-full border ${status === 'THINKING' ? 'border-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.4)]' : 'border-cyan-400/20'}`}>
                <Cpu className={`w-6 h-6 ${status === 'THINKING' ? 'animate-spin' : ''}`} />
            </div>
            <span className="text-[10px] font-bold tracking-widest">THINK</span>
        </div>

        <div className={`flex flex-col items-center gap-2 transition-all duration-500 ${status === 'SPEAKING' ? 'text-cyan-400 scale-110' : 'text-cyan-400/30'}`}>
            <div className={`p-4 rounded-full border ${status === 'SPEAKING' ? 'border-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.4)]' : 'border-cyan-400/20'}`}>
                <Volume2 className="w-6 h-6" />
            </div>
            <span className="text-[10px] font-bold tracking-widest">VOICE</span>
        </div>
      </div>

      {/* Decorative Corners */}
      <div className="absolute top-0 left-0 w-20 h-20 border-t-2 border-l-2 border-cyan-500/20 m-10" />
      <div className="absolute bottom-0 right-0 w-20 h-20 border-b-2 border-r-2 border-cyan-500/20 m-10" />

      {/* Scanline Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(255,0,0,0.03),rgba(0,255,0,0.01),rgba(0,0,255,0.03))] bg-[length:100%_4px,3px_100%] pointer-events-none opacity-20" />
    </div>
  )
}
