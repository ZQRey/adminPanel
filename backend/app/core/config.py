import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    PROJECT_NAME: str = "Sci-Fi HUD Personal Dashboard"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CYBER_HUD_SUPER_SECRET_KEY_9847291038472910")
    FERNET_KEY: str = os.getenv("FERNET_KEY", "jZ4OqKvhQ86a3D2x_r1PZ4wK6y0f0U6A1p2B3C4D5E6=")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR / 'dashboard.db'}")
    PLUGINS_DIR: Path = Path(os.getenv("PLUGINS_DIR", str(BASE_DIR / "plugins")))
    STATIC_DIR: Path = Path(os.getenv("STATIC_DIR", str(BASE_DIR / "static")))

settings = Settings()
settings.PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)

if "sqlite" in settings.DATABASE_URL:
    try:
        db_path = settings.DATABASE_URL.split(":///")[-1]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
