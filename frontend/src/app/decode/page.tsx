"use client";

import { useState } from "react";
import Link from "next/link";
import styles from "../encode/page.module.css";
import DropZone from "@/components/DropZone/DropZone";
import NeonButton from "@/components/NeonButton/NeonButton";
import WaveformViewer from "@/components/WaveformViewer/WaveformViewer";
import { useApi, downloadBlob } from "@/hooks/useApi";
import { decodeLSB, decodeVideo } from "@/lib/api";

type DecodeMode = "audio" | "video";

export default function DecodePage() {
  const [mode, setMode] = useState<DecodeMode>("audio");
  const [stegoFile, setStegoFile] = useState<File | null>(null);
  const { loading, error, data, progress, execute, reset } = useApi<Blob>();

  const canDecode = stegoFile && !loading;

  const handleDecode = async () => {
    if (!stegoFile) return;

    const blob = await execute((onProgress) => {
      if (mode === "video") {
        return decodeVideo({ video: stegoFile, method: "lsb", onProgress });
      }
      return decodeLSB({ audio: stegoFile, onProgress });
    });

    if (blob) {
      // Try to determine filename from content-disposition or use default
      downloadBlob(blob, "extracted_file");
    }
  };

  const handleReset = () => {
    setStegoFile(null);
    reset();
  };

  const audioAccept = {
    "audio/*": [".wav", ".mp3", ".ogg", ".flac"],
  };
  const videoAccept = {
    "video/*": [".mp4", ".avi", ".mkv", ".mov", ".webm"],
  };

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.breadcrumb}>
          <Link href="/">Home</Link> / Decode
        </div>
        <h1 className={styles.title}>
          <span className={styles.titleIcon}>🔓</span>
          Decode — Extract Data
        </h1>
        <p className={styles.subtitle}>
          Extract hidden files from steganographic audio or video
        </p>
      </div>

      {/* Mode toggle */}
      <div className={styles.formSection}>
        <span className={styles.formLabel}>Source Type</span>
        <div className={styles.methodToggle}>
          <button
            className={`${styles.methodBtn} ${mode === "audio" ? styles.methodBtnActive : ""}`}
            onClick={() => { setMode("audio"); setStegoFile(null); }}
            type="button"
          >
            🎵 Audio File
          </button>
          <button
            className={`${styles.methodBtn} ${mode === "video" ? styles.methodBtnActive : ""}`}
            onClick={() => { setMode("video"); setStegoFile(null); }}
            type="button"
          >
            🎬 Video File
          </button>
        </div>
      </div>

      {/* Upload form */}
      <div className={styles.form}>
        <div className={styles.formSection}>
          <span className={styles.formLabel}>
            {mode === "audio" ? "Steganographic Audio" : "Steganographic Video"}
          </span>
          <DropZone
            onFileSelect={setStegoFile}
            currentFile={stegoFile}
            onClear={() => setStegoFile(null)}
            accept={mode === "audio" ? audioAccept : videoAccept}
            label={
              mode === "audio"
                ? "Drop audio file with hidden data"
                : "Drop video file with hidden data"
            }
            icon="🔍"
          />
        </div>

        {/* Waveform preview */}
        {stegoFile && mode === "audio" && (
          <WaveformViewer audioFile={stegoFile} label="Stego Audio Preview" />
        )}

        {/* Progress */}
        {loading && (
          <div className={styles.progressWrap}>
            <div
              className={styles.progressBar}
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className={styles.errorBox}>⚠ {error}</div>
        )}

        {/* Success */}
        {data && (
          <div className={styles.result}>
            <div className={styles.resultTitle}>
              ✓ Decoding Complete — Hidden File Extracted
            </div>
            <div className={styles.resultActions}>
              <NeonButton variant="ghost" onClick={handleReset} icon="↻">
                Decode Another
              </NeonButton>
            </div>
          </div>
        )}

        {/* Submit */}
        <NeonButton
          variant="magenta"
          size="lg"
          onClick={handleDecode}
          disabled={!canDecode}
          loading={loading}
          icon="🔓"
        >
          {loading ? "Decoding..." : "Decode & Extract"}
        </NeonButton>
      </div>
    </div>
  );
}
