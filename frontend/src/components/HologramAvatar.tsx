"use client"

import React, { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { useTexture, Float } from '@react-three/drei'
import * as THREE from 'three'

interface AvatarProps {
  isSpeaking: boolean;
  audioAmplitude: number;
  emotion: string;
}

export default function HologramAvatar({ isSpeaking, audioAmplitude, emotion }: AvatarProps) {
  // Load all emotional textures (Now with Solid Black Backgrounds)
  const textures = useTexture({
    neutral: '/images/nova_live.png',
    happy:   '/images/nova_live.png', 
    angry:   '/images/nova_angry.png',
    sad:     '/images/nova_sad.png',
    stressed: '/images/nova_angry.png',
    very_stressed: '/images/nova_angry.png'
  })

  const meshRef = useRef<THREE.Mesh>(null)
  const materialRef = useRef<THREE.MeshBasicMaterial>(null)

  // Current texture logic
  const currentTexture = useMemo(() => {
    return textures[emotion as keyof typeof textures] || textures.neutral
  }, [emotion, textures])

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    
    if (meshRef.current) {
      // 1. Natural floating (Mood-based speed)
      const floatSpeed = emotion === 'angry' || emotion === 'stressed' ? 3 : 1.5;
      meshRef.current.position.y = Math.sin(t * floatSpeed) * 0.12;
      
      // 2. High-Tech Jitter for intense emotions
      if (emotion === 'angry' || emotion === 'very_stressed') {
        meshRef.current.position.x = Math.sin(t * 40) * 0.015;
      } else {
        meshRef.current.position.x = 0;
      }

      // 3. Speaking Pulse & Mouth Simulation
      if (isSpeaking) {
        const pulse = 1 + (Math.sin(t * 15) * 0.015);
        meshRef.current.scale.set(pulse, pulse, 1);
        // Simulate lip-sync with slight opacity flicker
        if (materialRef.current) {
            materialRef.current.opacity = 0.8 + Math.sin(t * 25) * 0.15;
        }
      } else if (materialRef.current) {
        materialRef.current.opacity = 0.9 + Math.sin(t * 5) * 0.05;
      }
    }
  });

  return (
    <group>
      {/* ── Main Hologram Plane ── */}
      <Float speed={2} rotationIntensity={0.3} floatIntensity={0.8}>
        <mesh ref={meshRef} position={[0, 0, 0]}>
          <planeGeometry args={[3, 4]} />
          <meshBasicMaterial 
            ref={materialRef}
            map={currentTexture} 
            transparent 
            opacity={1.0} 
            side={THREE.DoubleSide}
            blending={THREE.AdditiveBlending} // THE MAGIC: Makes black background transparent + Glows!
            depthWrite={false}
          />
        </mesh>
      </Float>

      {/* ── Outer Aura (Reactive to emotion) ── */}
      <mesh position={[0, 0, -0.1]}>
        <planeGeometry args={[3.5, 4.5]} />
        <meshBasicMaterial 
            color={emotion === 'angry' || emotion === 'stressed' ? '#ff0000' : '#22d3ee'} 
            transparent 
            opacity={0.1} 
            blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* ── Base Pedestal Rings ── */}
      <group position={[0, -2.2, 0]}>
          <mesh rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[1.6, 1.62, 64]} />
            <meshBasicMaterial color="#22d3ee" transparent opacity={0.4} />
          </mesh>
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.1, 0]}>
            <ringGeometry args={[1.4, 1.45, 64]} />
            <meshBasicMaterial color="#22d3ee" transparent opacity={0.2} />
          </mesh>
      </group>
    </group>
  )
}
