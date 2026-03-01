"""Tests for LSB steganography engine."""

import os
import struct
import tempfile
import wave

import numpy as np
import pytest

from app.services.lsb_stego import encode, decode, MAGIC


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    d = tempfile.mkdtemp()
    yield d
    import shutil
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def carrier_wav(temp_dir):
    """Generate a simple carrier WAV file (1 second of silence at 44100 Hz)."""
    path = os.path.join(temp_dir, "carrier.wav")
    sample_rate = 44100
    duration = 2  # seconds
    n_samples = sample_rate * duration

    # Generate random noise (better for hiding data than silence)
    samples = np.random.randint(-32768, 32767, size=n_samples, dtype=np.int16)

    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(samples.tobytes())

    return path


@pytest.fixture
def payload_file(temp_dir):
    """Create a small payload file."""
    path = os.path.join(temp_dir, "secret.txt")
    with open(path, "w") as f:
        f.write("This is a secret message hidden by Deceiving Siren!")
    return path


def test_encode_decode_roundtrip(temp_dir, carrier_wav, payload_file):
    """Test that encoding and decoding produces the original payload."""
    stego_path = os.path.join(temp_dir, "stego.wav")
    extract_dir = os.path.join(temp_dir, "extracted")
    os.makedirs(extract_dir, exist_ok=True)

    # Encode
    meta = encode(carrier_wav, payload_file, stego_path, "secret.txt")
    assert meta["payload_filename"] == "secret.txt"
    assert meta["capacity_used_pct"] > 0
    assert os.path.exists(stego_path)

    # Decode
    result = decode(stego_path, extract_dir)
    assert result["filename"] == "secret.txt"

    # Verify content
    with open(result["output_path"], "r") as f:
        content = f.read()
    assert content == "This is a secret message hidden by Deceiving Siren!"


def test_encode_binary_file(temp_dir, carrier_wav):
    """Test encoding a binary file (not just text)."""
    # Create a binary payload
    payload_path = os.path.join(temp_dir, "data.bin")
    binary_data = bytes(range(256)) * 10
    with open(payload_path, "wb") as f:
        f.write(binary_data)

    stego_path = os.path.join(temp_dir, "stego.wav")
    extract_dir = os.path.join(temp_dir, "extracted")
    os.makedirs(extract_dir, exist_ok=True)

    # Encode
    encode(carrier_wav, payload_path, stego_path, "data.bin")

    # Decode
    result = decode(stego_path, extract_dir)

    with open(result["output_path"], "rb") as f:
        extracted = f.read()
    assert extracted == binary_data


def test_carrier_too_small(temp_dir):
    """Test that encoding fails if carrier is too small."""
    # Create a tiny carrier
    carrier_path = os.path.join(temp_dir, "tiny.wav")
    samples = np.zeros(100, dtype=np.int16)
    with wave.open(carrier_path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(samples.tobytes())

    # Create a payload larger than the carrier can hold
    payload_path = os.path.join(temp_dir, "big.txt")
    with open(payload_path, "w") as f:
        f.write("x" * 1000)

    stego_path = os.path.join(temp_dir, "stego.wav")

    with pytest.raises(ValueError, match="too small"):
        encode(carrier_path, payload_path, stego_path, "big.txt")


def test_decode_no_hidden_data(temp_dir, carrier_wav):
    """Test that decoding a normal audio file raises ValueError."""
    extract_dir = os.path.join(temp_dir, "extracted")
    os.makedirs(extract_dir, exist_ok=True)

    with pytest.raises(ValueError, match="No hidden data found"):
        decode(carrier_wav, extract_dir)
