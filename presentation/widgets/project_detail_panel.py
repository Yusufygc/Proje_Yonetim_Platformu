"""
Seçili projenin tüm bilgilerini gösteren sağ panel.
Düzenleme, arşivleme ve silme için sinyal yayar; gerçekleştirmez.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from di_container import DIContainer
from domain.models.attachment import Attachment
from domain.models.project import Project
from domain.models.project_stage import ProjectStage
from presentation.pages.tasks_page import TasksPage
from presentation.widgets.decision_list_widget import DecisionListWidget
from presentation.widgets.note_list_widget import NoteListWidget
from presentation.widgets.resource_list_widget import ResourceListWidget
from presentation.widgets.stage_timeline_widget import StageTimelineWidget
from presentation.widgets.task_list_widget import TaskListWidget

_STATUS_THEME_KEYS: dict[str, tuple[str, str]] = {
    "PLANNED": ("Planlandı", "text_secondary"),
    "ACTIVE": ("Aktif", "success"),
    "ON_HOLD": ("Beklemede", "warning"),
    "BLOCKED": ("Engellendi", "danger"),
    "COMPLETED": ("Tamamlandı", "success"),
    "ARCHIVED": ("Arşivlendi", "text_muted"),
    "CANCELLED": ("İptal Edildi", "danger"),
}

_PRIORITY_THEME_KEYS: dict[str, tuple[str, str]] = {
    "LOW": ("Düşük", "text_secondary"),
    "MEDIUM": ("Orta", "accent_start"),
    "HIGH": ("Yüksek", "warning"),
    "CRITICAL": ("Kritik", "danger"),
}


class ProjectDetailPanel(QWidget):
    """Seçili projenin detay bilgilerini gösteren panel."""

    edit_requested = Signal(int)
    archive_requested = Signal(int)
    delete_requested = Signal(int)
    complete_stage_requested = Signal(int)
    activate_stage_requested = Signal(int)

    def __init__(self, parent: QWidget, di: DIContainer) -> None:
        super().__init__(parent=parent)
        self._di = di
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
        icon_lbl.setProperty("cssClass", "text-muted")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        msg_lbl = QLabel("Bir proje seçin\nveya yeni proje oluşturun", parent=page)
        msg_lbl.setProperty("cssClass", "text-muted")
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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        layout.addWidget(self._build_header_row(container))
        layout.addSpacing(12)
        layout.addWidget(self._build_badges_row(container))
        layout.addSpacing(16)

        self._desc_header = QLabel("AÇIKLAMA", parent=container)
        self._desc_header.setProperty("cssClass", "section-header")
        layout.addWidget(self._desc_header)
        layout.addSpacing(6)

        self._desc_lbl = QLabel("", parent=container)
        self._desc_lbl.setProperty("cssClass", "text-secondary")
        self._desc_lbl.setWordWrap(True)
        layout.addWidget(self._desc_lbl)
        layout.addSpacing(12)

        self._github_row = self._build_github_row(container)
        layout.addWidget(self._github_row)
        layout.addSpacing(16)

        stages_header = QLabel("SÜREÇ AŞAMALARI", parent=container)
        stages_header.setProperty("cssClass", "section-header")
        layout.addWidget(stages_header)
        layout.addSpacing(6)

        self._stage_timeline = StageTimelineWidget(parent=container)
        self._stage_timeline.complete_requested.connect(self.complete_stage_requested)
        self._stage_timeline.activate_requested.connect(self.activate_stage_requested)
        layout.addWidget(self._stage_timeline)
        layout.addSpacing(16)

        self._tab_widget = QTabWidget(parent=container)
        # QTabWidget stilleri global QSS içinde yönetiliyor

        self._summary_page = self._build_summary_tab()
        self._tab_widget.addTab(self._summary_page, "Özet")

        self._tasks_page = TasksPage(
            parent=self._tab_widget,
            controller=self._di.task_controller,
            project_controller=self._di.project_controller,
        )
        self._tab_widget.addTab(self._tasks_page, "Görevler")

        self._decisions_page = DecisionListWidget(
            controller=self._di.decision_controller,
            parent=self._tab_widget
        )
        self._tab_widget.addTab(self._decisions_page, "Kararlar")

        self._notes_page = NoteListWidget(
            controller=self._di.note_controller,
            parent=self._tab_widget
        )
        self._tab_widget.addTab(self._notes_page, "Notlar")

        self._resources_page = ResourceListWidget(
            controller=self._di.resource_controller,
            parent=self._tab_widget
        )
        self._tab_widget.addTab(self._resources_page, "Kaynaklar")

        self._ideas_page = self._build_simple_text_tab(
            "Projeye bağlı fikirler ProjectIdea ilişkisiyle saklanır."
        )
        self._tab_widget.addTab(self._ideas_page, "Fikirler")

        self._outputs_page = self._build_outputs_tab()
        self._tab_widget.addTab(self._outputs_page, "Çıktılar")

        self._activity_page = self._build_activity_tab()
        self._tab_widget.addTab(self._activity_page, "Aktivite")

        layout.addWidget(self._tab_widget, 1)
        layout.addStretch()

        return scroll

    def _build_summary_tab(self) -> QWidget:
        page = QWidget(parent=self._tab_widget)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        self._summary_problem = QLabel("", parent=page)
        self._summary_problem.setWordWrap(True)
        self._summary_target = QLabel("", parent=page)
        self._summary_target.setWordWrap(True)
        self._summary_progress = QLabel("", parent=page)
        for widget in (self._summary_problem, self._summary_target, self._summary_progress):
            widget.setProperty("cssClass", "text-secondary")
            layout.addWidget(widget)
        layout.addStretch()
        return page

    def _build_simple_text_tab(self, text: str) -> QWidget:
        page = QWidget(parent=self._tab_widget)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        label = QLabel(text, parent=page)
        label.setProperty("cssClass", "text-muted")
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addStretch()
        return page

    def _build_outputs_tab(self) -> QWidget:
        page = QWidget(parent=self._tab_widget)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        add_btn = QPushButton("+ Çıktı / Dosya Yolu Ekle", parent=page)
        add_btn.setProperty("cssClass", "btn-primary")
        add_btn.clicked.connect(self._on_add_output)
        layout.addWidget(add_btn)
        self._outputs_list = QListWidget(parent=page)
        self._outputs_list.setProperty("cssClass", "panel-raised")
        layout.addWidget(self._outputs_list)
        return page

    def _build_activity_tab(self) -> QWidget:
        page = QWidget(parent=self._tab_widget)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        self._activity_list = QListWidget(parent=page)
        self._activity_list.setProperty("cssClass", "panel-raised")
        layout.addWidget(self._activity_list)
        return page

    def _build_header_row(self, parent: QWidget) -> QWidget:
        row = QWidget(parent=parent)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._title_lbl = QLabel("", parent=row)
        self._title_lbl.setProperty("cssClass", "title-medium")
        self._title_lbl.setWordWrap(True)
        layout.addWidget(self._title_lbl, 1)

        self._edit_btn = QPushButton("Düzenle", parent=row)
        self._edit_btn.setMinimumSize(80, 32)
        self._edit_btn.setProperty("cssClass", "btn-primary")
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
        lbl.setProperty("cssClass", "text-secondary")
        layout.addWidget(lbl)

        self._github_lbl = QLabel("", parent=row)
        self._github_lbl.setProperty("cssClass", "text-accent")
        self._github_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._github_lbl, 1)
        return row

    def show_project(self, project: Project) -> None:
        """Proje detaylarını günceller ve detay sayfasını gösterir."""
        self._project_id = project.id
        self._title_lbl.setText(project.title)

        from core.managers.theme_manager import ThemeManager
        theme_mgr = ThemeManager.instance()

        status_text, theme_key = _STATUS_THEME_KEYS.get(project.status, (project.status, "text_secondary"))
        status_color = theme_mgr.color(theme_key)
        self._status_badge.setText(status_text)
        self._status_badge.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {status_color};"
            f" background: {status_color}22; padding: 4px 10px; border-radius: 10px;"
        )

        priority_text, theme_key = _PRIORITY_THEME_KEYS.get(
            project.priority, (project.priority, "accent_start")
        )
        priority_color = theme_mgr.color(theme_key)
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
        self._tasks_page.set_project(project.id)
        self._decisions_page.set_project(project.id)
        self._notes_page.set_project(project.id)
        self._resources_page.set_project(project.id)
        self._summary_problem.setText(f"Problem: {project.problem_statement or '-'}")
        self._summary_target.setText(f"Hedef çıktı: {project.target_outcome or '-'}")
        target_date = project.target_end_date.isoformat() if project.target_end_date else "-"
        self._summary_progress.setText(
            f"İlerleme: %{project.progress_percent}  |  Hedef tarih: {target_date}"
        )
        self._refresh_outputs()
        self._refresh_activity()

        has_github = bool(project.github_url)
        self._github_row.setVisible(has_github)
        if has_github:
            self._github_lbl.setText(project.github_url)

        self._stack.setCurrentIndex(1)

    def update_stages(self, stages: list[ProjectStage]) -> None:
        """Aşama zaman çizelgesini verilen liste ile yeniler."""
        self._stage_timeline.update_stages(stages)

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

    def _refresh_outputs(self) -> None:
        self._outputs_list.clear()
        if self._project_id is None:
            return
        for item in self._di.attachment_repository.get_by_project(self._project_id):
            self._outputs_list.addItem(QListWidgetItem(f"{item.file_path}\n{item.caption or ''}"))

    def _refresh_activity(self) -> None:
        self._activity_list.clear()
        if self._project_id is None:
            return
        for log in self._di.activity_log_repository.get_by_project(self._project_id):
            self._activity_list.addItem(QListWidgetItem(f"{log.created_at} · {log.summary}"))

    def _on_add_output(self) -> None:
        if self._project_id is None:
            return
        path, ok = QInputDialog.getText(self, "Çıktı Ekle", "Dosya yolu veya bağlantı:")
        if not ok or not path.strip():
            return
        caption, _ = QInputDialog.getText(self, "Çıktı Açıklaması", "Kısa açıklama:")
        self._di.attachment_repository.create(
            Attachment(
                project_id=self._project_id,
                file_path=path.strip(),
                caption=caption.strip() or None,
                attachment_type="OUTPUT",
            )
        )
        self._refresh_outputs()
