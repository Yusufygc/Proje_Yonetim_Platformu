"""Çekim sırasında gerçek kullanıcı verisinin ve ayarlarının korunması.

`prepare()` uygulama modülleri içe aktarılmadan ÖNCE çağrılmalıdır: `app.config` veri
dizinini içe aktarım anında bir kez çözer.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def prepare(root: Path) -> None:
    """Veri dizinini ve tercih deposunu `root` altına yönlendirir."""
    if "app.config" in sys.modules:
        raise RuntimeError("prepare() uygulama içe aktarılmadan önce çağrılmalı")
    home = root / "home"
    settings = root / "settings"
    home.mkdir(parents=True, exist_ok=True)
    settings.mkdir(parents=True, exist_ok=True)

    os.environ["PROJE_TAKIP_HOME"] = str(home)
    os.environ["PROJE_TAKIP_NO_UPDATE_CHECK"] = "1"
    # PreferenceManager kayıt defterine değil, defaultFormat() ile bu INI dosyasına yazar.
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(settings))

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
