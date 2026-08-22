"use client"

import React, { useState, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment, ContactShadows, Stars } from '@react-three/drei'
import VoiceVisualizer from '@/components/VoiceVisualizer'
import HUD from '@/components/HUD'
import Link from 'next/link'

export default function JarvisApp() {
  const [status, setStatus] = useState<'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING'>('IDLE')
  const [emotion, setEmotion] = useState('neutral')
  const [currentText, setCurrentText] = useState('')
  const [amplitude, setAmplitude] = useState(0)

  // WebSocket Connection
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws')

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      console.log("[JARVIS] Event:", message)

      switch (message.type) {
        case 'STATUS_UPDATE':
          setStatus(message.data.status)
          break
        case 'SPEECH_START':
          setStatus('SPEAKING')
          setCurrentText(message.data.text)
          break
        case 'SPEECH_END':
          setStatus('IDLE')
          break
        case 'AUDIO_AMPLITUDE':
          setAmplitude(message.data.value)
          break
        case 'EMOTION_UPDATE':
          setEmotion(message.data.emotion)
          break
      }
    }

    return () => ws.close()
  }, [])

  return (
    <main className="relative w-full h-screen bg-[#020617] overflow-hidden">
      
      {/* ── TOP NAVIGATION ────────────────────────────────── */}
      <header className="absolute top-0 w-full z-50 p-6 flex justify-between items-center bg-gradient-to-b from-black/80 to-transparent">
        <div className="text-white font-extrabold text-2xl tracking-widest flex items-center">
          <span className="text-[#22d3ee] mr-2">●</span> NOVA
        </div>
        <nav className="flex space-x-6">
          <Link href="/pricing" className="text-gray-300 hover:text-white font-bold transition">Pricing & Plans</Link>
          <Link href="/login" className="text-gray-300 hover:text-white font-bold transition">Login</Link>
          <Link href="/dashboard/billing" className="bg-[#22d3ee] text-black px-4 py-2 rounded-lg font-bold hover:brightness-110 transition">Dashboard</Link>
        </nav>
      </header>

      {/* ── 3D SCENE ────────────────────────────────────── */}
      <div className="absolute inset-0">
        <Canvas shadows camera={{ position: [0, 0, 5], fov: 50 }}>
          <color attach="background" args={['#020617']} />
          <fog attach="fog" args={['#020617', 2, 10]} />
          
          <ambientLight intensity={2} />
          <pointLight position={[10, 10, 10]} intensity={10} color="#22d3ee" />
          <pointLight position={[-10, 10, 10]} intensity={5} color="#3b82f6" />
          <spotLight 
            position={[0, 10, 10]} 
            angle={0.15} 
            penumbra={1} 
            intensity={20} 
            castShadow 
          />
          
          <React.Suspense fallback={<mesh position={[0,0,0]}><sphereGeometry args={[0.5, 32, 32]} /><meshStandardMaterial color="#22d3ee" wireframe /></mesh>}>
            <VoiceVisualizer 
              isSpeaking={status === 'SPEAKING'} 
              audioAmplitude={amplitude} 
              emotion={emotion}
            />
            <ContactShadows opacity={0.4} scale={10} blur={2.5} far={10} resolution={256} color="#000000" />
            <Environment preset="night" />
          </React.Suspense>

          {/* Cinematic Background Particles */}
          <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
          
          <OrbitControls 
            enablePan={false} 
            enableZoom={false}
            minPolarAngle={Math.PI / 2.2}
            maxPolarAngle={Math.PI / 2.2}
          />
        </Canvas>
      </div>

      {/* ── UI OVERLAY ──────────────────────────────────── */}
      <HUD status={status} text={currentText} />

      {/* Cinematic Vignette */}
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.6)_100%)] shadow-[inset_0_0_100px_rgba(34,211,238,0.05)]" />
      
      {/* Dynamic Scanline/Grain Effect */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
    </main>
  )
}
