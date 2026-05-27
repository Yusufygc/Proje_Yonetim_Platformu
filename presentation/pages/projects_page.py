"""
Projeler sayfası — sol liste paneli ve sağ detay paneli.
ProjectController üzerinden proje CRUD işlemlerini yönetir.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from controllers.project_controller import ProjectController
from controllers.stage_controller import StageController
from controllers.task_controller import TaskController
from domain.models.project import Project
from presentation.dialogs.project_dialog import ProjectDialog
from presentation.widgets.project_detail_panel import ProjectDetailPanel
from presentation.widgets.project_list_item import ProjectListItem


from di_container import DIContainer

class ProjectsPage(QWidget):
    """Sol liste + sağ detay görünümünü barındıran proje yönetim sayfası."""

    def __init__(
        self,
        parent: QWidget,
        di_container: DIContainer,
    ) -> None:
        super().__init__(parent=parent)
        self._di = di_container
        self._controller = di_container.project_controller
        self._stage_controller = di_container.stage_controller
        self._task_controller = di_container.task_controller
        self._selected_project_id: int | None = None
        self._selected_item: ProjectListItem | None = None
        self._list_items: dict[int, ProjectListItem] = {}
        self._stages = []
        self._setup_ui()
        self._connect_signals()
        self._controller.load_projects()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_left_panel())

        divider = QFrame(parent=self)
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet("background: #2A2D38; max-width: 1px; border: none;")
        layout.addWidget(divider)

        self._detail_panel = ProjectDetailPanel(parent=self, di=self._di)
        layout.addWidget(self._detail_panel, 1)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget(parent=self)
        panel.setFixedWidth(280)
        panel.setStyleSheet("background: #161820;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_panel_header(panel))

        self._search_edit = QLineEdit(parent=panel)
        self._search_edit.setPlaceholderText("Proje ara...")
        self._search_edit.setStyleSheet(
            "margin: 0 12px 12px 12px; padding: 8px 12px;"
            " border-radius: 8px; border: 1px solid #2A2D38;"
        )
        self._search_edit.textChanged.connect(self._on_search)
        layout.addWidget(self._search_edit)

        scroll = QScrollArea(parent=panel)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._list_container = QWidget(parent=scroll)
        self._list_container.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(8, 0, 8, 8)
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_container)
        layout.addWidget(scroll, 1)

        return panel

    def _build_panel_header(self, parent: QWidget) -> QWidget:
        header = QWidget(parent=parent)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 16, 12, 12)

        title = QLabel("Projeler", parent=header)
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #E8EAF0;")
        layout.addWidget(title, 1)

        new_btn = QPushButton("+", parent=header)
        new_btn.setFixedSize(28, 28)
        new_btn.setObjectName("accent_button")
        new_btn.setToolTip("Yeni Proje Oluştur")
        new_btn.clicked.connect(self._on_new_project)
        layout.addWidget(new_btn)

        return header

    def _connect_signals(self) -> None:
        self._controller.projects_loaded.connect(self._on_projects_loaded)
        self._controller.project_created.connect(self._on_project_created)
        self._controller.project_updated.connect(self._on_project_updated)
        self._controller.project_deleted.connect(self._on_project_removed)
        self._controller.project_archived.connect(self._on_project_removed)
        self._controller.error_occurred.connect(self._on_error)
        self._detail_panel.edit_requested.connect(self._on_edit_project)
        self._detail_panel.archive_requested.connect(self._controller.archive_project)
        self._detail_panel.delete_requested.connect(self._on_delete_project_confirm)
        self._detail_panel.complete_stage_requested.connect(self._stage_controller.complete_stage)
        self._detail_panel.activate_stage_requested.connect(self._stage_controller.activate_stage)
        self._stage_controller.stages_loaded.connect(self._on_stages_loaded)
        self._stage_controller.stage_updated.connect(self._on_stage_updated)
        self._stage_controller.error_occurred.connect(self._on_error)

    def _on_projects_loaded(self, projects: list[Project]) -> None:
        self._clear_list()
        for project in projects:
            self._add_item(project)
        if self._selected_project_id in self._list_items:
            item = self._list_items[self._selected_project_id]
            item.set_selected(True)
            self._selected_item = item
            project = self._controller.get_project_sync(self._selected_project_id)
            if project:
                self._detail_panel.show_project(project)
                self._stage_controller.load_stages(self._selected_project_id)
                self._task_controller.load_tasks(self._selected_project_id)
        else:
            self._selected_project_id = None
            self._detail_panel.show_empty_state()

    def _add_item(self, project: Project) -> None:
        item = ProjectListItem(project=project, parent=self._list_container)
        item.clicked.connect(self._on_item_clicked)
        count = self._list_layout.count()
        self._list_layout.insertWidget(count - 1, item)
        self._list_items[project.id] = item

    def _clear_list(self) -> None:
        while self._list_layout.count() > 1:
            child = self._list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._list_items.clear()
        self._selected_item = None

    def _on_item_clicked(self, project_id: int) -> None:
        if self._selected_item:
            self._selected_item.set_selected(False)
        self._selected_project_id = project_id
        item = self._list_items.get(project_id)
        if item:
            item.set_selected(True)
            self._selected_item = item
        project = self._controller.get_project_sync(project_id)
        if project:
            self._detail_panel.show_project(project)
            self._stage_controller.load_stages(project_id)
            self._task_controller.load_tasks(project_id)

    def _on_new_project(self) -> None:
        dialog = ProjectDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            self._controller.create_project(title, **data)

    def _on_edit_project(self, project_id: int) -> None:
        project = self._controller.get_project_sync(project_id)
        if project is None:
            return
        dialog = ProjectDialog(parent=self, project=project)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._controller.update_project(project_id, **dialog.get_data())

    def _on_delete_project_confirm(self, project_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Projeyi Sil",
            "Bu projeyi kalıcı olarak silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._controller.delete_project(project_id)

    def _on_project_created(self, project: Project) -> None:
        self._selected_project_id = project.id
        self._controller.load_projects()

    def _on_project_updated(self, _project: Project) -> None:
        self._controller.load_projects()

    def _on_project_removed(self, project_id: int) -> None:
        if self._selected_project_id == project_id:
            self._selected_project_id = None
        self._controller.load_projects()

    def _on_search(self, text: str) -> None:
        text_lower = text.lower().strip()
        for item in self._list_items.values():
            item.setVisible(item.matches_filter(text_lower))

    def _on_stage_updated(self, _stage: object) -> None:
        if self._selected_project_id is not None:
            self._stage_controller.load_stages(self._selected_project_id)

    def _on_stages_loaded(self, stages: list) -> None:
        self._stages = stages
        self._detail_panel.update_stages(stages)

    def _on_error(self, message: str) -> None:
        QMessageBox.critical(self, "Hata", message)
