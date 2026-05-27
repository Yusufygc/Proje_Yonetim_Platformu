"""
Görevler sayfası — WBS ağaç görünümü.
Faz 4'te TaskController ve QTreeView ile tam işlevsel hale getirilecek.
"""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class TasksPage(QWidget):
    """Hiyerarşik görev ağacını barındıran sayfa."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel("Görevler", parent=self)
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #E8EAF0;")
        layout.addWidget(title)

        placeholder = QLabel("Görev ağacı burada görünecek.", parent=self)
        placeholder.setStyleSheet("font-size: 14px; color: #8B8FA8;")
        layout.addWidget(placeholder)

        layout.addStretch()
