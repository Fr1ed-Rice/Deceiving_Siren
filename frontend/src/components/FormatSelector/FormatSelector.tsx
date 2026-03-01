"use client";

import styles from "./FormatSelector.module.css";

interface FormatOption {
  value: string;
  label: string;
  lossy: boolean;
}

const FORMAT_OPTIONS: FormatOption[] = [
  { value: "wav", label: "WAV", lossy: false },
  { value: "flac", label: "FLAC", lossy: false },
  { value: "mp3", label: "MP3", lossy: true },
  { value: "ogg", label: "OGG", lossy: true },
];

interface FormatSelectorProps {
  value: string;
  onChange: (format: string) => void;
  label?: string;
}

export default function FormatSelector({
  value,
  onChange,
  label = "Output Format",
}: FormatSelectorProps) {
  const selectedOption = FORMAT_OPTIONS.find((o) => o.value === value);

  return (
    <div className={styles.selectorGroup}>
      <span className={styles.label}>{label}</span>
      <div className={styles.options}>
        {FORMAT_OPTIONS.map((option) => {
          const isSelected = value === option.value;
          const classes = [
            styles.option,
            isSelected ? styles.optionSelected : "",
            option.lossy ? styles.optionLossy : "",
          ]
            .filter(Boolean)
            .join(" ");

          return (
            <button
              key={option.value}
              className={classes}
              onClick={() => onChange(option.value)}
              type="button"
            >
              {option.label}
              {option.lossy ? (
                <span className={styles.lossyTag}>lossy</span>
              ) : (
                <span className={styles.losslessTag}>✓</span>
              )}
            </button>
          );
        })}
      </div>

      {selectedOption?.lossy && (
        <div className={styles.warning}>
          ⚠ Lossy compression will <strong>destroy</strong> hidden data.
          The output will sound normal but embedded information will be
          unrecoverable. Use WAV or FLAC to preserve hidden data.
        </div>
      )}
    </div>
  );
}
