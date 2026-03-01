"""
Spectrogram Steganography Engine.

Hides data (rendered as an image) in the frequency domain of audio.
When viewing the spectrogram (e.g., in Audacity), the hidden image becomes visible.

For arbitrary file data: the file bytes are arranged into a 2D grid (image)
and embedded into specific frequency bins of the STFT magnitude matrix.

For image payloads: the image is directly resized and embedded.

Uses librosa for STFT/ISTFT with original phase preservation.
"""

import os
import struct

import numpy as np
from PIL import Image
import librosa
import soundfile as sf


MAGIC = b"DCSG"  # Spectrogram stego magic


def _data_to_image(data: bytes, filename: str) -> np.ndarray:
    """Convert arbitrary binary data into a 2D grayscale pixel grid."""
    # Pack header: magic + filename_len + filename + data_len + data
    filename_bytes = filename.encode("utf-8")
    header = (
        MAGIC
        + struct.pack("<I", len(filename_bytes))
        + filename_bytes
        + struct.pack("<I", len(data))
    )
    full_payload = header + data

    # Compute dimensions for a roughly square image
    total_bytes = len(full_payload)
    width = int(np.ceil(np.sqrt(total_bytes)))
    height = int(np.ceil(total_bytes / width))

    # Pad to fill the grid
    padded = full_payload + b"\x00" * (width * height - total_bytes)
    pixel_grid = np.frombuffer(padded, dtype=np.uint8).reshape((height, width))

    return pixel_grid


def _image_from_spectrogram(magnitude: np.ndarray, freq_start: int, freq_end: int,
                            width: int, height: int) -> np.ndarray:
    """Extract the embedded image region from a spectrogram magnitude matrix."""
    region = magnitude[freq_start:freq_end, :width]
    # Denormalize from spectrogram scale back to 0-255
    img_array = np.clip(region * 255.0, 0, 255).astype(np.uint8)
    return img_array[:height, :width]


def encode_data_in_spectrogram(
    carrier_path: str,
    payload_path: str,
    output_path: str,
    payload_filename: str,
    n_fft: int = 2048,
    hop_length: int = 512,
    intensity: float = 0.3,
) -> dict:
    """
    Hide arbitrary file data in the spectrogram of an audio file.

    The data is converted to a pixel grid and embedded into upper frequency
    bins of the STFT magnitude matrix.

    Args:
        carrier_path: Path to carrier WAV.
        payload_path: Path to the file to hide.
        output_path: Path for output WAV.
        payload_filename: Original filename of the payload.
        n_fft: FFT window size.
        hop_length: Hop length for STFT.
        intensity: Embedding strength (0.0 to 1.0).

    Returns:
        dict with metadata.
    """
    # Read payload
    with open(payload_path, "rb") as f:
        payload_data = f.read()

    # Convert data to pixel grid
    pixel_grid = _data_to_image(payload_data, payload_filename)
    img_height, img_width = pixel_grid.shape

    # Load carrier audio
    y, sr = librosa.load(carrier_path, sr=None, mono=True)

    # Compute STFT
    stft_matrix = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft_matrix)
    phase = np.angle(stft_matrix)

    freq_bins, time_frames = magnitude.shape

    # Check capacity
    if img_height > freq_bins // 2:
        raise ValueError(
            f"Payload too large for spectrogram. Need {img_height} frequency bins, "
            f"but only {freq_bins // 2} available in upper half. "
            f"Use a longer audio file or increase n_fft."
        )
    if img_width > time_frames:
        raise ValueError(
            f"Payload too wide for spectrogram. Need {img_width} time frames, "
            f"but only {time_frames} available. Use a longer audio file."
        )

    # Embed in upper frequency bins (less audible)
    freq_start = freq_bins - img_height
    freq_end = freq_bins

    # Normalize pixel values to 0-1 and embed
    normalized_pixels = pixel_grid.astype(np.float32) / 255.0
    magnitude[freq_start:freq_end, :img_width] = normalized_pixels * intensity * np.max(magnitude)

    # Reconstruct complex STFT
    stft_modified = magnitude * np.exp(1j * phase)

    # Inverse STFT
    y_modified = librosa.istft(stft_modified, hop_length=hop_length, length=len(y))

    # Normalize to prevent clipping
    max_val = np.max(np.abs(y_modified))
    if max_val > 0:
        y_modified = y_modified / max_val * 0.95

    # Write output
    sf.write(output_path, y_modified, sr)

    return {
        "carrier_duration_s": len(y) / sr,
        "sample_rate": sr,
        "payload_size_bytes": len(payload_data),
        "pixel_grid_shape": [img_height, img_width],
        "freq_range": [freq_start, freq_end],
        "intensity": intensity,
        "payload_filename": payload_filename,
    }


