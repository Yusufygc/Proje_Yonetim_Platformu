"""
Uygulama genelinde kullanılan sabitler, yol tanımları ve çevre değişkenleri.
"""
from pathlib import Path

# --- Uygulama Kök Dizini ---
APP_DIR = Path(__file__).parent
PROJECT_ROOT = APP_DIR.parent

# --- Veri ve Yedek Dizinleri ---
DATA_DIR = Path.home() / ".proje_takip"
DATABASE_PATH = DATA_DIR / "proje_takip.db"
BACKUPS_DIR = DATA_DIR / ".backups"
LOGS_DIR = DATA_DIR / "logs"

# --- Kaynak Dizinleri ---
RESOURCES_DIR = APP_DIR / "resources"
THEMES_DIR = RESOURCES_DIR / "themes"
STYLES_DIR = RESOURCES_DIR / "styles"
FONTS_DIR = RESOURCES_DIR / "fonts"
ICONS_DIR = RESOURCES_DIR / "icons"
LOCALES_DIR = RESOURCES_DIR / "locales"

# --- Uygulama Kimliği ---
APP_NAME = "Proje Takip Platformu"
APP_VERSION = "0.1.0"
APP_ORGANIZATION = "ProjeTakip"

# --- Veritabanı ---
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
ALEMBIC_MIGRATIONS_DIR = APP_DIR / "infrastructure" / "migrations"

# --- Loglama ---
LOG_FILE = LOGS_DIR / "app.log"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3

# --- UI Sabitleri ---
SIDEBAR_EXPANDED_WIDTH = 240
SIDEBAR_COLLAPSED_WIDTH = 60
ANIMATION_DURATION_MS = 300
ANIMATION_DURATION_SHORT_MS = 150


def ensure_data_dirs() -> None:
    """Uygulama başlangıcında gerekli veri dizinlerini oluşturur."""
    for directory in (DATA_DIR, BACKUPS_DIR, LOGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
