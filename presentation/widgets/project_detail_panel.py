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
    QVBoxLayout,
    QWidget,
)

from app.di_container import DIContainer
from domain.models.attachment import Attachment
from domain.models.project import Project
from domain.models.project_stage import ProjectStage
from presentation.dimensions import Size, Spacing
from presentation.pages.tasks import TasksPage
from presentation.utils.i18n import tr
from presentation.widgets.decision_list_widget import DecisionListWidget
from presentation.widgets.note_list_widget import NoteListWidget
from presentation.widgets.resource_list_widget import ResourceListWidget
from presentation.widgets.project_tab_bar import ProjectTabBar
from presentation.widgets.stage_timeline_widget import StageTimelineWidget


def _status_theme_keys() -> dict[str, tuple[str, str]]:
    """(etiket, tema rengi anahtarı) — dil değişimi yansısın diye fonksiyon."""
    return {
        "PLANNED": (tr("status_planned", "Planlandı"), "text_secondary"),
        "ACTIVE": (tr("status_active", "Aktif"), "success"),
        "ON_HOLD": (tr("status_on_hold", "Beklemede"), "warning"),
        "BLOCKED": (tr("status_blocked", "Engellendi"), "danger"),
        "COMPLETED": (tr("status_completed", "Tamamlandı"), "success"),
        "ARCHIVED": (tr("status_archived", "Arşivlendi"), "text_muted"),
        "CANCELLED": (tr("status_cancelled", "İptal Edildi"), "danger"),
    }


