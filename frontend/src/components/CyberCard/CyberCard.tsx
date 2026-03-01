import { ReactNode } from "react";
import styles from "./CyberCard.module.css";

type CyberCardVariant = "default" | "glow" | "magenta" | "green";

interface CyberCardProps {
  children: ReactNode;
  title?: string;
  icon?: string;
  variant?: CyberCardVariant;
  className?: string;
}

const variantMap: Record<CyberCardVariant, string> = {
  default: styles.card,
  glow: `${styles.card} ${styles.cardGlow}`,
  magenta: `${styles.card} ${styles.cardMagenta}`,
  green: `${styles.card} ${styles.cardGreen}`,
};

export default function CyberCard({
  children,
  title,
  icon,
  variant = "default",
  className = "",
}: CyberCardProps) {
  return (
    <div className={`${variantMap[variant]} ${className}`}>
      <div className={styles.cardContent}>
        {icon && <span className={styles.cardIcon}>{icon}</span>}
        {title && <h3 className={styles.cardTitle}>{title}</h3>}
        {children}
      </div>
    </div>
  );
}
