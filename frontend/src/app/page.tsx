"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import styles from "./page.module.css";
import CyberCard from "@/components/CyberCard/CyberCard";
import NeonButton from "@/components/NeonButton/NeonButton";

// Dynamic import for WebGL (no SSR)
const HeroScene = dynamic(
  () => import("@/components/HeroScene/HeroScene"),
  { ssr: false }
);

const features = [
  {
    icon: "🎵",
    title: "LSB Audio Steganography",
    desc: "Hide any file inside audio using Least Significant Bit encoding. The human ear can't detect the changes — your secret rides the soundwave.",
    variant: "default" as const,
  },
  {
    icon: "📊",
    title: "Spectrogram Embedding",
    desc: "Encode images and data into the frequency domain. Hidden content becomes visible only when viewing the spectrogram — invisible to the ear.",
    variant: "magenta" as const,
  },
  {
    icon: "🎬",
    title: "Video Steganography",
    desc: "Extract the audio track from any video, embed your payload, and remux it back. The video plays normally — the secret lives in the sound.",
    variant: "green" as const,
  },
  {
    icon: "📁",
    title: "Any File Format",
    desc: "Hide text, images, PDFs, archives — any file format can be embedded. Supports MP3, WAV, FLAC, OGG, MP4, AVI, MKV, and more.",
    variant: "default" as const,
  },
  {
    icon: "🔐",
    title: "Lossless Preservation",
    desc: "Output as WAV or FLAC to preserve your hidden data perfectly. Lossy formats (MP3, OGG) available with clear warnings.",
    variant: "magenta" as const,
  },
  {
    icon: "🖥️",
    title: "Real-time Visualization",
    desc: "Preview waveforms and spectrograms in-browser with WebGL-powered visualizations. See your data before and after encoding.",
    variant: "green" as const,
  },
];

export default function HomePage() {
  return (
    <>
      {/* Hero */}
      <section className={styles.hero}>
        <HeroScene />
        <div className={styles.heroContent}>
          <div className={styles.tagline}>
            Audio & Video Steganography Platform
          </div>
          <h1 className={styles.title}>
            <span className={styles.titleAccent}>Deceiving Siren</span>
            <br />
            What you hear is not what it seems
          </h1>
          <p className={styles.subtitle}>
            Hide any file inside audio and video data using LSB encoding
            and spectrogram embedding. Drag, drop, encode — your secrets
            travel as sound.
          </p>
          <div className={styles.actions}>
            <Link href="/encode">
              <NeonButton variant="primary" size="lg" icon="🔒">
                Encode Data
              </NeonButton>
            </Link>
            <Link href="/decode">
              <NeonButton variant="magenta" size="lg" icon="🔓">
                Decode Data
              </NeonButton>
            </Link>
            <Link href="/spectrogram">
              <NeonButton variant="green" size="lg" icon="📊">
                Spectrogram
              </NeonButton>
            </Link>
          </div>
        </div>
      </section>

      {/* Status Bar */}
      <div className={styles.statusBar}>
        <span className={styles.statusItem}>
          <span className="status-dot status-dot--live" />
          System Online
        </span>
        <span className={styles.statusItem}>⚡ 80MB Upload Limit</span>
        <span className={styles.statusItem}>🎵 LSB + Spectrogram Engines</span>
        <span className={styles.statusItem}>🎬 Video Support Active</span>
        <span className={styles.statusItem}>📊 Real-time Visualization</span>
      </div>

      {/* Features */}
      <section className={styles.features}>
        <h2 className={styles.featuresTitle}>⚙ Capabilities</h2>
        <div className={styles.featuresGrid}>
          {features.map((feat, i) => (
            <CyberCard key={i} icon={feat.icon} title={feat.title} variant={feat.variant}>
              <p className={styles.featureDesc}>{feat.desc}</p>
            </CyberCard>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <span className={styles.footerAccent}>🧜‍♀️ Deceiving Siren</span>
        {" "}— Audio & Video Steganography Platform
      </footer>
    </>
  );
}
