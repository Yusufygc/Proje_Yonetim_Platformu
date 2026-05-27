"""
Proje detay panelinde gösterilen görev listesi widget'ı.
Görev ekleme, durum toggle ve düzenleme için sinyal yayar.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from domain.models.task import Task

_STATUS_THEME_KEYS: dict[str, str] = {
    "TODO": "text_secondary",
    "IN_PROGRESS": "accent_start",
    "WAITING": "warning",
    "BLOCKED": "danger",
    "DONE": "success",
    "CANCELLED": "text_muted",
}

_PRIORITY_THEME_KEYS: dict[str, str] = {
    "LOW": "text_secondary",
    "MEDIUM": "accent_start",
    "HIGH": "warning",
    "CRITICAL": "danger",
}

_PRIORITY_TR: dict[str, str] = {
    "LOW": "Düşük",
    "MEDIUM": "Orta",
    "HIGH": "Yüksek",
    "CRITICAL": "Kritik",
}


class _TaskRow(QWidget):
    """Tek bir görevi gösteren satır widget'ı."""

    status_toggle_requested = Signal(int)
    edit_requested = Signal(int)

    def __init__(self, task: Task, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._task = task
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 6, 8, 6)
        layout.setSpacing(8)

        from core.managers.theme_manager import ThemeManager
        theme_mgr = ThemeManager.instance()

        status_color = theme_mgr.color(_STATUS_THEME_KEYS.get(self._task.status, "text_secondary"))
        is_done = self._task.status == "DONE"
        status_char = "●" if is_done else "○"
        self._status_btn = QPushButton(status_char, parent=self)
        self._status_btn.setFixedSize(20, 20)
        self._status_btn.setStyleSheet(
            f"QPushButton {{ color: {status_color}; font-size: 13px; border: none;"
            f" background: transparent; padding: 0; }}"
            f"QPushButton:hover {{ color: {theme_mgr.color('success')}; }}"
        )
        self._status_btn.setToolTip("Durumu değiştir")
        self._status_btn.clicked.connect(lambda: self.status_toggle_requested.emit(self._task.id))
        layout.addWidget(self._status_btn)

        self._title_btn = QPushButton(self._task.title, parent=self)
        title_color = theme_mgr.color("text_muted") if is_done else theme_mgr.color("text_primary")
        self._title_btn.setStyleSheet(
            f"QPushButton {{ font-size: 13px; color: {title_color}; border: none;"
            f" background: transparent; text-align: left; padding: 0; }}"
            f"QPushButton:hover {{ color: {theme_mgr.color('accent_start')}; }}"
        )
        self._title_btn.clicked.connect(lambda: self.edit_requested.emit(self._task.id))
        layout.addWidget(self._title_btn, 1)

        priority_color = theme_mgr.color(_PRIORITY_THEME_KEYS.get(self._task.priority, "accent_start"))
        priority_text = _PRIORITY_TR.get(self._task.priority, self._task.priority)
        priority_lbl = QLabel(priority_text, parent=self)
        priority_lbl.setStyleSheet(
            f"font-size: 10px; font-weight: 600; color: {priority_color};"
            f" background: {priority_color}22; padding: 2px 6px; border-radius: 7px;"
        )
        layout.addWidget(priority_lbl)

        self.setStyleSheet(
            f"_TaskRow {{ border-radius: 6px; }}"
            f"_TaskRow:hover {{ background-color: {theme_mgr.color('surface_raised')}; }}"
        )


class TaskListWidget(QWidget):
    """Proje detay panelinde gösterilen görev listesi."""

    add_task_requested = Signal()
    edit_task_requested = Signal(int)
    toggle_status_requested = Signal(int)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())

        scroll = QScrollArea(parent=self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMaximumHeight(220)

        self._list_container = QWidget(parent=scroll)
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(2)

        scroll.setWidget(self._list_container)
        layout.addWidget(scroll)

        self._rendered_tasks: list[Task] = []

    def _build_header(self) -> QWidget:
        header = QWidget(parent=self)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(8)

        from core.managers.theme_manager import ThemeManager
        theme_mgr = ThemeManager.instance()
        accent_color = theme_mgr.color("accent_start")

        title_lbl = QLabel("GÖREVLER", parent=header)
        title_lbl.setProperty("cssClass", "section-header")
        layout.addWidget(title_lbl)

        self._count_lbl = QLabel("0", parent=header)
        self._count_lbl.setStyleSheet(
            f"font-size: 10px; font-weight: 600; color: {accent_color};"
            f" background: {accent_color}22; padding: 1px 6px; border-radius: 8px;"
        )
        layout.addWidget(self._count_lbl)
        layout.addStretch()

        add_btn = QPushButton("+", parent=header)
        add_btn.setFixedSize(24, 24)
        add_btn.setProperty("cssClass", "btn-primary")
        add_btn.setToolTip("Görev Ekle")
        add_btn.clicked.connect(self.add_task_requested)
        layout.addWidget(add_btn)

        return header

    def update_tasks(self, tasks: list[Task]) -> None:
        """Görev listesini verilen liste ile yeniler."""
        for i in reversed(range(self._list_layout.count())):
            item = self._list_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        self._count_lbl.setText(str(len(tasks)))
        self._rendered_tasks = tasks

        if not tasks:
            empty = QLabel("Henüz görev yok.", parent=self._list_container)
            empty.setProperty("cssClass", "text-muted")
            empty.setStyleSheet("font-size: 12px; padding: 10px 4px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(empty)
        else:
            for task in tasks:
                row = _TaskRow(task=task, parent=self._list_container)
                row.status_toggle_requested.connect(self.toggle_status_requested)
                row.edit_requested.connect(self.edit_task_requested)
                self._list_layout.addWidget(row)

        self._list_layout.addStretch()
