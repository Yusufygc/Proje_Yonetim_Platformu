"""Proje detay paneli için navbar tarzı yatay sekme çubuğu."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from presentation.dimensions import Spacing


class ProjectTabButton(QPushButton):
    """Navbar sekme çubuğundaki tek sekme düğmesi."""

    def __init__(self, label: str, parent: QWidget) -> None:
        super().__init__(label, parent=parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)


class ProjectTabBar(QWidget):
    """
    Checkable QPushButton'lardan oluşan yatay sekme çubuğu.

    QTabWidget yerine kullanılır; QButtonGroup exclusive seçimi yönetir.
    tab_changed sinyali QStackedWidget.setCurrentIndex ile bağlanmalıdır.
    """

    tab_changed = Signal(int)

    def __init__(self, tabs: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._buttons: list[ProjectTabButton] = []
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._setup(tabs)

    def _setup(self, tabs: list[str]) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, 0, Spacing.LG, 0)
        layout.setSpacing(2)
        for i, label in enumerate(tabs):
            btn = ProjectTabButton(label, parent=self)
            self._group.addButton(btn, i)
            self._buttons.append(btn)
            layout.addWidget(btn)
        layout.addStretch()
        self._group.idClicked.connect(self.tab_changed)
        if self._buttons:
            self._buttons[0].setChecked(True)

    def set_current(self, index: int) -> None:
        if 0 <= index < len(self._buttons):
            self._buttons[index].setChecked(True)

    def current_index(self) -> int:
        return self._group.checkedId()
