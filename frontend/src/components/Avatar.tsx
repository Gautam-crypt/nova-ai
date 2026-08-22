"use client"

import React, { useEffect, useRef, useState, useMemo } from 'react'
import { useGLTF, useAnimations } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface AvatarProps {
  isSpeaking: boolean;
  audioAmplitude: number;
  emotion: string;
}

export default function Avatar({ isSpeaking, audioAmplitude, emotion }: AvatarProps) {
  const modelUrl = '/models/avatar.glb';
  const { scene, animations } = useGLTF(modelUrl) as any;
  const { actions } = useAnimations(animations, scene);
  const group = useRef<THREE.Group>(null)
  
  // 1. Auto-Fit Logic (Ensures visibility regardless of model's original scale)
  useEffect(() => {
    if (scene) {
      const box = new THREE.Box3().setFromObject(scene);
      const size = box.getSize(new THREE.Vector3());
      const center = box.getCenter(new THREE.Vector3());
      
      // Rescale to a standard size (roughly 2 units tall)
      const maxDim = Math.max(size.x, size.y, size.z);
      const f = 2.0 / maxDim;
      scene.scale.set(f, f, f);
      
      // Center the model
      scene.position.x = -center.x * f;
      scene.position.y = -center.y * f - 0.5; // Move slightly down
      scene.position.z = -center.z * f;
    }
  }, [scene]);

  // 2. Animation Handling
  useEffect(() => {
    if (actions) {
      const clips = Object.keys(actions);
      const idleClip = actions['idle'] || actions['Idle'] || actions[clips[0]];
      const talkClip = actions['talk'] || actions['Talking'] || actions['Talk'];

      if (idleClip) idleClip.reset().fadeIn(0.5).play();

      if (isSpeaking && talkClip) {
        talkClip.reset().fadeIn(0.2).play();
        if (idleClip) idleClip.fadeOut(0.2);
      } else if (talkClip) {
        talkClip.fadeOut(0.5);
        if (idleClip) idleClip.reset().fadeIn(0.5).play();
      }
    }
  }, [actions, isSpeaking]);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (group.current) {
      group.current.rotation.y = Math.sin(t * 0.2) * 0.05;
    }

    scene.traverse((child: any) => {
      if (child.isMesh && child.morphTargetInfluences) {
        // Mouth movement sync
        if (isSpeaking) {
          const mouthOpen = child.morphTargetDictionary['mouthOpen'] || child.morphTargetDictionary['viseme_aa'] || child.morphTargetDictionary['MouthOpen'];
          if (mouthOpen !== undefined) {
             child.morphTargetInfluences[mouthOpen] = 0.2 + Math.abs(Math.sin(t * 15)) * 0.4;
          }
        }
      }
    });
  });

  return (
    <group ref={group}>
      {/* ── Model ── */}
      <primitive object={scene} />
      
      {/* ── Debug Marker (Remove after seeing NOVA) ── */}
      <mesh position={[0, 0, -2]}>
        <sphereGeometry args={[0.1, 32, 32]} />
        <meshStandardMaterial color="#22d3ee" emissive="#22d3ee" emissiveIntensity={2} />
      </mesh>
    </group>
  )
}
