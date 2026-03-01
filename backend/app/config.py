import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_SIZE_MB", 80)) * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
    TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tmp")

    # Allowed extensions for carrier files
    ALLOWED_AUDIO_EXTENSIONS = {"wav", "mp3", "ogg", "flac", "aac", "m4a", "wma"}
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mkv", "mov", "webm", "flv", "wmv"}
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "gif", "webp"}

    # Output format options
    LOSSLESS_FORMATS = {"wav", "flac"}
    LOSSY_FORMATS = {"mp3", "ogg"}

    # Spectrogram defaults
    SPECTROGRAM_N_FFT = 2048
    SPECTROGRAM_HOP_LENGTH = 512


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = "production"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
