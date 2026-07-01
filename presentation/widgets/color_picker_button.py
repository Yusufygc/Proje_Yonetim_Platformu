from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QFrame, QWidget

from presentation.utils.i18n import tr


class ColorPickerButton(QFrame):
    """Tıklanınca QColorDialog açan, seçilen rengi gösteren kare buton."""

    color_changed = Signal(str)  # hex renk kodu (#rrggbb)

    def __init__(self, color: str = "#888888", parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._color = color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(28, 28)
        self._apply_style()

    def set_color(self, color: str) -> None:
        self._color = color
        self._apply_style()

    def get_color(self) -> str:
        return self._color

    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"QFrame {{ background-color: {self._color}; border-radius: 4px;"
            f" border: 2px solid rgba(255,255,255,0.2); }}"
            f"QFrame:hover {{ border: 2px solid rgba(255,255,255,0.55); }}"
        )

    def mousePressEvent(self, event: object) -> None:
        color = QColorDialog.getColor(QColor(self._color), self, tr("color_picker_dialog_title", "Renk Seç"))
        if color.isValid():
            self.set_color(color.name())
            self.color_changed.emit(self._color)
        super().mousePressEvent(event)  # type: ignore[arg-type]