def _priority_theme_keys() -> dict[str, tuple[str, str]]:
    return {
        "LOW": (tr("priority_low", "Düşük"), "text_secondary"),
        "MEDIUM": (tr("priority_medium", "Orta"), "accent_start"),
        "HIGH": (tr("priority_high", "Yüksek"), "warning"),
        "CRITICAL": (tr("priority_critical", "Kritik"), "danger"),
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
        self._stages_expanded: bool = True
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
        # Yatay 60px — sabit boşluk, tasarım kararı; Spacing skalalasından büyük
        layout.setContentsMargins(60, 0, 60, 0)
        layout.addStretch()

        icon_lbl = QLabel("◈", parent=page)
        icon_lbl.setProperty("cssClass", "text-muted")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        msg_lbl = QLabel(tr("detail_empty_message", "Bir proje seçin\nveya yeni proje oluşturun"), parent=page)
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
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(0)

        layout.addWidget(self._build_header_row(container))
        layout.addSpacing(12)
        layout.addWidget(self._build_badges_row(container))
        layout.addSpacing(16)

        self._desc_header = QLabel(tr("section_description", "AÇIKLAMA"), parent=container)
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

        stages_toggle = QFrame(parent=container)
        stages_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        stages_toggle.setProperty("cssClass", "section-collapse-header")
        sh_layout = QHBoxLayout(stages_toggle)
        sh_layout.setContentsMargins(0, Spacing.SM, 0, Spacing.SM)
        sh_layout.setSpacing(Spacing.SM)
        sh_lbl = QLabel(tr("section_stages", "SÜREÇ AŞAMALARI"), parent=stages_toggle)
        sh_lbl.setProperty("cssClass", "section-header")
        sh_layout.addWidget(sh_lbl, 1)
        self._stages_chevron = QLabel("▼", parent=stages_toggle)
        self._stages_chevron.setProperty("cssClass", "text-muted")
        sh_layout.addWidget(self._stages_chevron)
        layout.addWidget(stages_toggle)
        stages_toggle.mousePressEvent = lambda _e: self._toggle_stages()

        self._stage_timeline = StageTimelineWidget(parent=container, theme=self._di.theme)
        self._stage_timeline.complete_requested.connect(self.complete_stage_requested)
        self._stage_timeline.activate_requested.connect(self.activate_stage_requested)
        layout.addWidget(self._stage_timeline)
        layout.addSpacing(16)

        # Navbar sekme çubuğu
        tab_labels = [
            tr("tab_summary",   "Özet"),
            tr("tab_tasks",     "Görevler"),
            tr("tab_decisions", "Kararlar"),
            tr("tab_notes",     "Notlar"),
            tr("tab_resources", "Kaynaklar"),
            tr("tab_outputs",   "Çıktılar"),
        ]
        self._tab_bar = ProjectTabBar(tabs=tab_labels, parent=container)
        layout.addWidget(self._tab_bar)

        tab_divider = QFrame(parent=container)
        tab_divider.setFrameShape(QFrame.Shape.HLine)
        tab_divider.setProperty("cssClass", "divider")
        layout.addWidget(tab_divider)

        # İçerik yığını — sekme butonlarıyla senkron indeks sırasında olmalı
        self._tab_stack = QStackedWidget(parent=container)

        self._summary_page = self._build_summary_tab()
        self._tab_stack.addWidget(self._summary_page)

        self._tasks_page = TasksPage(
            parent=self._tab_stack,
            controller=self._di.task_controller,
            project_controller=self._di.project_controller,
            theme=self._di.theme,
            embedded=True,
        )
        self._tab_stack.addWidget(self._tasks_page)

        self._decisions_page = DecisionListWidget(
            controller=self._di.decision_controller,
            parent=self._tab_stack,
        )
        self._tab_stack.addWidget(self._decisions_page)

        self._notes_page = NoteListWidget(
            controller=self._di.note_controller,
            parent=self._tab_stack,
        )
        self._tab_stack.addWidget(self._notes_page)

        self._resources_page = ResourceListWidget(
            controller=self._di.resource_controller,
            parent=self._tab_stack,
            theme=self._di.theme,
        )
        self._tab_stack.addWidget(self._resources_page)

        self._outputs_page = self._build_outputs_tab()
        self._tab_stack.addWidget(self._outputs_page)

        self._tab_bar.tab_changed.connect(self._tab_stack.setCurrentIndex)
        layout.addWidget(self._tab_stack, 1)
        layout.addStretch()

        return scroll

    def _build_summary_tab(self) -> QWidget:
        page = QWidget(parent=self._tab_stack)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.MD)
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

    def _build_outputs_tab(self) -> QWidget:
        page = QWidget(parent=self._tab_stack)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        add_btn = QPushButton(tr("detail_add_output_btn", "+ Çıktı / Dosya Yolu Ekle"), parent=page)
        add_btn.setProperty("cssClass", "btn-primary")
        add_btn.clicked.connect(self._on_add_output)
        layout.addWidget(add_btn)
        self._outputs_list = QListWidget(parent=page)
        self._outputs_list.setProperty("cssClass", "panel-raised")
        layout.addWidget(self._outputs_list)
        return page

    def _build_header_row(self, parent: QWidget) -> QWidget:
        row = QWidget(parent=parent)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MD)

        self._title_lbl = QLabel("", parent=row)
        self._title_lbl.setProperty("cssClass", "title-medium")
        self._title_lbl.setWordWrap(True)
        layout.addWidget(self._title_lbl, 1)

        self._edit_btn = QPushButton(tr("action_edit", "Düzenle"), parent=row)
        self._edit_btn.setMinimumSize(Size.BTN_MD_W, Size.BTN_SM_H)
        self._edit_btn.setProperty("cssClass", "btn-primary")
        self._edit_btn.clicked.connect(self._on_edit)
        layout.addWidget(self._edit_btn)

        self._more_btn = QPushButton("···", parent=row)
        self._more_btn.setMinimumSize(Size.THEME_COLLAPSED_BTN, Size.BTN_SM_H)
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

        status_text, _theme_key = _status_theme_keys().get(project.status, (project.status, "text_secondary"))
        self._status_badge.setText(status_text)
        self._status_badge.setProperty("badge-type", "proj-status")
        self._status_badge.setProperty("badge-value", project.status)
        self._status_badge.style().unpolish(self._status_badge)
        self._status_badge.style().polish(self._status_badge)

        priority_text, _theme_key = _priority_theme_keys().get(
            project.priority, (project.priority, "accent_start")
        )
        self._priority_badge.setText(
            tr("detail_priority_badge", "● {priority} Öncelik").format(priority=priority_text)
        )
        self._priority_badge.setProperty("badge-type", "proj-priority")
        self._priority_badge.setProperty("badge-value", project.priority)
        self._priority_badge.style().unpolish(self._priority_badge)
        self._priority_badge.style().polish(self._priority_badge)

        has_desc = bool(project.short_description)
        self._desc_header.setVisible(has_desc)
        self._desc_lbl.setVisible(has_desc)
        if has_desc:
            self._desc_lbl.setText(project.short_description)
        self._tasks_page.set_project(project.id)
        self._decisions_page.set_project(project.id)
        self._notes_page.set_project(project.id)
        self._resources_page.set_project(project.id)
        self._summary_problem.setText(
            tr("detail_summary_problem", "Problem: {value}").format(value=project.problem_statement or "-")
        )
        self._summary_target.setText(
            tr("detail_summary_target", "Hedef çıktı: {value}").format(value=project.target_outcome or "-")
        )
        self._summary_progress.setText(
            tr("detail_summary_progress", "İlerleme: %{percent}").format(
                percent=project.progress_percent
            )
        )
        self._refresh_outputs()

        has_github = bool(project.github_url)
        self._github_row.setVisible(has_github)
        if has_github:
            self._github_lbl.setText(project.github_url)

        self._stages_chevron.setText("▼")
        self._stage_timeline.setVisible(True)
        self._stages_expanded = True
        self._stack.setCurrentIndex(1)

    def _toggle_stages(self) -> None:
        self._stages_expanded = not self._stages_expanded
        self._stage_timeline.setVisible(self._stages_expanded)
        self._stages_chevron.setText("▼" if self._stages_expanded else "▶")

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
        archive_action = menu.addAction(tr("action_archive", "Arşivle"))
        archive_action.triggered.connect(
            lambda: self.archive_requested.emit(self._project_id)
        )
        menu.addSeparator()
        delete_action = menu.addAction(tr("action_delete", "Sil"))
        delete_action.triggered.connect(
            lambda: self.delete_requested.emit(self._project_id)
        )
        menu.exec(self._more_btn.mapToGlobal(self._more_btn.rect().bottomLeft()))

    def _refresh_outputs(self) -> None:
        self._outputs_list.clear()
        if self._project_id is None:
            return
        for item in self._di.project_controller.get_attachments_sync(self._project_id):
            self._outputs_list.addItem(QListWidgetItem(f"{item.file_path}\n{item.caption or ''}"))

    def _on_add_output(self) -> None:
        if self._project_id is None:
            return
        path, ok = QInputDialog.getText(
            self,
            tr("detail_output_add_title", "Çıktı Ekle"),
            tr("detail_output_add_prompt", "Dosya yolu veya bağlantı:"),
        )
        if not ok or not path.strip():
            return
        caption, _ = QInputDialog.getText(
            self,
            tr("detail_output_caption_title", "Çıktı Açıklaması"),
            tr("detail_output_caption_prompt", "Kısa açıklama:"),
        )
        self._di.project_controller.create_attachment_sync(
            Attachment(
                project_id=self._project_id,
                file_path=path.strip(),
                caption=caption.strip() or None,
                attachment_type="OUTPUT",
            )
        )
        self._refresh_outputs()
