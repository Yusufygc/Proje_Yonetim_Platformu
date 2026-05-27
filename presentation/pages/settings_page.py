"""
Ayarlar sayfası — tema, tercihler ve uygulama bilgisi.
"""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

import config


class SettingsPage(QWidget):
    """Uygulama ayarlarının yönetildiği sayfa."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel("Ayarlar", parent=self)
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #E8EAF0;")
        layout.addWidget(title)

        version_label = QLabel(
            f"{config.APP_NAME}  —  v{config.APP_VERSION}", parent=self
        )
        version_label.setStyleSheet("font-size: 13px; color: #8B8FA8;")
        layout.addWidget(version_label)

        layout.addStretch()
