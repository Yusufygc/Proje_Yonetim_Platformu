"""QML için Çoklu Dil (i18n) ve Çeviri Köprüsü."""
from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from core.managers.string_manager import StringManager

logger = logging.getLogger(__name__)


class I18nBridge(QObject):
    """
    QML bileşenlerine anlık metin çevirisi (tr) ve aktif dil değişimi sağlar.
    """

    languageChanged = Signal(str)

    def __init__(
        self,
        string_mgr: StringManager,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._string_mgr = string_mgr
        self._string_mgr.language_changed.connect(self.languageChanged.emit)

    @Property(str, notify=languageChanged)
    def currentLanguage(self) -> str:
        return self._string_mgr.current_language

    @Slot(str, str, result=str)
    def tr(self, key: str, default: str = "") -> str:
        """Belirtilen anahtara karşılık gelen yerelleştirilmiş metni döndürür."""
        return self._string_mgr.get(key, default)

    @Slot(str)
    def setLanguage(self, lang_code: str) -> None:
        """Uygulama dilini değiştirir."""
        self._string_mgr.set_language(lang_code)
