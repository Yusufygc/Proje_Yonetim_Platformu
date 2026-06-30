"""Paylaşımlı çöp kutusu ikon butonu — liste satırı içi silme eylemi için."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QWidget

from core.managers.icon_manager import IconManager, Icons
from core.managers.theme_manager import ThemeManager
from presentation.utils.i18n import tr


class DeleteIconButton(QPushButton):
    """Çöp kutusu ikonlu silme butonu; hover'da kırmızı zemin + beyaz ikon.

    QIcon CSS :hover ile yeniden renklenmediğinden ikon enter/leave olaylarında
    elle değiştirilir (sidebar navigasyon butonu deseni).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._icons = IconManager.try_instance()
        self._theme = ThemeManager.instance()
        self.setFixedSize(28, 28)
        self.setIconSize(QSize(16, 16))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tr("action_delete", "Sil"))
        self.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 6px; padding: 0; }"
            " QPushButton:hover { background-color: #e53935; }"
        )
        self._apply_idle_icon()

    def _apply_idle_icon(self) -> None:
        if self._icons is not None:
            self.setIcon(self._icons.get_icon(Icons.TRASH, self._theme.color("text_muted")))

    def enterEvent(self, event: object) -> None:
        if self._icons is not None:
            self.setIcon(self._icons.get_icon(Icons.TRASH, "#FFFFFF"))
        super().enterEvent(event)

    def leaveEvent(self, event: object) -> None:
        self._apply_idle_icon()
        super().leaveEvent(event)
