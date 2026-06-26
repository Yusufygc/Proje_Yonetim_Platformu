"""
SVG ikonlu, hover'da renk değiştiren kompakt aksiyon butonu.

PySide6 QPushButton metni unicode sembolleri (✎, ×, 🗑) bu platformda
güvenilir render etmiyor; bu yüzden düzenle/sil gibi satır aksiyonları
SVG ikon ile çizilir. QIcon CSS :hover ile yeniden boyanmadığından
ikon rengi enter/leave olaylarında elle değiştirilir (sidebar deseni).
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QWidget

from core.managers.icon_manager import IconManager


class IconActionButton(QPushButton):
    """Tek SVG ikonlu, hover'da renk + zemin değiştiren 28x28 aksiyon butonu."""

    def __init__(
        self,
        icon_name: str,
        idle_color: str,
        hover_color: str,
        tooltip: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._icons = IconManager.try_instance()
        self._icon_name = icon_name
        self._idle_color = idle_color
        self._hover_color = hover_color
        self.setFixedSize(28, 28)
        self.setIconSize(QSize(16, 16))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if tooltip:
            self.setToolTip(tooltip)
        self.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 6px; padding: 0; }"
            " QPushButton:hover { background-color: rgba(128, 128, 128, 0.18); }"
        )
        self._set_icon(self._idle_color)

    def _set_icon(self, color: str) -> None:
        if self._icons is not None:
            self.setIcon(self._icons.get_icon(self._icon_name, color))

    def enterEvent(self, event: object) -> None:
        self._set_icon(self._hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event: object) -> None:
        self._set_icon(self._idle_color)
        super().leaveEvent(event)
