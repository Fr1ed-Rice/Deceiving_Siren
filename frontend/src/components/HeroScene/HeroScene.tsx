"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Points, PointMaterial } from "@react-three/drei";
import * as THREE from "three";
import styles from "./HeroScene.module.css";

function ParticleField() {
  const ref = useRef<THREE.Points>(null);

  const particleCount = 3000;
  const positions = useMemo(() => {
    const pos = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return pos;
  }, []);

  useFrame((state) => {
    if (!ref.current) return;
    ref.current.rotation.x = state.clock.elapsedTime * 0.02;
    ref.current.rotation.y = state.clock.elapsedTime * 0.035;
  });

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#00f0ff"
        size={0.03}
        sizeAttenuation
        depthWrite={false}
        opacity={0.6}
      />
    </Points>
  );
}

function WaveGrid() {
  const ref = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!ref.current) return;
    const geo = ref.current.geometry as THREE.PlaneGeometry;
    const pos = geo.attributes.position;

    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      const wave =
        Math.sin(x * 0.5 + state.clock.elapsedTime * 0.8) * 0.3 +
        Math.sin(y * 0.3 + state.clock.elapsedTime * 0.6) * 0.2;
      pos.setZ(i, wave);
    }
    pos.needsUpdate = true;
  });

  return (
    <mesh ref={ref} rotation={[-Math.PI / 3, 0, 0]} position={[0, -3, 0]}>
      <planeGeometry args={[30, 30, 60, 60]} />
      <meshBasicMaterial
        color="#00f0ff"
        wireframe
        transparent
        opacity={0.08}
      />
    </mesh>
  );
}

export default function HeroScene() {
  return (
    <div className={styles.heroCanvas}>
      <Canvas
        camera={{ position: [0, 0, 8], fov: 60 }}
        gl={{ alpha: true, antialias: true }}
        style={{ background: "transparent" }}
      >
        <ambientLight intensity={0.2} />
        <ParticleField />
        <WaveGrid />
      </Canvas>
    </div>
  );
}
