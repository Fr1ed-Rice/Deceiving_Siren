"use client";

import { useState, useCallback } from "react";

interface UseApiState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  progress: number;
}

export function useApi<T>() {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    error: null,
    loading: false,
    progress: 0,
  });

  const execute = useCallback(
    async (
      apiCall: (onProgress: (pct: number) => void) => Promise<T>
    ): Promise<T | null> => {
      setState({ data: null, error: null, loading: true, progress: 0 });

      try {
        const result = await apiCall((pct: number) => {
          setState((prev) => ({ ...prev, progress: pct }));
        });

        setState({ data: result, error: null, loading: false, progress: 100 });
        return result;
      } catch (err: any) {
        let errorMessage = "An unexpected error occurred.";

        if (err.response) {
          // Try to parse error from blob response
          if (err.response.data instanceof Blob) {
            try {
              const text = await err.response.data.text();
              const json = JSON.parse(text);
              errorMessage = json.error || json.message || errorMessage;
            } catch {
              errorMessage = `Server error (${err.response.status})`;
            }
          } else if (err.response.data?.error) {
            errorMessage = err.response.data.error;
          }
        } else if (err.message) {
          errorMessage = err.message;
        }

        setState({
          data: null,
          error: errorMessage,
          loading: false,
          progress: 0,
        });
        return null;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({ data: null, error: null, loading: false, progress: 0 });
  }, []);

  return { ...state, execute, reset };
}

/** Download a Blob as a file */
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
