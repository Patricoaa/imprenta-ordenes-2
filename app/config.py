import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER','postgres')}:{os.getenv('POSTGRES_PASSWORD','postgres')}@{os.getenv('DB_HOST','db')}:{os.getenv('DB_PORT','5432')}/{os.getenv('POSTGRES_DB','printshop')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB

    # SMTP
    SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "no-reply@example.com")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


def get_config(name: str | None):
    if not name:
        env = os.getenv("FLASK_ENV", "development").lower()
        name = "production" if env == "production" else "development"
    return DevelopmentConfig if name == "development" else ProductionConfig