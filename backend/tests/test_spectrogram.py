"""Tests for spectrogram steganography engine."""

import os
import tempfile
import wave

import numpy as np
import pytest

from app.services.spectrogram_stego import (
    encode_data_in_spectrogram,
    encode_image_in_spectrogram,
    extract_spectrogram_image,
)


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    import shutil
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def carrier_wav(temp_dir):
    """Generate a carrier WAV file (3 seconds of noise at 44100 Hz)."""
    path = os.path.join(temp_dir, "carrier.wav")
    sample_rate = 44100
    duration = 3
    n_samples = sample_rate * duration
    samples = (np.random.randn(n_samples) * 16000).astype(np.int16)

    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(samples.tobytes())

    return path


@pytest.fixture
def small_payload(temp_dir):
    """Small text payload."""
    path = os.path.join(temp_dir, "message.txt")
    with open(path, "w") as f:
        f.write("Hidden in the frequencies!")
    return path


@pytest.fixture
def test_image(temp_dir):
    """Create a small test image."""
    from PIL import Image
    path = os.path.join(temp_dir, "test_image.png")
    img = Image.new("L", (64, 64), 128)
    # Draw a simple pattern
    pixels = img.load()
    for x in range(64):
        for y in range(64):
            pixels[x, y] = (x * 4) % 256
    img.save(path)
    return path


def test_encode_data_in_spectrogram(temp_dir, carrier_wav, small_payload):
    """Test encoding data in spectrogram."""
    output_path = os.path.join(temp_dir, "stego_spectro.wav")

    meta = encode_data_in_spectrogram(
        carrier_path=carrier_wav,
        payload_path=small_payload,
        output_path=output_path,
        payload_filename="message.txt",
        intensity=0.3,
    )

    assert os.path.exists(output_path)
    assert meta["payload_filename"] == "message.txt"
    assert meta["intensity"] == 0.3
    assert len(meta["pixel_grid_shape"]) == 2


def test_encode_image_in_spectrogram(temp_dir, carrier_wav, test_image):
    """Test encoding an image in spectrogram."""
    output_path = os.path.join(temp_dir, "stego_img.wav")

    meta = encode_image_in_spectrogram(
        carrier_path=carrier_wav,
        image_path=test_image,
        output_path=output_path,
        intensity=0.5,
    )

    assert os.path.exists(output_path)
    assert meta["intensity"] == 0.5
    assert len(meta["embedded_size"]) == 2


def test_extract_spectrogram_image(temp_dir, carrier_wav):
    """Test extracting spectrogram as an image."""
    output_image = os.path.join(temp_dir, "spectrogram.png")

    meta = extract_spectrogram_image(
        audio_path=carrier_wav,
        output_image_path=output_image,
    )

    assert os.path.exists(output_image)
    assert meta["freq_bins"] > 0
    assert meta["time_frames"] > 0

    # Verify it's a valid image
    from PIL import Image
    img = Image.open(output_image)
    assert img.mode == "L"
    assert img.size[0] > 0 and img.size[1] > 0


def test_spectrogram_encode_then_extract(temp_dir, carrier_wav, test_image):
    """Test that encoding then extracting shows the embedded image."""
    stego_path = os.path.join(temp_dir, "stego.wav")
    extracted_image = os.path.join(temp_dir, "extracted_spectrogram.png")

    # Encode image
    encode_image_in_spectrogram(
        carrier_path=carrier_wav,
        image_path=test_image,
        output_path=stego_path,
        intensity=0.8,
    )

    # Extract spectrogram
    meta = extract_spectrogram_image(
        audio_path=stego_path,
        output_image_path=extracted_image,
    )

    assert os.path.exists(extracted_image)
    # The spectrogram should be larger than a trivial image
    file_size = os.path.getsize(extracted_image)
    assert file_size > 100  # Not empty
