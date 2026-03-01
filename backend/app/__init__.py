import os
from flask import Flask
from flask_cors import CORS

from .config import config_map


def create_app(config_name=None):
    """Flask application factory."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map["development"]))

    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure upload and temp directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["TEMP_FOLDER"], exist_ok=True)

    # Register blueprints
    from .routes.encode import encode_bp
    from .routes.decode import decode_bp
    from .routes.video import video_bp
    from .routes.health import health_bp

    app.register_blueprint(encode_bp, url_prefix="/api")
    app.register_blueprint(decode_bp, url_prefix="/api")
    app.register_blueprint(video_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")

    # Register error handlers
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """Register global error handlers."""

    @app.errorhandler(413)
    def request_entity_too_large(error):
        max_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        return {
            "error": "File too large",
            "message": f"Maximum upload size is {max_mb}MB.",
        }, 413

    @app.errorhandler(400)
    def bad_request(error):
        return {
            "error": "Bad request",
            "message": str(error.description) if hasattr(error, "description") else "Invalid request.",
        }, 400

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found", "message": "The requested resource was not found."}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again.",
        }, 500
