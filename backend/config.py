"""
CareerAI — Application Configuration
Loads all settings from environment variables (.env) with safe local defaults.
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

# Load variables from backend/.env into the process environment.
load_dotenv()

# Absolute path to the backend directory, so uploads resolve correctly
# no matter where the app is launched from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Central configuration consumed by app.config.from_object(Config)."""

    # ------------------------------------------------------------------
    # MongoDB Atlas
    # ------------------------------------------------------------------
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "career_guidance_db")

    # ------------------------------------------------------------------
    # JWT Authentication
    # ------------------------------------------------------------------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # ------------------------------------------------------------------
    # CORS
    # Comma-separated list in .env, e.g. "http://127.0.0.1:5500,http://localhost:5500"
    # Defaults cover Live Server and direct file serving during development.
    # ------------------------------------------------------------------
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:5501,http://localhost:5501,null",
        ).split(",")
        if origin.strip()
    ]

    # ------------------------------------------------------------------
    # Resume Uploads
    # ------------------------------------------------------------------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {"pdf"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB hard limit (triggers 413)

    # ------------------------------------------------------------------
    # Flask
    # ------------------------------------------------------------------
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    # ------------------------------------------------------------------
    # Contact form mail delivery
    # ------------------------------------------------------------------
    CONTACT_RECIPIENT_EMAIL = os.getenv(
        "CONTACT_RECIPIENT_EMAIL", "232u1a33b1@gist.edu.in"
    )
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER or "no-reply@careerai.local")
