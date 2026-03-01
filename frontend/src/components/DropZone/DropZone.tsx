"use client";

import { useCallback, useState } from "react";
import { useDropzone, FileRejection } from "react-dropzone";
import styles from "./DropZone.module.css";

const MAX_FILE_SIZE = 80 * 1024 * 1024; // 80MB

interface DropZoneProps {
  onFileSelect: (file: File) => void;
  accept?: Record<string, string[]>;
  label?: string;
  subtitle?: string;
  icon?: string;
  currentFile?: File | null;
  onClear?: () => void;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getFileIcon(filename: string): string {
  const ext = filename.split(".").pop()?.toLowerCase() || "";
  const iconMap: Record<string, string> = {
    wav: "🎵",
    mp3: "🎵",
    ogg: "🎵",
    flac: "🎵",
    mp4: "🎬",
    avi: "🎬",
    mkv: "🎬",
    mov: "🎬",
    txt: "📄",
    pdf: "📕",
    png: "🖼️",
    jpg: "🖼️",
    jpeg: "🖼️",
    zip: "📦",
    rar: "📦",
  };
  return iconMap[ext] || "📁";
}

export default function DropZone({
  onFileSelect,
  accept,
  label = "Drop your file here",
  subtitle = "or click to browse",
  icon = "📂",
  currentFile,
  onClear,
}: DropZoneProps) {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejections: FileRejection[]) => {
      setError(null);

      if (rejections.length > 0) {
        const rejection = rejections[0];
        const err = rejection.errors[0];
        if (err.code === "file-too-large") {
          setError(
            `File size (${formatFileSize(rejection.file.size)}) exceeds the 80MB limit.`
          );
        } else {
          setError(err.message);
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } =
    useDropzone({
      onDrop,
      maxSize: MAX_FILE_SIZE,
      multiple: false,
      accept,
    });

  const zoneClass = [
    styles.dropzone,
    isDragActive && !isDragReject ? styles.dropzoneActive : "",
    isDragReject ? styles.dropzoneReject : "",
  ]
    .filter(Boolean)
    .join(" ");

  if (currentFile) {
    return (
      <div className={styles.dropzone} style={{ cursor: "default" }}>
        <div className={styles.filePreview}>
          <span className={styles.fileIcon}>
            {getFileIcon(currentFile.name)}
          </span>
          <div className={styles.fileInfo}>
            <div className={styles.fileName}>{currentFile.name}</div>
            <div className={styles.fileSize}>
              {formatFileSize(currentFile.size)}
            </div>
          </div>
          {onClear && (
            <button
              className={styles.removeBtn}
              onClick={onClear}
              type="button"
            >
              ✕ Remove
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div {...getRootProps({ className: zoneClass })}>
        <input {...getInputProps()} />
        <span className={styles.icon}>{icon}</span>
        <div className={styles.title}>{label}</div>
        <div className={styles.subtitle}>
          {subtitle} — <span className={styles.browse}>browse files</span>
        </div>
        <div className={styles.sizeLimit}>Max file size: 80MB</div>
      </div>
      {error && <div className={styles.error}>⚠ {error}</div>}
    </div>
  );
}
