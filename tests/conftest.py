"""
Pytest fixture'ları — RAM üzerinde çalışan test veritabanı ve DI container.
Her test bağımsız, temiz bir veritabanıyla başlar.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
from PySide6.QtCore import QSettings

# Test çalışmasında proje kökünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.database.db_manager import DatabaseManager

# QSettings varsayılan olarak Windows kayıt defterine yazar; testler tema, kenar çubuğu ve pencere
# tercihlerini değiştirdiği için kullanıcının gerçek ayarları bozuluyordu. Testler geçici bir ini
# dosyası kullanır. PreferenceManager ilk oluşturulmadan önce ayarlanmalı, bu yüzden import anında yapılır.
_SETTINGS_DIR = tempfile.mkdtemp(prefix="proje_takip_test_settings_")
QSettings.setDefaultFormat(QSettings.Format.IniFormat)
QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, _SETTINGS_DIR)


def _redirect_data_dir(root: Path) -> None:
    """Veri, log, yedek ve görsel yollarını geçici dizine yönlendirir.

    DIContainer.bootstrap() log dosyasını açıyor, MemoViewModel panodaki görseli kaydediyor; bunlar
    gerçek %LOCALAPPDATA%\\ProjeTakip altına yazınca kullanıcının log geçmişi test gürültüsüyle
    dönüp siliniyor ve veri klasörü test görselleriyle doluyordu.
    """
    from app import config

    config.DATA_DIR = root
    config.DATABASE_PATH = root / "proje_takip.db"
    config.DATABASE_URL = f"sqlite:///{config.DATABASE_PATH}"
    config.BACKUPS_DIR = root / ".backups"
    config.LOGS_DIR = root / "logs"
    config.LOG_FILE = config.LOGS_DIR / "app.log"
    config.MEMO_IMAGES_DIR = root / "memo_images"


_redirect_data_dir(Path(tempfile.mkdtemp(prefix="proje_takip_test_data_")))


@pytest.fixture(scope="function")
def test_db() -> DatabaseManager:
    """
    Her test fonksiyonu için ayrı, bellek-içi SQLite veritabanı döndürür.
    Test sonunda otomatik temizlenir.
    """
    # Singleton state'i sıfırla
    DatabaseManager._instance = None

    db = DatabaseManager.instance("sqlite:///:memory:")
    db.create_all_tables()
    return db