def encode_image_in_spectrogram(
    carrier_path: str,
    image_path: str,
    output_path: str,
    n_fft: int = 2048,
    hop_length: int = 512,
    intensity: float = 0.5,
) -> dict:
    """
    Hide an image directly in the spectrogram (visible as a picture).

    Args:
        carrier_path: Path to carrier WAV.
        image_path: Path to the image (PNG/JPG) to embed.
        output_path: Path for output WAV.
        n_fft: FFT window size.
        hop_length: Hop length for STFT.
        intensity: Embedding strength (0.0 to 1.0).

    Returns:
        dict with metadata.
    """
    # Load carrier audio
    y, sr = librosa.load(carrier_path, sr=None, mono=True)

    # Compute STFT
    stft_matrix = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft_matrix)
    phase = np.angle(stft_matrix)

    freq_bins, time_frames = magnitude.shape

    # Load and resize image to fit spectrogram
    img = Image.open(image_path).convert("L")  # Grayscale

    # Use upper half of frequency bins
    target_height = freq_bins // 2
    target_width = time_frames
    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    img_array = np.array(img_resized, dtype=np.float32) / 255.0

    # Flip vertically (spectrogram y-axis is inverted)
    img_array = np.flipud(img_array)

    # Embed in upper half of frequency bins
    freq_start = freq_bins - target_height
    magnitude[freq_start:, :] = img_array * intensity * np.max(magnitude)

    # Reconstruct
    stft_modified = magnitude * np.exp(1j * phase)
    y_modified = librosa.istft(stft_modified, hop_length=hop_length, length=len(y))

    # Normalize
    max_val = np.max(np.abs(y_modified))
    if max_val > 0:
        y_modified = y_modified / max_val * 0.95

    sf.write(output_path, y_modified, sr)

    return {
        "carrier_duration_s": len(y) / sr,
        "sample_rate": sr,
        "image_original_size": list(img.size),
        "embedded_size": [target_height, target_width],
        "intensity": intensity,
    }


def extract_spectrogram_image(
    audio_path: str,
    output_image_path: str,
    n_fft: int = 2048,
    hop_length: int = 512,
) -> dict:
    """
    Extract the spectrogram of an audio file as a PNG image.

    This reveals any data hidden in the frequency domain.

    Args:
        audio_path: Path to the audio file.
        output_image_path: Path to save the spectrogram PNG.
        n_fft: FFT window size.
        hop_length: Hop length for STFT.

    Returns:
        dict with metadata.
    """
    # Load audio
    y, sr = librosa.load(audio_path, sr=None, mono=True)

    # Compute spectrogram (power)
    stft_matrix = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft_matrix)

    # Convert to dB scale for visualization
    mag_db = librosa.amplitude_to_db(magnitude, ref=np.max)

    # Normalize to 0-255
    mag_normalized = ((mag_db - mag_db.min()) / (mag_db.max() - mag_db.min()) * 255).astype(np.uint8)

    # Flip vertically (low freq at bottom)
    mag_normalized = np.flipud(mag_normalized)

    # Save as image
    img = Image.fromarray(mag_normalized, mode="L")
    img.save(output_image_path)

    return {
        "image_path": output_image_path,
        "image_size": list(img.size),
        "duration_s": len(y) / sr,
        "sample_rate": sr,
        "freq_bins": magnitude.shape[0],
        "time_frames": magnitude.shape[1],
    }
