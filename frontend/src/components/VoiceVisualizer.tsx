"use client"
import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface VoiceVisualizerProps {
  isSpeaking: boolean
  audioAmplitude: number
  emotion: string
}

export default function VoiceVisualizer({ isSpeaking, audioAmplitude, emotion }: VoiceVisualizerProps) {
  const meshRef = useRef<THREE.Mesh>(null)
  
  // Choose color based on emotion
  let color = '#22d3ee' // Default cyan
  if (emotion === 'happy') color = '#10b981' // Green
  else if (emotion === 'sad') color = '#3b82f6' // Blue
  else if (emotion === 'stressed') color = '#ef4444' // Red
  else if (emotion === 'excited') color = '#f59e0b' // Yellow/Orange
  
  const targetScale = isSpeaking ? 1 + (audioAmplitude * 2) : 1

  useFrame((state, delta) => {
    if (meshRef.current) {
      // Rotate slowly over time
      meshRef.current.rotation.x += delta * 0.5
      meshRef.current.rotation.y += delta * 0.5
      
      // Interpolate scale for smooth pulsing
      meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), delta * 10)
    }
  })

  return (
    <mesh ref={meshRef} position={[0, 0, 0]}>
      <sphereGeometry args={[1.5, 64, 64]} />
      <meshStandardMaterial 
        color={color} 
        wireframe={true} 
        emissive={color} 
        emissiveIntensity={isSpeaking ? 0.8 : 0.2} 
      />
    </mesh>
  )
}
