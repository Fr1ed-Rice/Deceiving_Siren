"use client";

import styles from "./SpectrogramViewer.module.css";

interface SpectrogramViewerProps {
  imageUrl?: string;
  label?: string;
}

export default function SpectrogramViewer({
  imageUrl,
  label = "Spectrogram",
}: SpectrogramViewerProps) {
  if (!imageUrl) {
    return (
      <div className={styles.container}>
        <span className={styles.label}>{label}</span>
        <div className={styles.placeholder}>
          No spectrogram data available
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <span className={styles.label}>{label}</span>
      <div className={styles.imageWrap}>
        <img
          src={imageUrl}
          alt="Audio spectrogram visualization"
          className={styles.image}
        />
      </div>
    </div>
  );
}
