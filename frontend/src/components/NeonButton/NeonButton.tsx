import { ReactNode, ButtonHTMLAttributes } from "react";
import styles from "./NeonButton.module.css";

type ButtonVariant = "primary" | "magenta" | "green" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

interface NeonButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  icon?: string;
}

export default function NeonButton({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  disabled,
  className = "",
  ...props
}: NeonButtonProps) {
  const sizeClass = size !== "md" ? styles[size] : "";

  return (
    <button
      className={`${styles.btn} ${styles[variant]} ${sizeClass} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <span className={styles.spinner} />}
      {!loading && icon && <span>{icon}</span>}
      {children}
    </button>
  );
}
