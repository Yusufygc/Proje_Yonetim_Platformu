"""
QSettings aracılığıyla pencere boyutu, konum ve son kullanılan proje ID'si gibi
kullanıcı tercihlerini kalıcı olarak saklayan Singleton.
"""
from __future__ import annotations

import logging

from PySide6.QtCore import QByteArray, QSettings

import config

logger = logging.getLogger(__name__)


class PreferenceManager:
    """
    Kullanıcı tercihlerini OS kayıt defterine (Windows) veya INI'ye kaydeden Singleton.
    """

    _instance: PreferenceManager | None = None

    def __init__(self) -> None:
        self._settings = QSettings(config.APP_ORGANIZATION, config.APP_NAME)

    @classmethod
    def instance(cls) -> "PreferenceManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def save_window_geometry(self, geometry: QByteArray) -> None:
        self._settings.setValue("window/geometry", geometry)

    def load_window_geometry(self) -> QByteArray | None:
        return self._settings.value("window/geometry")  # type: ignore[return-value]

    def save_last_project_id(self, project_id: int) -> None:
        self._settings.setValue("session/last_project_id", project_id)

    def load_last_project_id(self) -> int | None:
        value = self._settings.value("session/last_project_id")
        return int(value) if value is not None else None

    def save_theme(self, theme_name: str) -> None:
        self._settings.setValue("ui/theme", theme_name)

    def load_theme(self) -> str:
        return str(self._settings.value("ui/theme", "dark"))

    def save_language(self, lang_code: str) -> None:
        self._settings.setValue("ui/language", lang_code)

    def load_language(self) -> str:
        return str(self._settings.value("ui/language", "tr"))

    def save_sidebar_collapsed(self, collapsed: bool) -> None:
        self._settings.setValue("ui/sidebar_collapsed", collapsed)

    def load_sidebar_collapsed(self) -> bool:
        return bool(self._settings.value("ui/sidebar_collapsed", False))

    # ── Tema Slot Sistemi ────────────────────────────────────────────────────

    def save_dark_slot(self, theme_name: str) -> None:
        self._settings.setValue("ui/dark_slot", theme_name)

    def load_dark_slot(self) -> str:
        return str(self._settings.value("ui/dark_slot", "dark"))

    def save_light_slot(self, theme_name: str) -> None:
        self._settings.setValue("ui/light_slot", theme_name)

    def load_light_slot(self) -> str:
        return str(self._settings.value("ui/light_slot", "light"))

    def save_active_mode(self, mode: str) -> None:
        self._settings.setValue("ui/active_mode", mode)

    def load_active_mode(self) -> str:
        value = self._settings.value("ui/active_mode")
        if value is not None:
            return str(value)
        # Eski kurulumlardan göç: tema adından mod çıkar
        return "light" if self.load_theme() == "light" else "dark"

    # ── Font Tercihleri ──────────────────────────────────────────────────────

    def save_font_family(self, family: str) -> None:
        self._settings.setValue("ui/font_family", family)

    def load_font_family(self) -> str:
        return str(self._settings.value("ui/font_family", ""))

    def save_font_size(self, size: int) -> None:
        self._settings.setValue("ui/font_size", size)

    def load_font_size(self) -> int:
        value = self._settings.value("ui/font_size")
        return int(value) if value is not None else 10
