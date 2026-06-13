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
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr


def _priority_labels() -> dict[str, str]:
    """Öncelik etiketleri; dil değişimi satır her kurulduğunda yansısın diye fonksiyon."""
    return {
        "LOW": tr("priority_low", "Düşük"),
        "MEDIUM": tr("priority_medium", "Orta"),
        "HIGH": tr("priority_high", "Yüksek"),
        "CRITICAL": tr("priority_critical", "Kritik"),
    }


class _TaskRow(QWidget):
    """Tek bir görevi gösteren satır widget'ı."""

    status_toggle_requested = Signal(int)
    edit_requested = Signal(int)

    def __init__(self, task: Task, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.setObjectName("task_row")
        self._task = task
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.XS, Spacing.SM, Spacing.MD, Spacing.SM)
        layout.setSpacing(Spacing.MD)

        is_done = self._task.status == "DONE"
        status_char = "●" if is_done else "○"

        self._status_btn = QPushButton(status_char, parent=self)
        self._status_btn.setObjectName("task_status_btn")
        self._status_btn.setProperty("task-status", self._task.status)
        self._status_btn.setFixedSize(Size.BTN_ICON_SM, Size.BTN_ICON_SM)
        self._status_btn.setToolTip(tr("task_row_toggle_tooltip", "Durumu değiştir"))
        self._status_btn.clicked.connect(lambda: self.status_toggle_requested.emit(self._task.id))
        layout.addWidget(self._status_btn)

        self._title_btn = QPushButton(self._task.title, parent=self)
        self._title_btn.setObjectName("task_title_btn")
        self._title_btn.setProperty("task-done", str(is_done))
        self._title_btn.clicked.connect(lambda: self.edit_requested.emit(self._task.id))
        layout.addWidget(self._title_btn, 1)

        priority_text = _priority_labels().get(self._task.priority, self._task.priority)
        priority_lbl = QLabel(priority_text, parent=self)
        priority_lbl.setProperty("badge-type", "task-priority")
        priority_lbl.setProperty("badge-value", self._task.priority)
        layout.addWidget(priority_lbl)


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
        scroll.setMaximumHeight(Size.TASK_LIST_MAX_H)

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
        layout.setContentsMargins(0, 0, 0, Spacing.MD)
        layout.setSpacing(Spacing.MD)

        title_lbl = QLabel(tr("section_tasks", "GÖREVLER"), parent=header)
        title_lbl.setProperty("cssClass", "section-header")
        layout.addWidget(title_lbl)

        self._count_lbl = QLabel("0", parent=header)
        self._count_lbl.setObjectName("task_count_badge")
        layout.addWidget(self._count_lbl)
        layout.addStretch()

        add_btn = QPushButton("+", parent=header)
        add_btn.setFixedSize(Size.BTN_ICON_MD, Size.BTN_ICON_MD)
        add_btn.setProperty("cssClass", "btn-primary")
        add_btn.setToolTip(tr("task_add_tooltip", "Görev Ekle"))
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
            empty = QLabel(tr("tasks_empty_short", "Henüz görev yok."), parent=self._list_container)
            empty.setObjectName("task_empty_msg")
            empty.setProperty("cssClass", "text-muted")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(empty)
        else:
            for task in tasks:
                row = _TaskRow(task=task, parent=self._list_container)
                row.status_toggle_requested.connect(self.toggle_status_requested)
                row.edit_requested.connect(self.edit_task_requested)
                self._list_layout.addWidget(row)

        self._list_layout.addStretch()
