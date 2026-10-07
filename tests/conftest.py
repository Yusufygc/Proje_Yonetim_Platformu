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
