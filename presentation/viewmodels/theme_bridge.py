"""QML için Tema ve Renk Paleti Köprüsü."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from core.managers.preference_manager import PreferenceManager
from core.managers.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class ThemeBridge(QObject):
    """
    QML tarafına dinamik renk paleti ve tema değiştirme işlevleri sunar.
    Tema değiştiğinde themeChanged sinyali ile tüm bağlı QML property'leri güncellenir.
    """

    themeChanged = Signal()

    def __init__(
        self,
        theme_mgr: ThemeManager,
        prefs: PreferenceManager,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._theme_mgr = theme_mgr
        self._prefs = prefs
        self._theme_mgr.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str) -> None:
        logger.debug("QML ThemeBridge tema değişimi algıladı: %s", theme_name)  # l10n: log
        self.themeChanged.emit()

    @Property(str, notify=themeChanged)
    def currentTheme(self) -> str:
        return self._theme_mgr.current_theme

    @Property(bool, notify=themeChanged)
    def isDark(self) -> bool:
        return self._prefs.load_active_mode() == "dark"

    @Property("QVariantMap", notify=themeChanged)
    def colors(self) -> dict[str, Any]:
        """Tüm tema token'larını sözlük olarak döndürür."""
        palette: dict[str, Any] = getattr(self._theme_mgr, "_palette", {})
        return dict(palette)

    @Property(str, notify=themeChanged)
    def background(self) -> str:
        return self._theme_mgr.color("background")

    @Property(str, notify=themeChanged)
    def surface(self) -> str:
        return self._theme_mgr.color("surface")

    @Property(str, notify=themeChanged)
    def surfaceRaised(self) -> str:
        return self._theme_mgr.color("surface_raised")

    @Property(str, notify=themeChanged)
    def textPrimary(self) -> str:
        return self._theme_mgr.color("text_primary")

    @Property(str, notify=themeChanged)
    def textSecondary(self) -> str:
        return self._theme_mgr.color("text_secondary")

    @Property(str, notify=themeChanged)
    def textMuted(self) -> str:
        return self._theme_mgr.color("text_muted")

    @Property(str, notify=themeChanged)
    def accentStart(self) -> str:
        return self._theme_mgr.color("accent_start")

    @Property(str, notify=themeChanged)
    def accentEnd(self) -> str:
        return self._theme_mgr.color("accent_end")

    @Property(str, notify=themeChanged)
    def border(self) -> str:
        return self._theme_mgr.color("border")

    @Property(str, notify=themeChanged)
    def sidebarBg(self) -> str:
        return self._theme_mgr.color("sidebar_bg")

    @Property(str, notify=themeChanged)
    def sidebarActive(self) -> str:
        return self._theme_mgr.color("sidebar_active")

    @Property(str, notify=themeChanged)
    def sidebarText(self) -> str:
        return self._theme_mgr.color("sidebar_text")

    @Property(str, notify=themeChanged)
    def sidebarTextActive(self) -> str:
        return self._theme_mgr.color("sidebar_text_active")

    @Property(str, notify=themeChanged)
    def sidebarHoverBg(self) -> str:
        return self._theme_mgr.color("sidebar_hover_bg")

    @Property(str, notify=themeChanged)
    def sidebarActiveBg(self) -> str:
        return self._theme_mgr.color("sidebar_active_bg")

    @Property(str, notify=themeChanged)
    def success(self) -> str:
        return self._theme_mgr.color("success")

    @Property(str, notify=themeChanged)
    def warning(self) -> str:
        return self._theme_mgr.color("warning")

    @Property(str, notify=themeChanged)
    def danger(self) -> str:
        return self._theme_mgr.color("danger")

    @Property(str, notify=themeChanged)
    def iconOnAccent(self) -> str:
        return self._theme_mgr.color("icon_on_accent")

    @Property(str, notify=themeChanged)
    def surfaceHover(self) -> str:
        return self._theme_mgr.color("surface_raised")

    @Property(str, notify=themeChanged)
    def accentHover(self) -> str:
        return self._theme_mgr.color("accent_end")

    @Slot(str, result=str)
    def color(self, token: str) -> str:
        """İstenen token rengini döndürür."""
        return self._theme_mgr.color(token)

    @Slot()
    def toggleTheme(self) -> None:
        """Karanlık ve aydınlık mod arasında geçiş yapar."""
        current_mode = self._prefs.load_active_mode()
        if current_mode == "dark":
            next_mode = "light"
            next_theme = self._prefs.load_light_slot()
        else:
            next_mode = "dark"
            next_theme = self._prefs.load_dark_slot()

        self._prefs.save_active_mode(next_mode)
        self._prefs.save_theme(next_theme)
        self._theme_mgr.switch_theme(next_theme)

    @Slot(str)
    def switchTheme(self, theme_name: str) -> None:
        """Belirtilen temayı aktif yapar."""
        self._theme_mgr.switch_theme(theme_name)
        self._prefs.save_theme(theme_name)
