"""
Uygulama genelinde kullanılan sabitler, yol tanımları ve çevre değişkenleri.
"""
import logging
import os
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

# --- Uygulama Kök Dizini ---
# Bu dosya app/ altında; kök dizin bir üst seviyededir.
APP_DIR = Path(__file__).parent.parent
PROJECT_ROOT = APP_DIR.parent

# --- Uygulama Kimliği ---
APP_NAME = "Proje Takip Platformu"
APP_VERSION = "0.1.0"
APP_ORGANIZATION = "ProjeTakip"


def _resolve_data_dir() -> Path:
    """Windows'ta %LOCALAPPDATA%\\ProjeTakip; env değişkeni yoksa eski konuma düşer.

    Önceki sürümler veriyi doğrudan Path.home() / ".proje_takip" içinde
    tutuyordu — Windows Gezgini nokta-prefiksli klasörleri gizlemediği için
    bu konvansiyon burada yanlış (Unix işi) ve kullanıcı home dizinini
    kirletiyordu. Gerçek dosya taşıma işlemi (veri kaybı olmadan) tek
    seferlik olarak app/di_container.py::_migrate_legacy_data_dir() içinde
    yapılır; burada sadece hedef yol hesaplanır.
    """
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_ORGANIZATION
    return Path.home() / ".proje_takip"


# --- Veri ve Yedek Dizinleri ---
LEGACY_DATA_DIR = Path.home() / ".proje_takip"
DATA_DIR = _resolve_data_dir()
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

# --- Sesli Komut Modeli ---
# Model repoya commit edilmez (~50 MB). resources/models/ .gitignore kapsamında.
# İndirme: https://alphacephei.com/vosk/models → vosk-model-small-tr-0.3
MODELS_DIR = RESOURCES_DIR / "models"
VOSK_TR_MODEL_DIR = MODELS_DIR / "vosk-model-small-tr-0.3"

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


def migrate_legacy_data_dir() -> None:
    """Eski `~/.proje_takip` veri dizinini yeni `%LOCALAPPDATA%\\ProjeTakip` konumuna taşır.

    Tek seferlik ve veri kaybetmeden yapılır (2026-07-02, Windows'ta ana dizine
    nokta-prefiksli klasör açmak yanlış konvansiyondu — Gezgin bu klasörleri
    gizlemiyor). `main.py`'de HERHANGİ bir loglama kurulumundan önce çağrılmalı:
    log dosyası bir kez açıldığında yolu değişmez, bu yüzden taşıma daha geç
    (ör. DIContainer.bootstrap() içinde) denenirse log her zaman taşıma-öncesi
    yanlış yola yazmaya devam eder (üretimde yakalandı, düzeltildi).
    """
    legacy_dir = LEGACY_DATA_DIR
    if legacy_dir == DATA_DIR or not legacy_dir.exists():
        return
    if DATABASE_PATH.exists():
        logger.warning(
            "Eski veri dizini (%s) ve yeni veri dizini (%s) ikisi de mevcut; "
            "veri kaybını önlemek için otomatik taşıma atlandı, elle kontrol gerekir.",
            legacy_dir, DATA_DIR,
        )
        return
    DATA_DIR.parent.mkdir(parents=True, exist_ok=True)
    if DATA_DIR.exists() and not _clear_stale_target_dir(legacy_dir):
        return
    _perform_move(legacy_dir)


def _clear_stale_target_dir(legacy_dir: Path) -> bool:
    """DB'siz (yarım/bozuk) bir hedef dizini temizler; başarılıysa True döner.

    DB yok (çağıran tarafta doğrulandı) ama dizin zaten var — shutil.move
    dst'yi var olan bir dizin sanıp İÇİNE taşır (istenmeyen iç içe geçme).
    Temizlik kilitli dosya yüzünden başarısız olursa move'un sessizce yanlış
    bir sonuç üretmesindense eski konuma dönülür.
    """
    shutil.rmtree(DATA_DIR, ignore_errors=True)
    if not DATA_DIR.exists():
        return True
    logger.warning(
        "Yeni veri dizini (%s) temizlenemedi (muhtemelen kilitli dosya); "
        "bu oturumda eski konum (%s) kullanılacak.",
        DATA_DIR, legacy_dir,
    )
    _fall_back_to_legacy_dir()
    return False


def _perform_move(legacy_dir: Path) -> None:
    """Eski dizini yeni konuma taşır; başarısız olursa eski konuma güvenle döner."""
    try:
        shutil.move(str(legacy_dir), str(DATA_DIR))
    except OSError as exc:
        # Kilitli dosya (ör. hâlâ çalışan bir örnek, virüs taraması) taşımayı
        # yarıda kesebilir. Veri kaybını önlemek için bu oturumda ESKİ konuma
        # dönülür — yeni (muhtemelen yarım/bozuk) hedef asla kullanılmaz.
        logger.warning(
            "Veri dizini taşınamadı (%s); bu oturumda eski konum (%s) kullanılacak, "
            "sonraki başlatmada tekrar denenecek.",
            exc, legacy_dir,
        )
        shutil.rmtree(DATA_DIR, ignore_errors=True)
        _fall_back_to_legacy_dir()
        return
    logger.info("Veri dizini taşındı: %s -> %s", legacy_dir, DATA_DIR)


def _fall_back_to_legacy_dir() -> None:
    """Taşıma başarısız olduğunda bu oturumun eski veri konumunu kullanmasını sağlar."""
    global DATA_DIR, DATABASE_PATH, BACKUPS_DIR, LOGS_DIR, DATABASE_URL, LOG_FILE
    DATA_DIR = LEGACY_DATA_DIR
    DATABASE_PATH = DATA_DIR / "proje_takip.db"
    BACKUPS_DIR = DATA_DIR / ".backups"
    LOGS_DIR = DATA_DIR / "logs"
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    LOG_FILE = LOGS_DIR / "app.log"
