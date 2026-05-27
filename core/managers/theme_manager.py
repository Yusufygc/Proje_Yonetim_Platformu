"""
Dark/Light renk paletlerini yöneten ve QSS üretimini merkezi olarak sağlayan Singleton.
14_PREMIUM_UI_UX_TASARIM_PLANI.md'deki renk standartları burada uygulanır.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ThemeManager:
    """
    Uygulama temasını yöneten Singleton sınıf.

    Paleti JSON dosyasından yükler; renk ve QSS erişimini merkezi hale getirir.
    """

    _instance: ThemeManager | None = None

    def __init__(self, themes_dir: Path) -> None:
        self._themes_dir = themes_dir
        self._palette: dict[str, Any] = {}
        self._current_theme = "dark"
        self._load_theme(self._current_theme)

    @classmethod
    def instance(cls, themes_dir: Path | None = None) -> "ThemeManager":
        if cls._instance is None:
            if themes_dir is None:
                raise RuntimeError("ThemeManager ilk çağrıda themes_dir gerektirir.")
            cls._instance = cls(themes_dir)
        return cls._instance

    def _load_theme(self, theme_name: str) -> None:
        """Belirtilen tema dosyasını yükler; bulunamazsa gömülü varsayılanı kullanır."""
        theme_file = self._themes_dir / f"{theme_name}.json"
        if theme_file.exists():
            with open(theme_file, encoding="utf-8") as f:
                self._palette = json.load(f)
            logger.info("Tema yüklendi: %s", theme_file)
        else:
            logger.warning("Tema dosyası bulunamadı (%s), varsayılan kullanılıyor.", theme_file)
            self._palette = self._default_dark_palette()

    def switch_theme(self, theme_name: str) -> None:
        """Temayı çalışma zamanında değiştirir."""
        self._current_theme = theme_name
        self._load_theme(theme_name)

    def color(self, key: str) -> str:
        """Palet sözlüğünden renk kodu döndürür."""
        return str(self._palette.get(key, "#FFFFFF"))

    def build_global_qss(self) -> str:
        """Tüm uygulama için merkezi QSS stil dizgesini üretir."""
        p = self._palette
        bg = p.get("background", "#12141A")
        surface = p.get("surface", "#1C1F26")
        text_primary = p.get("text_primary", "#E8EAF0")
        text_secondary = p.get("text_secondary", "#8B8FA8")
        accent_start = p.get("accent_start", "#6366F1")
        accent_end = p.get("accent_end", "#8B5CF6")
        border = p.get("border", "#2A2D38")
        scrollbar_bg = p.get("scrollbar_bg", "#1C1F26")
        scrollbar_handle = p.get("scrollbar_handle", "#3A3D4A")

        return f"""
QWidget {{
    background-color: {bg};
    color: {text_primary};
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 13px;
    border: none;
    outline: none;
}}
QMainWindow {{
    background-color: {bg};
}}
QFrame {{
    background-color: transparent;
}}
QLabel {{
    background-color: transparent;
    color: {text_primary};
}}
QLabel[secondary="true"] {{
    color: {text_secondary};
}}
QPushButton {{
    background-color: {surface};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {accent_start};
    border-color: {accent_start};
}}
QPushButton[primary="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {accent_start}, stop:1 {accent_end});
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
}}
QPushButton[primary="true"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {accent_end}, stop:1 {accent_start});
}}
QScrollBar:vertical {{
    background-color: {scrollbar_bg};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background-color: {scrollbar_handle};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {accent_start};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background-color: {scrollbar_bg};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background-color: {scrollbar_handle};
    border-radius: 4px;
    min-width: 30px;
}}
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {surface};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: {accent_start};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {accent_start};
}}
QComboBox {{
    background-color: {surface};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 6px 10px;
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {surface};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 8px;
    selection-background-color: {accent_start};
}}
QToolTip {{
    background-color: {surface};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 4px 8px;
}}
"""

    @staticmethod
    def _default_dark_palette() -> dict[str, str]:
        """Tema dosyası yokken kullanılacak gömülü koyu tema paleti."""
        return {
            "background": "#12141A",
            "surface": "#1C1F26",
            "surface_raised": "#22263A",
            "text_primary": "#E8EAF0",
            "text_secondary": "#8B8FA8",
            "text_muted": "#4A4D5C",
            "accent_start": "#6366F1",
            "accent_end": "#8B5CF6",
            "success": "#22C55E",
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "border": "#2A2D38",
            "scrollbar_bg": "#1C1F26",
            "scrollbar_handle": "#3A3D4A",
            "sidebar_bg": "#0F1117",
            "sidebar_active": "#6366F1",
        }
