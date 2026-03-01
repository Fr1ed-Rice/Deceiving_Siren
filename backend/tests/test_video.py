"""Tests for video audio extraction and remuxing."""

import os
import tempfile

import pytest

# These tests require ffmpeg to be installed.
# They are skipped in CI if ffmpeg is not available.

from app.services.video_audio import extract_audio, remux_audio_into_video, get_video_info


def _ffmpeg_available():
    """Check if ffmpeg is available on the system."""
    import shutil
    return shutil.which("ffmpeg") is not None


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    import shutil
    shutil.rmtree(d, ignore_errors=True)


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not installed")
def test_extract_audio_requires_video(temp_dir):
    """Test that extraction fails for a non-video file."""
    # Create a dummy text file
    fake_video = os.path.join(temp_dir, "fake.mp4")
    with open(fake_video, "w") as f:
        f.write("not a video")

    output = os.path.join(temp_dir, "audio.wav")

    with pytest.raises(Exception):
        extract_audio(fake_video, output)
