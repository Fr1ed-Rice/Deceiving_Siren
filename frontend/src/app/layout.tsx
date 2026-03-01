import type { Metadata } from "next";
import "@fontsource/jetbrains-mono/400.css";
import "@fontsource/jetbrains-mono/700.css";
import "./globals.css";
import Navbar from "@/components/Navbar/Navbar";

export const metadata: Metadata = {
  title: "Deceiving Siren — Audio & Video Steganography",
  description:
    "Hide any file inside audio and video data using LSB encoding and spectrogram embedding. What you hear is not what it seems.",
  keywords: [
    "steganography",
    "audio",
    "video",
    "LSB",
    "spectrogram",
    "cybersecurity",
    "data hiding",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
