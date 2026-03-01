"""
Video steganography routes — encode/decode via video's audio track.
"""

import os
from flask import Blueprint, request, send_file, jsonify

from ..services import lsb_stego, spectrogram_stego, video_audio
from ..utils.audio_utils import convert_to_wav
from ..utils.file_utils import (
    get_temp_dir,
    cleanup_temp_dir,
    save_upload,
    generate_output_filename,
)

video_bp = Blueprint("video", __name__)


@video_bp.route("/encode-video", methods=["POST"])
def encode_video():
    """
    Hide data in a video's audio track using LSB steganography.

    Pipeline: extract audio → LSB encode → remux back into video.

    Form data:
        video: Video file (MP4, AVI, MKV, etc.)
        payload: Any file to hide
        method: (optional) 'lsb' or 'spectrogram' (default: 'lsb')
        intensity: (optional) For spectrogram method, 0.0-1.0 (default: 0.3)
    """
    temp_dir = get_temp_dir()

    try:
        if "video" not in request.files:
            return jsonify({"error": "Missing 'video' file."}), 400
        if "payload" not in request.files:
            return jsonify({"error": "Missing 'payload' file to hide."}), 400

        video_file = request.files["video"]
        payload_file = request.files["payload"]
        method = request.form.get("method", "lsb").lower()

        if not video_file.filename:
            return jsonify({"error": "Video file has no filename."}), 400
        if not payload_file.filename:
            return jsonify({"error": "Payload file has no filename."}), 400

        # Save uploads
        video_path = save_upload(video_file, temp_dir, prefix="video_")
        payload_path = save_upload(payload_file, temp_dir, prefix="payload_")

        # Extract audio from video
        extracted_audio = os.path.join(temp_dir, "extracted_audio.wav")
        extract_info = video_audio.extract_audio(video_path, extracted_audio)

        # Apply steganography to extracted audio
        stego_audio = os.path.join(temp_dir, "stego_audio.wav")

        if method == "spectrogram":
            intensity = float(request.form.get("intensity", "0.3"))
            spectrogram_stego.encode_data_in_spectrogram(
                carrier_path=extracted_audio,
                payload_path=payload_path,
                output_path=stego_audio,
                payload_filename=payload_file.filename,
                intensity=intensity,
            )
        else:
            lsb_stego.encode(
                carrier_path=extracted_audio,
                payload_path=payload_path,
                output_path=stego_audio,
                payload_filename=payload_file.filename,
            )

        # Remux modified audio back into video
        output_name = generate_output_filename(video_file.filename, "_stego")
        output_video = os.path.join(temp_dir, output_name)

        video_audio.remux_audio_into_video(
            original_video_path=video_path,
            modified_audio_path=stego_audio,
            output_video_path=output_video,
        )

        # Determine mimetype from extension
        ext = os.path.splitext(video_file.filename)[1].lower()
        mimetype = {
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mkv": "video/x-matroska",
            ".mov": "video/quicktime",
            ".webm": "video/webm",
        }.get(ext, "video/mp4")

        return send_file(
            output_video,
            as_attachment=True,
            download_name=output_name,
            mimetype=mimetype,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Video encoding failed: {str(e)}"}), 500
    finally:
        cleanup_temp_dir(temp_dir)


@video_bp.route("/decode-video", methods=["POST"])
def decode_video():
    """
    Extract hidden data from a video's audio track.

    Pipeline: extract audio → LSB decode → return extracted file.

    Form data:
        video: Video file containing hidden data
        method: (optional) 'lsb' or 'spectrogram' (default: 'lsb')
    """
    temp_dir = get_temp_dir()

    try:
        if "video" not in request.files:
            return jsonify({"error": "Missing 'video' file."}), 400

        video_file = request.files["video"]
        method = request.form.get("method", "lsb").lower()

        if not video_file.filename:
            return jsonify({"error": "Video file has no filename."}), 400

        # Save upload
        video_path = save_upload(video_file, temp_dir, prefix="video_")

        # Extract audio
        extracted_audio = os.path.join(temp_dir, "extracted_audio.wav")
        video_audio.extract_audio(video_path, extracted_audio)

        if method == "spectrogram":
            # Return spectrogram image
            output_image = os.path.join(temp_dir, "spectrogram.png")
            spectrogram_stego.extract_spectrogram_image(
                audio_path=extracted_audio,
                output_image_path=output_image,
            )
            return send_file(
                output_image,
                as_attachment=True,
                download_name="video_spectrogram.png",
                mimetype="image/png",
            )
        else:
            # LSB decode
            output_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(output_dir, exist_ok=True)

            result = lsb_stego.decode(
                stego_path=extracted_audio,
                output_dir=output_dir,
            )

            return send_file(
                result["output_path"],
                as_attachment=True,
                download_name=result["filename"],
            )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Video decoding failed: {str(e)}"}), 500
    finally:
        cleanup_temp_dir(temp_dir)
