"""
Lokal TTF/OTF font dosyalarını QFontDatabase'e kaydeden Singleton.
Font bulunamazsa sessizce sistem fontuna geri döner.
"""
from __future__ import annotations

import logging
from pathlib import Path

from presentation.dimensions import FontFamily

logger = logging.getLogger(__name__)


class FontManager:
    """
    Uygulama kaynak klasöründeki font dosyalarını sisteme tanıtan Singleton.
    """

    _instance: FontManager | None = None

    def __init__(self, fonts_dir: Path) -> None:
        self._fonts_dir = fonts_dir
        self._loaded_families: list[str] = []

    @classmethod
    def instance(cls, fonts_dir: Path | None = None) -> "FontManager":
        if cls._instance is None:
            if fonts_dir is None:
                raise RuntimeError("FontManager ilk çağrıda fonts_dir gerektirir.")
            cls._instance = cls(fonts_dir)
        return cls._instance

    def load_all(self) -> None:
        """Fonts dizinindeki tüm TTF, OTF ve WOFF2 dosyalarını yükler."""
        if not self._fonts_dir.exists():
            logger.warning("Font dizini bulunamadı: %s", self._fonts_dir)
            return

        for pattern in ("*.ttf", "*.otf", "*.woff2"):
            for font_file in self._fonts_dir.glob(pattern):
                self._register(font_file)

    def _register(self, font_file: Path) -> None:
        # QApplication oluşturulduktan sonra çağrılır; geç import zorunludur
        from PySide6.QtGui import QFontDatabase  # noqa: PLC0415
        font_id = QFontDatabase.addApplicationFont(str(font_file))
        if font_id == -1:
            logger.warning("Font yüklenemedi: %s", font_file.name)
        else:
            families = QFontDatabase.applicationFontFamilies(font_id)
            self._loaded_families.extend(families)
            logger.debug("Font yüklendi: %s → %s", font_file.name, families)

    @property
    def loaded_families(self) -> list[str]:
        return list(self._loaded_families)

    @property
    def ui_font(self) -> str:
        """Birincil UI font ailesi; yüklü değilse Inter ardından sistem fontuna döner."""
        for fam in self._loaded_families:
            if FontFamily.UI in fam:
                return FontFamily.UI
        for fam in self._loaded_families:
            if "Inter" in fam:
                return "Inter"
        return FontFamily.FALLBACK_UI

    @property
    def mono_font(self) -> str:
        """Monospace font ailesi; yüklü değilse sistem monospace fontuna döner."""
        for fam in self._loaded_families:
            if FontFamily.MONO in fam:
                return FontFamily.MONO
        return FontFamily.FALLBACK_MONO
