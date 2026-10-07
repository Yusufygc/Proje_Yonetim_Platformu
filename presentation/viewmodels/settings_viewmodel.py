"""QML Ayarlar ve Veri Yönetimi ViewModel'i (SettingsViewModel)."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from app import config
from presentation.dimensions import FontFamily
from presentation.utils.i18n import tr

if TYPE_CHECKING:
    from app.di_container import DIContainer

logger = logging.getLogger(__name__)

_THEME_PACKAGES = [
    {"id": "slate", "name": "Slate", "color": "#678180", "dark": "dark", "light": "light"},
    {"id": "indigo", "name": "Indigo", "color": "#6366F1", "dark": "indigo_dark", "light": "indigo_light"},
    {"id": "emerald", "name": "Emerald", "color": "#10B981", "dark": "emerald_dark", "light": "emerald_light"},
    {"id": "ocean", "name": "Ocean", "color": "#2563EB", "dark": "ocean_dark", "light": "ocean_light"},
    {"id": "rose", "name": "Rose", "color": "#F43F5E", "dark": "rose_dark", "light": "rose_light"},
    {"id": "violet", "name": "Violet", "color": "#8B5CF6", "dark": "violet_dark", "light": "violet_light"},
]

_FONT_CHOICES = ["Plus Jakarta Sans", "Inter", "Roboto", "Open Sans", "Segoe UI"]


class SettingsViewModel(QObject):
    """Tema, font, dil ve veri dışa aktarma ayarları köprüsü."""

    themeChanged = Signal()
    fontChanged = Signal()
    languageChanged = Signal()

    def __init__(self, container: DIContainer, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._container = container
        self._theme = container.theme
        self._prefs = container.prefs
        self._strings = container.strings
        self._controller = container.settings_controller
        self._event_bus = container.event_bus

        self._active_package: str = self._resolve_current_package()
        self._font_family: str = self._prefs.load_font_family() or FontFamily.UI

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._theme.theme_changed.connect(self._on_theme_changed)
        self._controller.export_completed.connect(self._on_export_completed)
        self._controller.error_occurred.connect(self._on_error)

    def _resolve_current_package(self) -> str:
        current = self._theme.current_theme
        for pkg in _THEME_PACKAGES:
            if current in (pkg["dark"], pkg["light"]):
                return pkg["id"]
        return "slate"

    def _on_theme_changed(self, _theme_name: str) -> None:
        self._active_package = self._resolve_current_package()
        self.themeChanged.emit()

    # ── Slots ──────────────────────────────────────────────────────────────

    @Slot(bool)
    def setMode(self, is_dark: bool) -> None:
        mode = "dark" if is_dark else "light"
        slot_theme = (
            self._prefs.load_dark_slot()
            if is_dark
            else self._prefs.load_light_slot()
        )
        self._prefs.save_active_mode(mode)
        self._prefs.save_theme(slot_theme)
        self._theme.switch_theme(slot_theme)
        self.themeChanged.emit()

    @Slot(str)
    def setThemePackage(self, package_id: str) -> None:
        target = next((p for p in _THEME_PACKAGES if p["id"] == package_id), None)
        if not target:
            return
        is_light = self._prefs.load_active_mode() == "light"
        stem = target["light"] if is_light else target["dark"]
        if is_light:
            self._prefs.save_light_slot(stem)
        else:
            self._prefs.save_dark_slot(stem)
        self._prefs.save_theme(stem)
        self._theme.switch_theme(stem)
        self._active_package = package_id
        self.themeChanged.emit()

    @Slot(str)
    def setFontFamily(self, family: str) -> None:
        self._font_family = family
        self._prefs.save_font_family(family)
        app = QApplication.instance()
        if app:
            app.setFont(QFont(family, FontFamily.DEFAULT_SIZE))
        self.fontChanged.emit()

    @Slot(str)
    def setLanguage(self, lang_code: str) -> None:
        if lang_code in ("tr", "en") and lang_code != self._strings.current_language:
            self._prefs.save_language(lang_code)
            self._strings.set_language(lang_code)
            self.languageChanged.emit()

    @Slot(str)
    def exportToJson(self, target_path: str = "") -> None:
        path = target_path or self.getDefaultExportPath()
        self._controller.export_to_json(path)

    @Slot(result=str)
    def getDefaultExportPath(self) -> str:
        downloads = Path.home() / "Downloads"
        dest_dir = downloads if downloads.exists() else Path.home()
        return str(dest_dir / "proje_takip_export.json")

    def _on_export_completed(self, path: str) -> None:
        if self._event_bus:
            self._event_bus.publish(
                "toast.show",
                message=tr(
                    "settings_export_toast",
                    "Veriler başarıyla dışa aktarıldı: {path}",
                ).format(path=path),
                type_="success",
            )

    def _on_error(self, err: str) -> None:
        if self._event_bus:
            self._event_bus.publish("toast.show", message=err, type_="error")

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(bool, notify=themeChanged)
    def isDark(self) -> bool:
        return self._prefs.load_active_mode() != "light"

    @Property(str, notify=themeChanged)
    def activePackage(self) -> str:
        return self._active_package

    @Property("QVariantList", constant=True)
    def themePackages(self) -> list[dict[str, Any]]:
        return _THEME_PACKAGES

    @Property(str, notify=fontChanged)
    def fontFamily(self) -> str:
        return self._font_family

    @Property("QVariantList", constant=True)
    def fontFamilies(self) -> list[str]:
        return _FONT_CHOICES

    @Property(str, notify=languageChanged)
    def currentLanguage(self) -> str:
        return self._strings.current_language

    @Property(str, constant=True)
    def appName(self) -> str:
        return config.APP_NAME

    @Property(str, constant=True)
    def appVersion(self) -> str:
        return config.APP_VERSION
