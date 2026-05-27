"""
Seçili projenin tüm bilgilerini gösteren sağ panel.
Düzenleme, arşivleme ve silme için sinyal yayar; gerçekleştirmez.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from domain.models.project import Project
from domain.models.project_stage import ProjectStage
from presentation.widgets.stage_timeline_widget import StageTimelineWidget
from presentation.widgets.task_list_widget import TaskListWidget

_STATUS_TR: dict[str, tuple[str, str]] = {
    "PLANNED": ("Planlandı", "#8B8FA8"),
    "ACTIVE": ("Aktif", "#22C55E"),
    "ON_HOLD": ("Beklemede", "#F59E0B"),
    "BLOCKED": ("Engellendi", "#EF4444"),
    "COMPLETED": ("Tamamlandı", "#22C55E"),
    "ARCHIVED": ("Arşivlendi", "#4A4D5C"),
    "CANCELLED": ("İptal Edildi", "#EF4444"),
}

_PRIORITY_TR: dict[str, tuple[str, str]] = {
    "LOW": ("Düşük", "#4A4D5C"),
    "MEDIUM": ("Orta", "#6366F1"),
    "HIGH": ("Yüksek", "#F59E0B"),
    "CRITICAL": ("Kritik", "#EF4444"),
}


class ProjectDetailPanel(QWidget):
    """Seçili projenin detay bilgilerini gösteren panel."""

    edit_requested = Signal(int)
    archive_requested = Signal(int)
    delete_requested = Signal(int)
    complete_stage_requested = Signal(int)
    activate_stage_requested = Signal(int)
    add_task_requested = Signal()
    edit_task_requested = Signal(int)
    toggle_task_status_requested = Signal(int)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._project_id: int | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget(parent=self)
        outer_layout.addWidget(self._stack)

        self._stack.addWidget(self._build_empty_page())
        self._stack.addWidget(self._build_detail_page())
        self._stack.setCurrentIndex(0)

    def _build_empty_page(self) -> QWidget:
        page = QWidget(parent=self._stack)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(60, 0, 60, 0)
        layout.addStretch()

        icon_lbl = QLabel("◈", parent=page)
        icon_lbl.setStyleSheet("font-size: 48px; color: #2A2D38;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        msg_lbl = QLabel("Bir proje seçin\nveya yeni proje oluşturun", parent=page)
        msg_lbl.setStyleSheet("font-size: 14px; color: #4A4D5C; line-height: 1.6;")
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_lbl)
        layout.addStretch()
        return page

    def _build_detail_page(self) -> QScrollArea:
        scroll = QScrollArea(parent=self._stack)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget(parent=scroll)
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(0)

        layout.addWidget(self._build_header_row(container))
        layout.addSpacing(20)
        layout.addWidget(self._build_badges_row(container))
        layout.addSpacing(24)

        self._desc_header = QLabel("AÇIKLAMA", parent=container)
        self._desc_header.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #4A4D5C; letter-spacing: 1px;"
        )
        layout.addWidget(self._desc_header)
        layout.addSpacing(8)

        self._desc_lbl = QLabel("", parent=container)
        self._desc_lbl.setStyleSheet("font-size: 14px; color: #8B8FA8; line-height: 1.6;")
        self._desc_lbl.setWordWrap(True)
        layout.addWidget(self._desc_lbl)
        layout.addSpacing(20)

        self._github_row = self._build_github_row(container)
        layout.addWidget(self._github_row)
        layout.addSpacing(28)

        stages_header = QLabel("SÜREÇ AŞAMALARI", parent=container)
        stages_header.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #4A4D5C; letter-spacing: 1px;"
        )
        layout.addWidget(stages_header)
        layout.addSpacing(8)

        self._stage_timeline = StageTimelineWidget(parent=container)
        self._stage_timeline.complete_requested.connect(self.complete_stage_requested)
        self._stage_timeline.activate_requested.connect(self.activate_stage_requested)
        layout.addWidget(self._stage_timeline)
        layout.addSpacing(28)

        self._task_list = TaskListWidget(parent=container)
        self._task_list.add_task_requested.connect(self.add_task_requested)
        self._task_list.edit_task_requested.connect(self.edit_task_requested)
        self._task_list.toggle_status_requested.connect(self.toggle_task_status_requested)
        layout.addWidget(self._task_list)
        layout.addStretch()

        return scroll

    def _build_header_row(self, parent: QWidget) -> QWidget:
        row = QWidget(parent=parent)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._title_lbl = QLabel("", parent=row)
        self._title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #E8EAF0;")
        self._title_lbl.setWordWrap(True)
        layout.addWidget(self._title_lbl, 1)

        self._edit_btn = QPushButton("Düzenle", parent=row)
        self._edit_btn.setMinimumSize(80, 32)
        self._edit_btn.setObjectName("accent_button")
        self._edit_btn.clicked.connect(self._on_edit)
        layout.addWidget(self._edit_btn)

        self._more_btn = QPushButton("···", parent=row)
        self._more_btn.setMinimumSize(36, 32)
        self._more_btn.clicked.connect(self._on_more_menu)
        layout.addWidget(self._more_btn)
        return row

    def _build_badges_row(self, parent: QWidget) -> QWidget:
        row = QWidget(parent=parent)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._status_badge = QLabel("", parent=row)
        layout.addWidget(self._status_badge)

        self._priority_badge = QLabel("", parent=row)
        layout.addWidget(self._priority_badge)
        layout.addStretch()
        return row

    def _build_github_row(self, parent: QWidget) -> QWidget:
        row = QWidget(parent=parent)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        lbl = QLabel("GitHub:", parent=row)
        lbl.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #4A4D5C; min-width: 60px;"
        )
        layout.addWidget(lbl)

        self._github_lbl = QLabel("", parent=row)
        self._github_lbl.setStyleSheet("font-size: 12px; color: #6366F1;")
        self._github_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._github_lbl, 1)
        return row

    def show_project(self, project: Project) -> None:
        """Proje detaylarını günceller ve detay sayfasını gösterir."""
        self._project_id = project.id
        self._title_lbl.setText(project.title)

        status_text, status_color = _STATUS_TR.get(project.status, (project.status, "#8B8FA8"))
        self._status_badge.setText(status_text)
        self._status_badge.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {status_color};"
            f" background: {status_color}22; padding: 4px 10px; border-radius: 10px;"
        )

        priority_text, priority_color = _PRIORITY_TR.get(
            project.priority, (project.priority, "#6366F1")
        )
        self._priority_badge.setText(f"● {priority_text} Öncelik")
        self._priority_badge.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {priority_color};"
            f" background: {priority_color}22; padding: 4px 10px; border-radius: 10px;"
        )

        has_desc = bool(project.short_description)
        self._desc_header.setVisible(has_desc)
        self._desc_lbl.setVisible(has_desc)
        if has_desc:
            self._desc_lbl.setText(project.short_description)

        has_github = bool(project.github_url)
        self._github_row.setVisible(has_github)
        if has_github:
            self._github_lbl.setText(project.github_url)

        self._stack.setCurrentIndex(1)

    def update_stages(self, stages: list[ProjectStage]) -> None:
        """Aşama zaman çizelgesini verilen liste ile yeniler."""
        self._stage_timeline.update_stages(stages)

    def update_tasks(self, tasks: list) -> None:
        """Görev listesini yeniler."""
        self._task_list.update_tasks(tasks)

    def show_empty_state(self) -> None:
        self._project_id = None
        self._stack.setCurrentIndex(0)

    def _on_edit(self) -> None:
        if self._project_id is not None:
            self.edit_requested.emit(self._project_id)

    def _on_more_menu(self) -> None:
        menu = QMenu(self)
        archive_action = menu.addAction("Arşivle")
        archive_action.triggered.connect(
            lambda: self.archive_requested.emit(self._project_id)
        )
        menu.addSeparator()
        delete_action = menu.addAction("Sil")
        delete_action.triggered.connect(
            lambda: self.delete_requested.emit(self._project_id)
        )
        menu.exec(self._more_btn.mapToGlobal(self._more_btn.rect().bottomLeft()))
