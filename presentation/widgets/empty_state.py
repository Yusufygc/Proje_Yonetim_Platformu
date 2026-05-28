"""Reusable empty state with illustration and CTA."""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

import config


class EmptyState(QWidget):
    """Compact SVG empty state used by list/detail pages."""

    def __init__(
        self,
        title: str,
        message: str,
        action_label: str | None = None,
        action: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._action = action
        self._setup_ui(title, message, action_label)

    def _setup_ui(self, title: str, message: str, action_label: str | None) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        illustration = QSvgWidget(str(config.RESOURCES_DIR / "illustrations" / "empty_state.svg"))
        illustration.setFixedSize(160, 120)
        layout.addWidget(illustration, alignment=Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title, parent=self)
        title_label.setProperty("cssClass", "title-small")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        message_label = QLabel(message, parent=self)
        message_label.setProperty("cssClass", "text-secondary")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)

        if action_label and self._action:
            button = QPushButton(action_label, parent=self)
            button.setProperty("cssClass", "btn-primary")
            button.setMinimumHeight(36)
            button.clicked.connect(self._action)
            layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
