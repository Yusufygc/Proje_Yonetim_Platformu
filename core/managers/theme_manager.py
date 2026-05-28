"""
Dark/Light renk paletlerini yöneten ve QSS üretimini merkezi olarak sağlayan Singleton.
14_PREMIUM_UI_UX_TASARIM_PLANI.md'deki renk standartları burada uygulanır.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class ThemeManager(QObject):
    """
    Uygulama temasını yöneten Singleton sınıf.

    Paleti JSON dosyasından yükler; renk ve QSS erişimini merkezi hale getirir.
    """
    
    theme_changed = Signal(str)

    _instance: ThemeManager | None = None

    def __init__(self, themes_dir: Path) -> None:
        super().__init__()
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
        self.theme_changed.emit(theme_name)

    @property
    def current_theme(self) -> str:
        return self._current_theme

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
        surface_raised = p.get("surface_raised", "#22263A")
        text_muted = p.get("text_muted", "#4A4D5C")
        success = p.get("success", "#22C55E")
        danger = p.get("danger", "#EF4444")
        sidebar_bg = p.get("sidebar_bg", "#0F1117")

        return f"""
QWidget {{
    color: {text_primary};
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 13px;
    border: none;
    outline: none;
}}
QMainWindow, QDialog, QStackedWidget, QTabWidget, QScrollArea {{
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
    border-radius: 12px;
    padding: 8px 16px;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {accent_start};
    border-color: {accent_start};
    color: #FFFFFF;
}}
QPushButton:focus, QComboBox:focus, QTreeWidget:focus {{
    border: 1px solid {accent_start};
}}
QPushButton[primary="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {accent_start}, stop:1 {accent_end});
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
}}
QPushButton[primary="true"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {accent_end}, stop:1 {accent_start});
}}
QPushButton#accent_button {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {accent_start}, stop:1 {accent_end});
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}
QPushButton#accent_button:hover {{
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
QSpinBox, QDoubleSpinBox {{
    background-color: {surface};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 6px 10px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {accent_start};
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background-color: {surface_raised};
    border: none;
    width: 18px;
    border-radius: 4px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {accent_start};
}}
QToolTip {{
    background-color: {surface};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 4px 8px;
}}
QTreeWidget {{
    background-color: {surface};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 8px;
}}
QTreeWidget::item {{
    padding: 4px;
}}
QTreeWidget::item:hover {{
    background-color: {surface_raised};
}}
QTreeWidget::item:selected {{
    background-color: {surface_raised};
    color: {accent_start};
}}
QTreeWidget::indicator {{
    width: 16px;
    height: 16px;
}}
QAbstractItemView {{
    outline: 1px solid transparent;
}}
QAbstractItemView:focus {{
    outline: 1px solid {accent_start};
}}
QHeaderView::section {{
    background-color: {surface_raised};
    color: {text_secondary};
    border: none;
    padding: 8px;
    font-weight: bold;
}}
QProgressBar {{
    background-color: {border};
    border-radius: 2px;
    border: none;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {accent_start},stop:1 {accent_end});
    border-radius: 2px;
}}
QListWidget {{
    background-color: transparent;
    border: none;
    color: {text_primary};
    font-size: 14px;
}}
QListWidget::item {{
    padding: 12px;
    border-bottom: 1px solid {border};
}}
QListWidget::item:selected {{
    background-color: {surface_raised};
    border-radius: 6px;
}}
QTabWidget::pane {{
    border: none;
    background: transparent;
}}
QTabBar::tab {{
    background: {surface_raised};
    color: {text_secondary};
    padding: 10px 20px;
    border-radius: 6px;
    margin-right: 4px;
    font-weight: bold;
}}
QTabBar::tab:selected {{
    background: {accent_start};
    color: #FFFFFF;
}}
QTabBar::tab:hover:!selected {{
    background: {border};
}}

/* ========================================================= */
/* CSS Class (Property) tabanlı dinamik seçiciler            */
/* ========================================================= */

*[cssClass="text-primary"] {{ color: {text_primary}; }}
*[cssClass="text-secondary"] {{ color: {text_secondary}; }}
*[cssClass="text-muted"] {{ color: {text_muted}; }}
*[cssClass="text-accent"] {{ color: {accent_start}; }}

*[cssClass="title-large"] {{ font-size: 26px; font-weight: 800; color: {text_primary}; }}
*[cssClass="title-medium"] {{ font-size: 22px; font-weight: 700; color: {text_primary}; }}
*[cssClass="title-small"] {{ font-size: 18px; font-weight: bold; color: {text_primary}; }}
*[cssClass="section-header"] {{ font-size: 11px; font-weight: 600; color: {text_muted}; letter-spacing: 1px; }}

*[cssClass="surface-panel"] {{ background-color: {sidebar_bg}; }}
*[cssClass="panel"] {{ background-color: {surface}; border-radius: 12px; border: 1px solid {border}; }}
*[cssClass="panel-raised"] {{ background-color: {surface_raised}; border-radius: 8px; }}
*[cssClass="divider"] {{ background-color: {border}; max-height: 1px; border: none; }}

/* Buton Sınıfları */
*[cssClass="btn-primary"] {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {accent_start}, stop:1 {accent_end}); color: #FFFFFF; font-weight: bold; border-radius: 6px; padding: 6px 12px; }}
*[cssClass="btn-primary"]:hover {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {accent_end}, stop:1 {accent_start}); }}
*[cssClass="btn-secondary"] {{ background-color: {surface_raised}; color: {text_primary}; border-radius: 6px; padding: 6px 12px; }}
*[cssClass="btn-secondary"]:hover {{ background-color: {border}; }}

/* Özel Bileşen Sınıfları */
ProjectListItem {{ background: transparent; border-left: 3px solid transparent; border-radius: 8px; }}
ProjectListItem:hover {{ background-color: {surface_raised}; }}
ProjectListItem[selected="true"] {{ background-color: {surface_raised}; border-left: 3px solid {accent_start}; }}

Toast {{ background-color: {success}; border-radius: 8px; }}
Toast[type="error"] {{ background-color: {danger}; border-radius: 8px; }}
Toast[type="info"] {{ background-color: {accent_start}; border-radius: 8px; }}

QListWidget[cssClass="panel"] {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 12px;
}}

QPushButton[cssClass="theme-collapsed-btn"] {{
    background: transparent;
    border: none;
    font-size: 16px;
    border-radius: 18px;
}}
QPushButton[cssClass="theme-collapsed-btn"]:hover {{
    background-color: {surface_raised};
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
