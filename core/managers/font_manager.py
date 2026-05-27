"""
Lokal TTF/OTF font dosyalarını QFontDatabase'e kaydeden Singleton.
Font bulunamazsa sessizce sistem fontuna geri döner.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtGui import QFontDatabase

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
        """Fonts dizinindeki tüm TTF ve OTF dosyalarını yükler."""
        if not self._fonts_dir.exists():
            logger.warning("Font dizini bulunamadı: %s", self._fonts_dir)
            return

        for font_file in self._fonts_dir.glob("*.ttf"):
            self._register(font_file)
        for font_file in self._fonts_dir.glob("*.otf"):
            self._register(font_file)

    def _register(self, font_file: Path) -> None:
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
