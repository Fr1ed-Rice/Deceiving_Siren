import axios, { AxiosProgressEvent } from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 300000, // 5 minutes for large files
});

export interface EncodeOptions {
  carrier: File;
  payload: File;
  outputFormat?: string;
  onProgress?: (pct: number) => void;
}

export interface SpectrogramEncodeOptions extends EncodeOptions {
  mode?: "data" | "image";
  intensity?: number;
}

export interface VideoEncodeOptions {
  video: File;
  payload: File;
  method?: "lsb" | "spectrogram";
  intensity?: number;
  onProgress?: (pct: number) => void;
}

export interface DecodeOptions {
  audio: File;
  onProgress?: (pct: number) => void;
}

export interface VideoDecodeOptions {
  video: File;
  method?: "lsb" | "spectrogram";
  onProgress?: (pct: number) => void;
}

function buildProgress(
  onProgress?: (pct: number) => void
): ((event: AxiosProgressEvent) => void) | undefined {
  if (!onProgress) return undefined;
  return (event: AxiosProgressEvent) => {
    if (event.total) {
      onProgress(Math.round((event.loaded / event.total) * 100));
    }
  };
}

/** LSB encode a payload into a carrier audio file */
export async function encodeLSB(options: EncodeOptions): Promise<Blob> {
  const form = new FormData();
  form.append("carrier", options.carrier);
  form.append("payload", options.payload);
  form.append("output_format", options.outputFormat || "wav");

  const res = await api.post("/encode", form, {
    responseType: "blob",
    onUploadProgress: buildProgress(options.onProgress),
  });
  return res.data;
}

/** LSB decode hidden data from an audio file */
export async function decodeLSB(options: DecodeOptions): Promise<Blob> {
  const form = new FormData();
  form.append("audio", options.audio);

  const res = await api.post("/decode", form, {
    responseType: "blob",
    onUploadProgress: buildProgress(options.onProgress),
  });
  return res.data;
}

/** Encode data/image into audio spectrogram */
export async function encodeSpectrogram(
  options: SpectrogramEncodeOptions
): Promise<Blob> {
  const form = new FormData();
  form.append("carrier", options.carrier);
  form.append("payload", options.payload);
  form.append("mode", options.mode || "data");
  form.append("output_format", options.outputFormat || "wav");
  if (options.intensity !== undefined) {
    form.append("intensity", options.intensity.toString());
  }

  const res = await api.post("/encode-spectrogram", form, {
    responseType: "blob",
    onUploadProgress: buildProgress(options.onProgress),
  });
  return res.data;
}

/** Extract spectrogram as PNG image */
export async function decodeSpectrogram(
  options: DecodeOptions
): Promise<Blob> {
  const form = new FormData();
  form.append("audio", options.audio);

  const res = await api.post("/decode-spectrogram", form, {
    responseType: "blob",
    onUploadProgress: buildProgress(options.onProgress),
  });
  return res.data;
}

/** Encode data into video's audio track */
export async function encodeVideo(
  options: VideoEncodeOptions
): Promise<Blob> {
  const form = new FormData();
  form.append("video", options.video);
  form.append("payload", options.payload);
  form.append("method", options.method || "lsb");
  if (options.intensity !== undefined) {
    form.append("intensity", options.intensity.toString());
  }

  const res = await api.post("/encode-video", form, {
    responseType: "blob",
    onUploadProgress: buildProgress(options.onProgress),
  });
  return res.data;
}

/** Decode hidden data from video's audio track */
export async function decodeVideo(
  options: VideoDecodeOptions
): Promise<Blob> {
  const form = new FormData();
  form.append("video", options.video);
  form.append("method", options.method || "lsb");

  const res = await api.post("/decode-video", form, {
    responseType: "blob",
    onUploadProgress: buildProgress(options.onProgress),
  });
  return res.data;
}

/** Health check */
export async function healthCheck(): Promise<{ status: string }> {
  const res = await api.get("/health");
  return res.data;
}

export default api;
