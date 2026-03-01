"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./Navbar.module.css";

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/encode", label: "Encode" },
  { href: "/decode", label: "Decode" },
  { href: "/spectrogram", label: "Spectrogram" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className={styles.nav}>
      <div className={styles.navInner}>
        <Link href="/" className={styles.logo}>
          <span className={styles.logoIcon}>🧜‍♀️</span>
          <span className={styles.logoText}>Deceiving Siren</span>
        </Link>

        <button
          className={styles.mobileToggle}
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? "✕" : "☰"}
        </button>

        <ul className={`${styles.links} ${mobileOpen ? styles.linksOpen : ""}`}>
          {navLinks.map(({ href, label }) => (
            <li key={href}>
              <Link
                href={href}
                className={`${styles.link} ${pathname === href ? styles.linkActive : ""}`}
                onClick={() => setMobileOpen(false)}
              >
                {label}
              </Link>
            </li>
          ))}
          <li>
            <span className={styles.statusBadge}>
              <span className="status-dot status-dot--live" />
              Online
            </span>
          </li>
        </ul>
      </div>
    </nav>
  );
}
