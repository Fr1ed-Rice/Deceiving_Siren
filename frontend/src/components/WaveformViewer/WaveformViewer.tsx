"use client";

import { useRef, useEffect, useState, useCallback } from "react";
import styles from "./WaveformViewer.module.css";

interface WaveformViewerProps {
  audioUrl?: string;
  audioFile?: File | null;
  label?: string;
}

export default function WaveformViewer({
  audioUrl,
  audioFile,
  label = "Waveform",
}: WaveformViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<any>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState("0:00");
  const [duration, setDuration] = useState("0:00");
  const [loading, setLoading] = useState(false);

  const formatTime = (seconds: number) => {
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min}:${sec.toString().padStart(2, "0")}`;
  };

  const initWavesurfer = useCallback(async () => {
    if (!containerRef.current) return;

    // Dynamically import wavesurfer.js (client-side only)
    const WaveSurfer = (await import("wavesurfer.js")).default;

    // Destroy previous instance
    if (wavesurferRef.current) {
      wavesurferRef.current.destroy();
    }

    const ws = WaveSurfer.create({
      container: containerRef.current,
      waveColor: "rgba(0, 240, 255, 0.4)",
      progressColor: "#00f0ff",
      cursorColor: "#ff00aa",
      cursorWidth: 2,
      barWidth: 2,
      barGap: 1,
      barRadius: 2,
      height: 100,
      normalize: true,
      backend: "WebAudio",
    });

    ws.on("ready", () => {
      setDuration(formatTime(ws.getDuration()));
      setLoading(false);
    });

    ws.on("audioprocess", () => {
      setCurrentTime(formatTime(ws.getCurrentTime()));
    });

    ws.on("play", () => setIsPlaying(true));
    ws.on("pause", () => setIsPlaying(false));
    ws.on("finish", () => setIsPlaying(false));

    wavesurferRef.current = ws;
    return ws;
  }, []);

  useEffect(() => {
    const loadAudio = async () => {
      if (!audioUrl && !audioFile) return;

      setLoading(true);
      const ws = await initWavesurfer();
      if (!ws) return;

      if (audioFile) {
        const url = URL.createObjectURL(audioFile);
        ws.load(url);
      } else if (audioUrl) {
        ws.load(audioUrl);
      }
    };

    loadAudio();

    return () => {
      if (wavesurferRef.current) {
        wavesurferRef.current.destroy();
        wavesurferRef.current = null;
      }
    };
  }, [audioUrl, audioFile, initWavesurfer]);

  const togglePlay = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause();
    }
  };

  if (!audioUrl && !audioFile) {
    return null;
  }

  return (
    <div className={styles.container}>
      <span className={styles.label}>{label}</span>

      {loading && (
        <div className={styles.loading}>Loading waveform...</div>
      )}

      <div
        ref={containerRef}
        className={styles.waveform}
        style={{ display: loading ? "none" : "block" }}
      />

      {!loading && (
        <div className={styles.controls}>
          <button className={styles.playBtn} onClick={togglePlay} type="button">
            {isPlaying ? "⏸ Pause" : "▶ Play"}
          </button>
          <span className={styles.time}>
            {currentTime} / {duration}
          </span>
        </div>
      )}
    </div>
  );
}
