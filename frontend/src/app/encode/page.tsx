"use client";

import { useState } from "react";
import Link from "next/link";
import styles from "./page.module.css";
import DropZone from "@/components/DropZone/DropZone";
import FormatSelector from "@/components/FormatSelector/FormatSelector";
import NeonButton from "@/components/NeonButton/NeonButton";
import WaveformViewer from "@/components/WaveformViewer/WaveformViewer";
import CyberCard from "@/components/CyberCard/CyberCard";
import { useApi, downloadBlob } from "@/hooks/useApi";
import { encodeLSB, encodeVideo } from "@/lib/api";

type EncodeMode = "audio" | "video";

export default function EncodePage() {
  const [mode, setMode] = useState<EncodeMode>("audio");
  const [carrierFile, setCarrierFile] = useState<File | null>(null);
  const [payloadFile, setPayloadFile] = useState<File | null>(null);
  const [outputFormat, setOutputFormat] = useState("wav");
  const { loading, error, data, progress, execute, reset } = useApi<Blob>();

  const canEncode = carrierFile && payloadFile && !loading;

  const handleEncode = async () => {
    if (!carrierFile || !payloadFile) return;

    const blob = await execute((onProgress) => {
      if (mode === "video") {
        return encodeVideo({
          video: carrierFile,
          payload: payloadFile,
          method: "lsb",
          onProgress,
        });
      }
      return encodeLSB({
        carrier: carrierFile,
        payload: payloadFile,
        outputFormat,
        onProgress,
      });
    });

    if (blob) {
      const ext = mode === "video"
        ? carrierFile.name.split(".").pop() || "mp4"
        : outputFormat;
      downloadBlob(blob, `stego_output.${ext}`);
    }
  };

  const handleReset = () => {
    setCarrierFile(null);
    setPayloadFile(null);
    setOutputFormat("wav");
    reset();
  };

  const audioAccept = {
    "audio/*": [".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a"],
  };
  const videoAccept = {
    "video/*": [".mp4", ".avi", ".mkv", ".mov", ".webm"],
  };

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.breadcrumb}>
          <Link href="/">Home</Link> / Encode
        </div>
        <h1 className={styles.title}>
          <span className={styles.titleIcon}>🔒</span>
          Encode — Hide Data
        </h1>
        <p className={styles.subtitle}>
          Hide any file inside audio or video using LSB steganography
        </p>
      </div>

      {/* Mode toggle */}
      <div className={styles.formSection}>
        <span className={styles.formLabel}>Carrier Type</span>
        <div className={styles.methodToggle}>
          <button
            className={`${styles.methodBtn} ${mode === "audio" ? styles.methodBtnActive : ""}`}
            onClick={() => { setMode("audio"); setCarrierFile(null); }}
            type="button"
          >
            🎵 Audio File
          </button>
          <button
            className={`${styles.methodBtn} ${mode === "video" ? styles.methodBtnActive : ""}`}
            onClick={() => { setMode("video"); setCarrierFile(null); }}
            type="button"
          >
            🎬 Video File
          </button>
        </div>
      </div>

      {/* Upload form */}
      <div className={styles.form}>
        <div className={styles.formRow}>
          <div className={styles.formSection}>
            <span className={styles.formLabel}>
              {mode === "audio" ? "Carrier Audio" : "Carrier Video"}
            </span>
            <DropZone
              onFileSelect={setCarrierFile}
              currentFile={carrierFile}
              onClear={() => setCarrierFile(null)}
              accept={mode === "audio" ? audioAccept : videoAccept}
              label={mode === "audio" ? "Drop audio file here" : "Drop video file here"}
              icon={mode === "audio" ? "🎵" : "🎬"}
            />
          </div>

          <div className={styles.formSection}>
            <span className={styles.formLabel}>Payload (file to hide)</span>
            <DropZone
              onFileSelect={setPayloadFile}
              currentFile={payloadFile}
              onClear={() => setPayloadFile(null)}
              label="Drop any file to hide"
              icon="🔐"
            />
          </div>
        </div>

        {/* Waveform preview */}
        {carrierFile && mode === "audio" && (
          <WaveformViewer audioFile={carrierFile} label="Carrier Preview" />
        )}

        {/* Output format (audio mode only) */}
        {mode === "audio" && (
          <FormatSelector value={outputFormat} onChange={setOutputFormat} />
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
              ✓ Encoding Complete — File Downloaded
            </div>
            <div className={styles.resultActions}>
              <NeonButton variant="ghost" onClick={handleReset} icon="↻">
                Encode Another
              </NeonButton>
            </div>
          </div>
        )}

        {/* Submit */}
        <NeonButton
          variant="primary"
          size="lg"
          onClick={handleEncode}
          disabled={!canEncode}
          loading={loading}
          icon="🔒"
        >
          {loading ? "Encoding..." : "Encode & Download"}
        </NeonButton>
      </div>
    </div>
  );
}
