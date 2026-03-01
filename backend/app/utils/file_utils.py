"""File handling utilities — temp files, cleanup, validation."""

import os
import uuid
import shutil
from functools import wraps
from flask import current_app


def get_temp_dir() -> str:
    """Get a unique temporary directory for a single operation."""
    base = current_app.config["TEMP_FOLDER"]
    op_dir = os.path.join(base, str(uuid.uuid4()))
    os.makedirs(op_dir, exist_ok=True)
    return op_dir


def cleanup_temp_dir(temp_dir: str):
    """Remove a temporary directory and all its contents."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


def save_upload(file_storage, temp_dir: str, prefix: str = "") -> str:
    """
    Save a werkzeug FileStorage to the temp directory.

    Args:
        file_storage: The uploaded file (from request.files).
        temp_dir: Directory to save into.
        prefix: Optional prefix for the filename.

    Returns:
        Full path to the saved file.
    """
    filename = file_storage.filename or "upload"
    safe_name = f"{prefix}{uuid.uuid4().hex[:8]}_{filename}"
    path = os.path.join(temp_dir, safe_name)
    file_storage.save(path)
    return path


def get_extension(filename: str) -> str:
    """Get the lowercase file extension without the dot."""
    return os.path.splitext(filename)[1].lower().lstrip(".")


def generate_output_filename(original_name: str, suffix: str = "_stego", ext: str = None) -> str:
    """Generate a descriptive output filename."""
    name, original_ext = os.path.splitext(original_name)
    if ext:
        return f"{name}{suffix}.{ext}"
    return f"{name}{suffix}{original_ext}"
