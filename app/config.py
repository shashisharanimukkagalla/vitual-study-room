import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
DEFAULT_DATABASE = f"sqlite:///{BASE_DIR / 'instance' / 'study_hall.db'}"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DATABASE)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-this-secret")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = BASE_DIR / "instance" / "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_UPLOAD_EXTENSIONS = {"pdf", "ppt", "pptx", "doc", "docx", "png", "jpg", "jpeg", "txt"}
    ALLOWED_UPLOAD_MIMES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "image/png",
        "image/jpeg",
        "text/plain",
    }
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get("SOCKETIO_CORS_ALLOWED_ORIGINS")
