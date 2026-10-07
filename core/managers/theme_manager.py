"""
Dark/Light renk paletlerini yöneten Singleton.
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

    Paleti JSON dosyasından yükler; renk erişimini merkezi hale getirir.
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
        if not theme_file.exists():
            # Kullanıcı temaları user/ alt klasöründe saklanır
            theme_file = self._themes_dir / "user" / f"{theme_name}.json"
        if theme_file.exists():
            with open(theme_file, encoding="utf-8") as f:
                self._palette = json.load(f)
            # Alpha token'ları kaynak JSON'a bağlı olmaksızın garantile
            self._palette = self.derive_alpha_tokens(self._palette)
            logger.info("Tema yüklendi: %s", theme_file)
        else:
            logger.warning(
                "Tema dosyası bulunamadı (%s), varsayılan kullanılıyor.", theme_file
            )
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
        if key in self._palette:
            return str(self._palette[key])
        if key == "surface_alt":
            return str(self._palette.get("surface_raised", self._palette.get("surface", "#1E2738")))
        if key == "hover_overlay":
            bg = str(self._palette.get("background", "#000000"))
            return "#FFFFFF12" if bg[:2] in ["#0", "#1", "#2"] else "#0000000A"
        return str(self._palette.get(key, "#FFFFFF"))

    @staticmethod
    def derive_alpha_tokens(palette: dict[str, str]) -> dict[str, str]:
        """Alpha token'larını ve eksik türetilmiş token'ları otomatik hesaplar."""
        result = dict(palette)
        mappings = [
            ("success_alpha", "success"),
            ("warning_alpha", "warning"),
            ("danger_alpha", "danger"),
            ("accent_alpha", "accent_start"),
            ("secondary_alpha", "text_secondary"),
            ("muted_alpha", "text_muted"),
            ("stage_active_alpha", "stage_active"),
            ("stage_done_alpha", "stage_done"),
        ]
        for alpha_key, src_key in mappings:
            src_color = result.get(src_key, "#888888")
            result[alpha_key] = src_color[:7] + "22"
        if "surface_alt" not in result:
            result["surface_alt"] = result.get("surface_raised", result.get("surface", "#1C1F26"))
        if "hover_overlay" not in result:
            bg = str(result.get("background", "#000000"))
            result["hover_overlay"] = "#FFFFFF12" if bg[:2] in ["#0", "#1", "#2"] else "#0000000A"
        return result

    # ── Varsayılan palet ─────────────────────────────────────────────────────

    @staticmethod
    def _default_dark_palette() -> dict[str, str]:
        """Tema dosyası yokken kullanılacak gömülü koyu tema paleti."""
        return ThemeManager.derive_alpha_tokens({
            "background": "#0B0F17",
            "surface": "#151C28",
            "surface_raised": "#1E2738",
            "surface_alt": "#1B2433",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "text_muted": "#64748B",
            "accent_start": "#3B82F6",
            "accent_end": "#2563EB",
            "icon_on_accent": "#FFFFFF",
            "success": "#10B981",
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "border": "#263347",
            "scrollbar_bg": "#0D121B",
            "scrollbar_handle": "#263347",
            "sidebar_bg": "#0D121B",
            "sidebar_active": "#60A5FA",
            "sidebar_text": "#94A3B8",
            "sidebar_text_active": "#FFFFFF",
            "sidebar_hover_bg": "#1E2738",
            "sidebar_active_bg": "#223047",
            "h-sidebar_bg": "#0B0F17",
            "stage_active": "#3B82F6",
            "stage_done": "#10B981",
            "hover_overlay": "#FFFFFF0D",
        })
