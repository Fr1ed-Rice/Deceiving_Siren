"""
LSB (Least Significant Bit) Audio Steganography Engine.

Hides arbitrary binary data inside the least significant bits of WAV audio samples.
The human ear cannot perceive single-bit changes in amplitude.

Algorithm:
  Encode: For each audio sample, clear LSB then OR with one bit of payload.
          sample = (sample & 0xFE) | secret_bit
  Decode: Read LSB of each sample, reconstruct payload bit-by-bit.
"""

import struct
import wave
import numpy as np


# Header format: 4 bytes magic + 4 bytes filename length + filename + 4 bytes data length
MAGIC = b"DCSN"  # Deceiving Siren magic bytes


def encode(carrier_path: str, payload_path: str, output_path: str, payload_filename: str) -> dict:
    """
    Hide a file inside a WAV audio file using LSB steganography.

    Args:
        carrier_path: Path to the carrier WAV file.
        payload_path: Path to the file to hide.
        output_path: Path to write the output WAV file.
        payload_filename: Original filename of the payload (preserved for extraction).

    Returns:
        dict with metadata about the operation.

    Raises:
        ValueError: If the carrier is too small to hold the payload.
    """
    # Read the payload data
    with open(payload_path, "rb") as f:
        payload_data = f.read()

    # Build the header: MAGIC + filename_len + filename + data_len + data
    filename_bytes = payload_filename.encode("utf-8")
    header = (
        MAGIC
        + struct.pack("<I", len(filename_bytes))
        + filename_bytes
        + struct.pack("<I", len(payload_data))
    )
    full_payload = header + payload_data

    # Convert payload to bit array
    payload_bits = np.unpackbits(
        np.frombuffer(full_payload, dtype=np.uint8)
    )

    # Read carrier WAV
    with wave.open(carrier_path, "rb") as wav_in:
        params = wav_in.getparams()
        n_channels = params.nchannels
        sample_width = params.sampwidth
        n_frames = params.nframes
        raw_frames = wav_in.readframes(n_frames)

    # Calculate capacity
    total_samples = n_frames * n_channels
    if len(payload_bits) > total_samples:
        max_bytes = total_samples // 8
        raise ValueError(
            f"Carrier audio too small. Can hide {max_bytes:,} bytes, "
            f"but payload is {len(full_payload):,} bytes. "
            f"Use a longer audio file."
        )

    # Convert raw frames to numpy array
    if sample_width == 1:
        dtype = np.uint8
    elif sample_width == 2:
        dtype = np.int16
    elif sample_width == 4:
        dtype = np.int32
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")

    samples = np.frombuffer(raw_frames, dtype=dtype).copy()

    # Embed payload bits into LSB of each sample
    for i, bit in enumerate(payload_bits):
        if dtype == np.uint8:
            samples[i] = (int(samples[i]) & 0xFE) | int(bit)
        else:
            # For signed types, modify the least significant bit
            val = int(samples[i])
            if val >= 0:
                samples[i] = (val & ~1) | int(bit)
            else:
                # Two's complement: modify LSB
                samples[i] = (val | 1) if bit else (val & ~1)

    # Write output WAV
    with wave.open(output_path, "wb") as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(samples.tobytes())

    capacity_pct = (len(payload_bits) / total_samples) * 100

    return {
        "carrier_duration_s": n_frames / params.framerate,
        "carrier_samples": total_samples,
        "payload_size_bytes": len(full_payload),
        "payload_bits": len(payload_bits),
        "capacity_used_pct": round(capacity_pct, 2),
        "payload_filename": payload_filename,
    }


def decode(stego_path: str, output_dir: str) -> dict:
    """
    Extract a hidden file from a steganographic WAV file.

    Args:
        stego_path: Path to the WAV file containing hidden data.
        output_dir: Directory to write the extracted file.

    Returns:
        dict with the extracted filename and output path.

    Raises:
        ValueError: If no hidden data is found (magic bytes don't match).
    """
    # Read WAV
    with wave.open(stego_path, "rb") as wav_in:
        params = wav_in.getparams()
        n_channels = params.nchannels
        sample_width = params.sampwidth
        n_frames = params.nframes
        raw_frames = wav_in.readframes(n_frames)

    # Convert to numpy
    if sample_width == 1:
        dtype = np.uint8
    elif sample_width == 2:
        dtype = np.int16
    elif sample_width == 4:
        dtype = np.int32
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")

    samples = np.frombuffer(raw_frames, dtype=dtype)

    # Extract bits from LSB
    total_samples = n_frames * n_channels

    # First, extract enough bits to read the header
    # MAGIC (4) + filename_len (4) = 8 bytes = 64 bits minimum
    min_header_bits = 64
    if total_samples < min_header_bits:
        raise ValueError("Audio file too short to contain hidden data.")

    header_bits = np.array([int(s) & 1 for s in samples[:min_header_bits]], dtype=np.uint8)
    header_bytes = np.packbits(header_bits).tobytes()

    # Check magic
    if header_bytes[:4] != MAGIC:
        raise ValueError(
            "No hidden data found. The magic signature does not match. "
            "This file may not contain steganographic data, or it may have been "
            "re-encoded with a lossy format."
        )

    # Read filename length
    filename_len = struct.unpack("<I", header_bytes[4:8])[0]
    if filename_len > 1024:
        raise ValueError("Invalid header: filename length is unreasonably large.")

    # Now extract enough bits for: header(8) + filename + data_len(4)
    extended_header_bytes = 8 + filename_len + 4
    extended_header_bits = extended_header_bytes * 8

    if total_samples < extended_header_bits:
        raise ValueError("Audio file too short to contain the full header.")

    all_header_bits = np.array(
        [int(s) & 1 for s in samples[:extended_header_bits]], dtype=np.uint8
    )
    all_header = np.packbits(all_header_bits).tobytes()

    # Parse filename
    filename = all_header[8 : 8 + filename_len].decode("utf-8", errors="replace")

    # Parse data length
    data_len = struct.unpack("<I", all_header[8 + filename_len : 8 + filename_len + 4])[0]

    # Extract full payload
    total_needed_bits = (extended_header_bytes + data_len) * 8
    if total_samples < total_needed_bits:
        raise ValueError(
            f"Audio file too short. Expected {total_needed_bits} samples "
            f"but only have {total_samples}."
        )

    all_bits = np.array(
        [int(s) & 1 for s in samples[:total_needed_bits]], dtype=np.uint8
    )
    all_data = np.packbits(all_bits).tobytes()

    # Extract payload data
    payload_data = all_data[extended_header_bytes : extended_header_bytes + data_len]

    # Write extracted file
    import os
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "wb") as f:
        f.write(payload_data)

    return {
        "filename": filename,
        "output_path": output_path,
        "data_size_bytes": data_len,
    }
