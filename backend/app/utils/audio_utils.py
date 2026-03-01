"""Audio format conversion utilities using pydub."""

import os
import shutil
from pydub import AudioSegment

# Ensure pydub can find ffmpeg/ffprobe even if PATH isn't inherited
_ffmpeg = shutil.which("ffmpeg")
_ffprobe = shutil.which("ffprobe")
if _ffmpeg:
    AudioSegment.converter = _ffmpeg
if _ffprobe:
    AudioSegment.ffprobe = _ffprobe


LOSSY_WARNING = (
    "⚠️ LOSSY FORMAT WARNING: You selected a lossy output format. "
    "Lossy compression will permanently alter the audio data, DESTROYING any hidden "
    "information embedded via steganography. The output file will sound normal but the "
    "hidden message will be unrecoverable. Use WAV or FLAC to preserve hidden data."
)


def convert_to_wav(input_path: str, output_path: str) -> str:
    """
    Convert any supported audio format to WAV (PCM 16-bit).

    Args:
        input_path: Path to the input audio file.
        output_path: Path for the output WAV file.

    Returns:
        Path to the converted WAV file.
    """
    ext = os.path.splitext(input_path)[1].lower().lstrip(".")

    if ext == "wav":
        # Already WAV — but normalize to PCM 16-bit
        audio = AudioSegment.from_wav(input_path)
    elif ext == "mp3":
        audio = AudioSegment.from_mp3(input_path)
    elif ext == "ogg":
        audio = AudioSegment.from_ogg(input_path)
    elif ext == "flac":
        audio = AudioSegment.from_file(input_path, format="flac")
    else:
        audio = AudioSegment.from_file(input_path)

    # Export as PCM 16-bit WAV
    audio = audio.set_sample_width(2)  # 16-bit
    audio.export(output_path, format="wav")

    return output_path


def convert_from_wav(input_path: str, output_path: str, output_format: str,
                     bitrate: str = "192k") -> dict:
    """
    Convert a WAV file to the specified output format.

    Args:
        input_path: Path to the input WAV file.
        output_path: Path for the output file.
        output_format: Target format ('wav', 'flac', 'mp3', 'ogg').
        bitrate: Bitrate for lossy formats (default: 192k).

    Returns:
        dict with output info and optional lossy warning.
    """
    audio = AudioSegment.from_wav(input_path)

    is_lossy = output_format in ("mp3", "ogg")
    warning = LOSSY_WARNING if is_lossy else None

    if output_format == "wav":
        audio.export(output_path, format="wav")
    elif output_format == "flac":
        audio.export(output_path, format="flac")
    elif output_format == "mp3":
        audio.export(output_path, format="mp3", bitrate=bitrate)
    elif output_format == "ogg":
        audio.export(output_path, format="ogg", codec="libvorbis", bitrate=bitrate)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    return {
        "output_path": output_path,
        "output_format": output_format,
        "output_size_bytes": os.path.getsize(output_path),
        "is_lossy": is_lossy,
        "warning": warning,
    }


def get_audio_info(file_path: str) -> dict:
    """Get basic info about an audio file."""
    audio = AudioSegment.from_file(file_path)
    return {
        "duration_ms": len(audio),
        "duration_s": len(audio) / 1000.0,
        "channels": audio.channels,
        "sample_width": audio.sample_width,
        "frame_rate": audio.frame_rate,
        "frame_count": audio.frame_count(),
    }


def is_audio_file(filename: str) -> bool:
    """Check if a filename has an audio extension."""
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    return ext in {"wav", "mp3", "ogg", "flac", "aac", "m4a", "wma"}


def is_video_file(filename: str) -> bool:
    """Check if a filename has a video extension."""
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    return ext in {"mp4", "avi", "mkv", "mov", "webm", "flv", "wmv"}
