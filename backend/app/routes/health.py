"""Health check endpoint."""

from flask import Blueprint

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Simple health check."""
    return {"status": "ok", "service": "deceiving-siren-api", "version": "1.0.0"}
