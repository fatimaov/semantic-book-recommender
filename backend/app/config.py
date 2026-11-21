import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=False)


def _as_bool(value: str | None) -> bool:
    return value is not None and value.lower() in {"1", "true", "yes", "on"}


def _sqlalchemy_database_uri(value: str | None) -> str | None:
    if not value:
        return value
    url = make_url(value)
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
    return url.render_as_string(hide_password=False)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    APP_ENV = os.getenv("APP_ENV", "production").lower()
    SEARCH_LOGGING_ENABLED = APP_ENV == "production"
    SUPABASE_DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = _sqlalchemy_database_uri(SUPABASE_DATABASE_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    FLASK_DEBUG = _as_bool(os.getenv("FLASK_DEBUG"))
    DEBUG = FLASK_DEBUG
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL")
