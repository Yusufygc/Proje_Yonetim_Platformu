"""
Çoklu dil (i18n) ve metin yönetim merkezi.
Uygulama içerisindeki tüm hardcoded metinler bu yöneticiden çekilir.
"""
import json
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class StringManager(QObject):
    """JSON tabanlı çoklu dil yöneticisi.

    Dil değişiminde `language_changed` yayınlanır; metinlerini programatik
    kuran widget'lar bu sinyale abone olarak kendilerini tazelemelidir
    (tema sözleşmesindeki theme_changed ile aynı desen).
    """

    language_changed = Signal(str)

    _instance: Optional["StringManager"] = None

    def __init__(self, locales_dir: Path) -> None:
        super().__init__()
        self._locales_dir = locales_dir
        self._strings: dict[str, str] = {}
        self._current_lang = "tr"
        self._load_language(self._current_lang)

    @classmethod
    def instance(cls, locales_dir: Optional[Path] = None) -> "StringManager":
        if cls._instance is None:
            if locales_dir is None:
                raise RuntimeError("StringManager ilk çağrıda locales_dir gerektirir.")
            cls._instance = cls(locales_dir)
        return cls._instance

    @property
    def current_language(self) -> str:
        return self._current_lang

    def _load_language(self, lang_code: str) -> None:
        lang_file = self._locales_dir / f"strings.{lang_code}.json"
        if lang_file.exists():
            try:
                with open(lang_file, encoding="utf-8") as f:
                    self._strings = json.load(f)
                logger.info("Dil dosyası yüklendi: %s", lang_file)
            except Exception as e:
                logger.error("Dil dosyası okunurken hata: %s", e)
        else:
            logger.warning("Dil dosyası bulunamadı: %s. Varsayılanlar kullanılacak.", lang_file)
            self._strings = {}

    def set_language(self, lang_code: str) -> None:
        """Aktif dili değiştirir ve dinleyicilere yayın yapar."""
        if lang_code == self._current_lang:
            return
        self._current_lang = lang_code
        self._load_language(lang_code)
        self.language_changed.emit(lang_code)

    @classmethod
    def get(cls, key: str, default: str = "") -> str:
        """Belirtilen anahtara karşılık gelen metni döndürür."""
        if cls._instance is None:
            return default or key
        return cls._instance._strings.get(key, default or key)
