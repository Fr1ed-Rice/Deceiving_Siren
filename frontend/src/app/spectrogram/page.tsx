"use client";

import { useState } from "react";
import Link from "next/link";
import styles from "../encode/page.module.css";
import DropZone from "@/components/DropZone/DropZone";
import FormatSelector from "@/components/FormatSelector/FormatSelector";
import NeonButton from "@/components/NeonButton/NeonButton";
import WaveformViewer from "@/components/WaveformViewer/WaveformViewer";
import SpectrogramViewer from "@/components/SpectrogramViewer/SpectrogramViewer";
import CyberCard from "@/components/CyberCard/CyberCard";
import { useApi, downloadBlob } from "@/hooks/useApi";
import { encodeSpectrogram, decodeSpectrogram } from "@/lib/api";

type SpectroAction = "encode" | "decode";
type SpectroMode = "data" | "image";

export default function SpectrogramPage() {
  const [action, setAction] = useState<SpectroAction>("encode");
  const [encodeMode, setEncodeMode] = useState<SpectroMode>("image");
  const [carrierFile, setCarrierFile] = useState<File | null>(null);
  const [payloadFile, setPayloadFile] = useState<File | null>(null);
  const [outputFormat, setOutputFormat] = useState("wav");
  const [intensity, setIntensity] = useState(0.5);
  const [spectrogramUrl, setSpectrogramUrl] = useState<string | null>(null);

  const encodeApi = useApi<Blob>();
  const decodeApi = useApi<Blob>();

  const canEncode = carrierFile && payloadFile && !encodeApi.loading;
  const canDecode = carrierFile && !decodeApi.loading;

  const handleEncode = async () => {
    if (!carrierFile || !payloadFile) return;

    const blob = await encodeApi.execute((onProgress) =>
      encodeSpectrogram({
        carrier: carrierFile,
        payload: payloadFile,
        mode: encodeMode,
        outputFormat,
        intensity,
        onProgress,
      })
    );

    if (blob) {
      downloadBlob(blob, `spectro_output.${outputFormat}`);
    }
  };

  const handleDecode = async () => {
    if (!carrierFile) return;

    const blob = await decodeApi.execute((onProgress) =>
      decodeSpectrogram({ audio: carrierFile, onProgress })
    );

    if (blob) {
      const url = URL.createObjectURL(blob);
      setSpectrogramUrl(url);
      downloadBlob(blob, "spectrogram.png");
    }
  };

  const handleReset = () => {
    setCarrierFile(null);
    setPayloadFile(null);
    setOutputFormat("wav");
    setIntensity(0.5);
    setSpectrogramUrl(null);
    encodeApi.reset();
    decodeApi.reset();
  };

  const audioAccept = {
    "audio/*": [".wav", ".mp3", ".ogg", ".flac"],
  };
  const imageAccept = {
    "image/*": [".png", ".jpg", ".jpeg", ".bmp"],
  };

  const loading = encodeApi.loading || decodeApi.loading;
  const error = encodeApi.error || decodeApi.error;
  const progress = encodeApi.progress || decodeApi.progress;

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.breadcrumb}>
          <Link href="/">Home</Link> / Spectrogram
        </div>
        <h1 className={styles.title}>
          <span className={styles.titleIcon}>📊</span>
          Spectrogram Steganography
        </h1>
        <p className={styles.subtitle}>
          Hide data in the frequency domain — visible only in the spectrogram view
        </p>
      </div>

      {/* Action toggle */}
      <div className={styles.formSection}>
        <span className={styles.formLabel}>Action</span>
        <div className={styles.methodToggle}>
          <button
            className={`${styles.methodBtn} ${action === "encode" ? styles.methodBtnActive : ""}`}
            onClick={() => { setAction("encode"); handleReset(); }}
            type="button"
          >
            🔒 Encode
          </button>
          <button
            className={`${styles.methodBtn} ${action === "decode" ? styles.methodBtnActive : ""}`}
            onClick={() => { setAction("decode"); handleReset(); }}
            type="button"
          >
            📊 View Spectrogram
          </button>
        </div>
      </div>

      <div className={styles.form}>
        {action === "encode" ? (
          <>
            {/* Encode mode */}
            <div className={styles.formSection}>
              <span className={styles.formLabel}>Embed Mode</span>
              <div className={styles.methodToggle}>
                <button
                  className={`${styles.methodBtn} ${encodeMode === "image" ? styles.methodBtnActive : ""}`}
                  onClick={() => setEncodeMode("image")}
                  type="button"
                >
                  🖼️ Image (visible in spectrogram)
                </button>
                <button
                  className={`${styles.methodBtn} ${encodeMode === "data" ? styles.methodBtnActive : ""}`}
                  onClick={() => setEncodeMode("data")}
                  type="button"
                >
                  📁 Any File (data grid)
                </button>
              </div>
            </div>

            <div className={styles.formRow}>
              <div className={styles.formSection}>
                <span className={styles.formLabel}>Carrier Audio</span>
                <DropZone
                  onFileSelect={setCarrierFile}
                  currentFile={carrierFile}
                  onClear={() => setCarrierFile(null)}
                  accept={audioAccept}
                  label="Drop carrier audio here"
                  icon="🎵"
                />
              </div>

              <div className={styles.formSection}>
                <span className={styles.formLabel}>
                  {encodeMode === "image" ? "Image to Embed" : "File to Embed"}
                </span>
                <DropZone
                  onFileSelect={setPayloadFile}
                  currentFile={payloadFile}
                  onClear={() => setPayloadFile(null)}
                  accept={encodeMode === "image" ? imageAccept : undefined}
                  label={
                    encodeMode === "image"
                      ? "Drop image (PNG/JPG)"
                      : "Drop any file"
                  }
                  icon={encodeMode === "image" ? "🖼️" : "📁"}
                />
              </div>
            </div>

            {/* Waveform preview */}
            {carrierFile && (
              <WaveformViewer audioFile={carrierFile} label="Carrier Preview" />
            )}

            {/* Intensity slider */}
            <div className={styles.sliderGroup}>
              <div className={styles.sliderLabel}>
                <span>Embedding Intensity</span>
                <span>{Math.round(intensity * 100)}%</span>
              </div>
              <input
                type="range"
                className={styles.slider}
                min="0.05"
                max="1"
                step="0.05"
                value={intensity}
                onChange={(e) => setIntensity(parseFloat(e.target.value))}
              />
            </div>

            {/* Output format */}
            <FormatSelector value={outputFormat} onChange={setOutputFormat} />

            {/* Encode button */}
            <NeonButton
              variant="primary"
              size="lg"
              onClick={handleEncode}
              disabled={!canEncode}
              loading={encodeApi.loading}
              icon="📊"
            >
              {encodeApi.loading ? "Encoding..." : "Encode in Spectrogram"}
            </NeonButton>
          </>
        ) : (
          <>
            {/* Decode / View Spectrogram */}
            <div className={styles.formSection}>
              <span className={styles.formLabel}>Audio to Analyze</span>
              <DropZone
                onFileSelect={setCarrierFile}
                currentFile={carrierFile}
                onClear={() => setCarrierFile(null)}
                accept={audioAccept}
                label="Drop audio file to view spectrogram"
                icon="🔍"
              />
            </div>

            {carrierFile && (
              <WaveformViewer audioFile={carrierFile} label="Audio Preview" />
            )}

            {/* Spectrogram display */}
            {spectrogramUrl && (
              <SpectrogramViewer
                imageUrl={spectrogramUrl}
                label="Extracted Spectrogram"
              />
            )}

            <NeonButton
              variant="green"
              size="lg"
              onClick={handleDecode}
              disabled={!canDecode}
              loading={decodeApi.loading}
              icon="📊"
            >
              {decodeApi.loading ? "Extracting..." : "Extract Spectrogram"}
            </NeonButton>
          </>
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
        {error && <div className={styles.errorBox}>⚠ {error}</div>}

        {/* Success */}
        {(encodeApi.data || decodeApi.data) && (
          <div className={styles.result}>
            <div className={styles.resultTitle}>
              ✓ Operation Complete
            </div>
            <div className={styles.resultActions}>
              <NeonButton variant="ghost" onClick={handleReset} icon="↻">
                Start Over
              </NeonButton>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
