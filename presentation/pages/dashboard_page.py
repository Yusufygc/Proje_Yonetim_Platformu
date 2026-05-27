"""
Dashboard sayfası — istatistik kartlarını ve hızlı fikir kutusunu barındırır.
Henüz veri katmanına bağlı değil; Faz 7'de DashboardService ile doldurulacak.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    """Ana dashboard ekranı — özet istatistikler ve son aktiviteler."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Dashboard", parent=self)
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #E8EAF0;")
        layout.addWidget(title)

        subtitle = QLabel("Proje özetleri burada görünecek.", parent=self)
        subtitle.setStyleSheet("font-size: 14px; color: #8B8FA8;")
        layout.addWidget(subtitle)

        layout.addStretch()
