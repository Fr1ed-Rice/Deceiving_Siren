"""
Video Audio Extraction & Remuxing.

Extracts the audio track from a video file, allows steganographic processing,
then remuxes the modified audio back into the original video container.

Uses moviepy for extraction and ffmpeg for remuxing.
"""

import os
import subprocess
import tempfile

from moviepy import VideoFileClip


def extract_audio(video_path: str, output_audio_path: str) -> dict:
    """
    Extract the audio track from a video file as WAV.

    Args:
        video_path: Path to the input video file.
        output_audio_path: Path to write the extracted WAV.

    Returns:
        dict with metadata about the extraction.

    Raises:
        ValueError: If the video has no audio track.
    """
    clip = VideoFileClip(video_path)

    if clip.audio is None:
        clip.close()
        raise ValueError("The video file has no audio track.")

    duration = clip.duration
    fps = clip.audio.fps

    clip.audio.write_audiofile(
        output_audio_path,
        fps=44100,
        nbytes=2,
        codec="pcm_s16le",
        logger=None,
    )
    clip.close()

    return {
        "video_duration_s": duration,
        "audio_sample_rate": 44100,
        "audio_path": output_audio_path,
    }


def remux_audio_into_video(
    original_video_path: str,
    modified_audio_path: str,
    output_video_path: str,
) -> dict:
    """
    Replace the audio track of a video with a modified audio file.

    Uses ffmpeg to copy the video stream and replace only the audio.

    Args:
        original_video_path: Path to the original video.
        modified_audio_path: Path to the modified audio (WAV).
        output_video_path: Path for the output video.

    Returns:
        dict with metadata.
    """
    cmd = [
        "ffmpeg",
        "-y",                     # Overwrite output
        "-i", original_video_path,  # Original video
        "-i", modified_audio_path,  # New audio
        "-c:v", "copy",           # Copy video stream (no re-encode)
        "-map", "0:v:0",          # Take video from first input
        "-map", "1:a:0",          # Take audio from second input
        "-shortest",              # Match shortest stream
        output_video_path,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,  # 10 minute timeout
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg remux failed (exit code {result.returncode}): {result.stderr[:500]}"
        )

    output_size = os.path.getsize(output_video_path)

    return {
        "output_path": output_video_path,
        "output_size_bytes": output_size,
    }


def get_video_info(video_path: str) -> dict:
    """Get basic info about a video file."""
    clip = VideoFileClip(video_path)
    info = {
        "duration_s": clip.duration,
        "size": clip.size,
        "fps": clip.fps,
        "has_audio": clip.audio is not None,
    }
    clip.close()
    return info
