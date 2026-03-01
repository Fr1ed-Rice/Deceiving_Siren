"""
Encode routes — LSB and Spectrogram encoding endpoints.
"""

import io
import os
from flask import Blueprint, request, send_file, jsonify

from ..services import lsb_stego, spectrogram_stego
from ..utils.audio_utils import convert_to_wav, convert_from_wav
from ..utils.file_utils import (
    get_temp_dir,
    cleanup_temp_dir,
    save_upload,
    get_extension,
    generate_output_filename,
)

encode_bp = Blueprint("encode", __name__)


@encode_bp.route("/encode", methods=["POST"])
def encode_lsb():
    """
    LSB-encode a payload file into an audio carrier.

    Form data:
        carrier: Audio file (WAV, MP3, etc.)
        payload: Any file to hide
        output_format: (optional) wav, flac, mp3, ogg (default: wav)
    """
    temp_dir = get_temp_dir()

    try:
        # Validate uploads
        if "carrier" not in request.files:
            return jsonify({"error": "Missing 'carrier' audio file."}), 400
        if "payload" not in request.files:
            return jsonify({"error": "Missing 'payload' file to hide."}), 400

        carrier_file = request.files["carrier"]
        payload_file = request.files["payload"]
        output_format = request.form.get("output_format", "wav").lower()

        if not carrier_file.filename:
            return jsonify({"error": "Carrier file has no filename."}), 400
        if not payload_file.filename:
            return jsonify({"error": "Payload file has no filename."}), 400

        # Validate output format
        valid_formats = {"wav", "flac", "mp3", "ogg"}
        if output_format not in valid_formats:
            return jsonify({"error": f"Invalid output format. Choose from: {valid_formats}"}), 400

        # Save uploads
        carrier_path = save_upload(carrier_file, temp_dir, prefix="carrier_")
        payload_path = save_upload(payload_file, temp_dir, prefix="payload_")

        # Convert carrier to WAV if needed
        carrier_wav = os.path.join(temp_dir, "carrier_converted.wav")
        convert_to_wav(carrier_path, carrier_wav)

        # Encode
        stego_wav = os.path.join(temp_dir, "stego_output.wav")
        metadata = lsb_stego.encode(
            carrier_path=carrier_wav,
            payload_path=payload_path,
            output_path=stego_wav,
            payload_filename=payload_file.filename,
        )

        # Convert to desired output format
        output_name = generate_output_filename(carrier_file.filename, "_stego", output_format)
        final_output = os.path.join(temp_dir, output_name)

        format_info = convert_from_wav(stego_wav, final_output, output_format)

        # Read into memory before cleanup so send_file doesn't race with deletion
        buf = io.BytesIO()
        with open(final_output, "rb") as f:
            buf.write(f.read())
        buf.seek(0)

        cleanup_temp_dir(temp_dir)

        return send_file(
            buf,
            as_attachment=True,
            download_name=output_name,
            mimetype=_get_audio_mimetype(output_format),
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Encoding failed: {str(e)}"}), 500
    finally:
        cleanup_temp_dir(temp_dir)


@encode_bp.route("/encode-spectrogram", methods=["POST"])
def encode_spectrogram():
    """
    Hide data in the spectrogram of an audio file.

    Form data:
        carrier: Audio file (WAV, MP3, etc.)
        payload: File to hide (any format) OR image file
        mode: 'data' (hide any file) or 'image' (hide visible image in spectrogram)
        intensity: (optional) Embedding strength 0.0-1.0 (default: 0.3 for data, 0.5 for image)
        output_format: (optional) wav, flac, mp3, ogg (default: wav)
    """
    temp_dir = get_temp_dir()

    try:
        if "carrier" not in request.files:
            return jsonify({"error": "Missing 'carrier' audio file."}), 400
        if "payload" not in request.files:
            return jsonify({"error": "Missing 'payload' file."}), 400

        carrier_file = request.files["carrier"]
        payload_file = request.files["payload"]
        mode = request.form.get("mode", "data")
        output_format = request.form.get("output_format", "wav").lower()

        intensity = float(request.form.get("intensity", "0.3" if mode == "data" else "0.5"))
        intensity = max(0.05, min(1.0, intensity))  # Clamp

        # Save uploads
        carrier_path = save_upload(carrier_file, temp_dir, prefix="carrier_")
        payload_path = save_upload(payload_file, temp_dir, prefix="payload_")

        # Convert carrier to WAV
        carrier_wav = os.path.join(temp_dir, "carrier_converted.wav")
        convert_to_wav(carrier_path, carrier_wav)

        # Encode
        stego_wav = os.path.join(temp_dir, "stego_spectrogram.wav")

        if mode == "image":
            metadata = spectrogram_stego.encode_image_in_spectrogram(
                carrier_path=carrier_wav,
                image_path=payload_path,
                output_path=stego_wav,
                intensity=intensity,
            )
        else:
            metadata = spectrogram_stego.encode_data_in_spectrogram(
                carrier_path=carrier_wav,
                payload_path=payload_path,
                output_path=stego_wav,
                payload_filename=payload_file.filename,
                intensity=intensity,
            )

        # Convert to output format
        output_name = generate_output_filename(carrier_file.filename, "_spectro", output_format)
        final_output = os.path.join(temp_dir, output_name)
        convert_from_wav(stego_wav, final_output, output_format)

        buf = io.BytesIO()
        with open(final_output, "rb") as f:
            buf.write(f.read())
        buf.seek(0)

        cleanup_temp_dir(temp_dir)

        return send_file(
            buf,
            as_attachment=True,
            download_name=output_name,
            mimetype=_get_audio_mimetype(output_format),
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Spectrogram encoding failed: {str(e)}"}), 500
    finally:
        cleanup_temp_dir(temp_dir)


def _get_audio_mimetype(fmt: str) -> str:
    """Get MIME type for an audio format."""
    return {
        "wav": "audio/wav",
        "flac": "audio/flac",
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
    }.get(fmt, "application/octet-stream")
