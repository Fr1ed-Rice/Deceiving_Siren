"""
Decode routes — LSB and Spectrogram decoding endpoints.
"""

import io
import os
import traceback
from flask import Blueprint, request, send_file, jsonify

from ..services import lsb_stego, spectrogram_stego
from ..utils.audio_utils import convert_to_wav
from ..utils.file_utils import (
    get_temp_dir,
    cleanup_temp_dir,
    save_upload,
)

decode_bp = Blueprint("decode", __name__)


@decode_bp.route("/decode", methods=["POST"])
def decode_lsb():
    """
    Extract hidden data from a steganographic audio file (LSB).

    Form data:
        audio: The steganographic audio file (WAV recommended)
    """
    temp_dir = get_temp_dir()

    try:
        if "audio" not in request.files:
            return jsonify({"error": "Missing 'audio' file."}), 400

        audio_file = request.files["audio"]
        if not audio_file.filename:
            return jsonify({"error": "Audio file has no filename."}), 400

        # Save upload
        audio_path = save_upload(audio_file, temp_dir, prefix="stego_")

        # Convert to WAV if needed
        audio_wav = os.path.join(temp_dir, "stego_converted.wav")
        convert_to_wav(audio_path, audio_wav)

        # Decode
        output_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(output_dir, exist_ok=True)

        result = lsb_stego.decode(
            stego_path=audio_wav,
            output_dir=output_dir,
        )

        buf = io.BytesIO()
        with open(result["output_path"], "rb") as f:
            buf.write(f.read())
        buf.seek(0)

        cleanup_temp_dir(temp_dir)

        return send_file(
            buf,
            as_attachment=True,
            download_name=result["filename"],
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Decoding failed: {str(e)}"}), 500
    finally:
        cleanup_temp_dir(temp_dir)


@decode_bp.route("/decode-spectrogram", methods=["POST"])
def decode_spectrogram():
    """
    Extract the spectrogram from an audio file as a PNG image.

    This reveals any data hidden in the frequency domain.

    Form data:
        audio: The audio file to analyze
    """
    temp_dir = get_temp_dir()

    try:
        if "audio" not in request.files:
            return jsonify({"error": "Missing 'audio' file."}), 400

        audio_file = request.files["audio"]
        if not audio_file.filename:
            return jsonify({"error": "Audio file has no filename."}), 400

        # Save upload
        audio_path = save_upload(audio_file, temp_dir, prefix="spectro_")

        # Convert to WAV
        audio_wav = os.path.join(temp_dir, "spectro_converted.wav")
        convert_to_wav(audio_path, audio_wav)

        # Extract spectrogram
        output_image = os.path.join(temp_dir, "spectrogram.png")
        result = spectrogram_stego.extract_spectrogram_image(
            audio_path=audio_wav,
            output_image_path=output_image,
        )

        buf = io.BytesIO()
        with open(output_image, "rb") as f:
            buf.write(f.read())
        buf.seek(0)

        cleanup_temp_dir(temp_dir)

        return send_file(
            buf,
            as_attachment=True,
            download_name="spectrogram.png",
            mimetype="image/png",
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Spectrogram extraction failed: {str(e)}"}), 500
    finally:
        cleanup_temp_dir(temp_dir)
