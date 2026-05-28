"""
Fikir havuzu sayfası.
Sol tarafta fikir listesi, sağ tarafta seçili fikrin detayları ve projeye dönüştürme seçeneği yer alır.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from controllers.idea_controller import IdeaController
from controllers.project_controller import ProjectController
from domain.enums.idea_status import IdeaStatus
from domain.models.idea import Idea
from presentation.dialogs.idea_dialog import IdeaDialog, _IDEA_STATUS_LABELS
from presentation.dialogs.project_dialog import ProjectDialog

_STATUS_THEME_KEYS = {
    IdeaStatus.RAW.value: "text_muted",
    IdeaStatus.REVIEWING.value: "warning",
    IdeaStatus.VALIDATING.value: "accent_start",
    IdeaStatus.CONVERTED.value: "success",
    IdeaStatus.DEFERRED.value: "text_secondary",
    IdeaStatus.REJECTED.value: "danger",
}

class IdeaListItem(QListWidgetItem):
    def __init__(self, idea: Idea) -> None:
        super().__init__()
        self.idea = idea
        self.setText(idea.title)
        self.setData(Qt.ItemDataRole.UserRole, idea.id)
        
        if idea.status == IdeaStatus.CONVERTED.value:
            self.setForeground(Qt.GlobalColor.darkGray)

class IdeasPage(QWidget):
    """Fikirlerin listelendiği ve yönetildiği sayfa."""

    def __init__(
        self,
        parent: QWidget,
        idea_controller: IdeaController,
        project_controller: ProjectController,
    ) -> None:
        super().__init__(parent=parent)
        self._controller = idea_controller
        self._project_controller = project_controller
        self._selected_idea_id: int | None = None
        self._setup_ui()
        self._connect_signals()
        self._controller.load_ideas()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header = QWidget(parent=self)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Fikir Havuzu", parent=header)
        title.setProperty("cssClass", "title-medium")
        header_layout.addWidget(title)

        header_layout.addStretch()

        add_btn = QPushButton("+ Yeni Fikir", parent=header)
        add_btn.setMinimumSize(140, 40)
        add_btn.setProperty("cssClass", "btn-primary")
        add_btn.clicked.connect(self._on_add_idea)
        header_layout.addWidget(add_btn)

        layout.addWidget(header)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal, parent=self)
        splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        # Sol Liste
        list_container = QFrame(parent=splitter)
        list_container.setProperty("cssClass", "panel")
        list_layout = QVBoxLayout(list_container)
        
        self._list_widget = QListWidget(parent=list_container)
        # QListWidget stili artık global QSS içinde
        self._list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self._list_widget)

        self._empty_label = QLabel("Henüz fikir yok.\nYeni oluşturmak için\n+ Yeni Fikir'e basın.", parent=list_container)
        self._empty_label.setProperty("cssClass", "text-secondary")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        list_layout.addWidget(self._empty_label)

        # Sağ Detay Paneli
        self._detail_panel = QFrame(parent=splitter)
        self._detail_panel.setProperty("cssClass", "panel")
        self._detail_layout = QVBoxLayout(self._detail_panel)
        self._detail_layout.setContentsMargins(32, 32, 32, 32)
        self._detail_layout.setSpacing(16)
        
        self._build_detail_panel()
        
        splitter.addWidget(list_container)
        splitter.addWidget(self._detail_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, 1)
        self._show_empty_state()

    def _build_detail_panel(self) -> None:
        # Detay elemanları
        self._detail_header = QWidget(parent=self._detail_panel)
        dh_layout = QHBoxLayout(self._detail_header)
        dh_layout.setContentsMargins(0,0,0,0)
        
        self._idea_title = QLabel("", parent=self._detail_header)
        self._idea_title.setProperty("cssClass", "title-small")
        self._idea_title.setWordWrap(True)
        dh_layout.addWidget(self._idea_title, 1)
        
        self._idea_status = QLabel("", parent=self._detail_header)
        self._idea_status.setStyleSheet("padding: 4px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;")
        dh_layout.addWidget(self._idea_status)
        
        self._detail_layout.addWidget(self._detail_header)
        self._detail_layout.addSpacing(20)

        # Detay alanları
        self._desc_lbl = QLabel("", parent=self._detail_panel)
        self._desc_lbl.setProperty("cssClass", "text-secondary")
        self._desc_lbl.setWordWrap(True)
        self._detail_layout.addWidget(self._desc_lbl)
        
        self._detail_layout.addStretch()

        # Butonlar
        btn_row = QWidget(parent=self._detail_panel)
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(0,0,0,0)
        
        self._edit_btn = QPushButton("Düzenle", parent=btn_row)
        self._edit_btn.setMinimumHeight(36)
        self._edit_btn.setProperty("cssClass", "btn-secondary")
        self._edit_btn.clicked.connect(self._on_edit_idea)
        btn_layout.addWidget(self._edit_btn)
        
        self._convert_btn = QPushButton("Projeye Dönüştür", parent=btn_row)
        self._convert_btn.setMinimumHeight(36)
        self._convert_btn.setProperty("cssClass", "btn-primary")
        self._convert_btn.clicked.connect(self._on_convert_to_project)
        btn_layout.addWidget(self._convert_btn)
        
        self._detail_layout.addWidget(btn_row)

    def _connect_signals(self) -> None:
        self._controller.ideas_loaded.connect(self._on_ideas_loaded)
        self._controller.idea_created.connect(self._on_idea_changed)
        self._controller.idea_updated.connect(self._on_idea_changed)
        self._controller.idea_converted.connect(self._on_idea_changed)
        self._controller.error_occurred.connect(self._on_error)

    def _on_ideas_loaded(self, ideas: list[Idea]) -> None:
        self._list_widget.clear()
        
        if not ideas:
            self._list_widget.hide()
            self._empty_label.show()
        else:
            self._empty_label.hide()
            self._list_widget.show()
            for idea in ideas:
                item = IdeaListItem(idea)
                self._list_widget.addItem(item)
                if self._selected_idea_id == idea.id:
                    item.setSelected(True)
                
        if not self._selected_idea_id or not self._list_widget.selectedItems():
            self._show_empty_state()

    def _on_selection_changed(self) -> None:
        selected = self._list_widget.selectedItems()
        if selected:
            idea = selected[0].idea
            self._selected_idea_id = idea.id
            self._show_idea_detail(idea)
        else:
            self._selected_idea_id = None
            self._show_empty_state()

    def _show_empty_state(self) -> None:
        self._detail_header.setVisible(False)
        self._desc_lbl.setVisible(False)
        self._edit_btn.setVisible(False)
        self._convert_btn.setVisible(False)

    def _show_idea_detail(self, idea: Idea) -> None:
        self._detail_header.setVisible(True)
        self._desc_lbl.setVisible(True)
        
        self._idea_title.setText(idea.title)
        
        from core.managers.theme_manager import ThemeManager
        theme_key = _STATUS_THEME_KEYS.get(idea.status, "text_secondary")
        color = ThemeManager.instance().color(theme_key)
        status_label = _IDEA_STATUS_LABELS.get(idea.status, idea.status)
        self._idea_status.setText(status_label)
        self._idea_status.setStyleSheet(
            f"background-color: {color}22; color: {color};"
            f" padding: 4px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;"
        )
        
        desc = ""
        if idea.problem:
            desc += f"<b>Çözülen Problem:</b><br>{idea.problem}<br><br>"
        if idea.solution:
            desc += f"<b>Önerilen Çözüm:</b><br>{idea.solution}<br><br>"
        if idea.expected_value:
            desc += f"<b>Beklenen Değer:</b><br>{idea.expected_value}<br><br>"
            
        self._desc_lbl.setText(desc)
        
        is_converted = idea.status == IdeaStatus.CONVERTED.value
        self._edit_btn.setVisible(not is_converted)
        self._convert_btn.setVisible(not is_converted)

    def _on_add_idea(self) -> None:
        dialog = IdeaDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            self._controller.create_idea(title, **data)

    def _on_edit_idea(self) -> None:
        if not self._selected_idea_id:
            return
        idea = self._controller.get_idea_sync(self._selected_idea_id)
        if not idea:
            return
            
        dialog = IdeaDialog(parent=self, idea=idea)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._controller.update_idea(self._selected_idea_id, **dialog.get_data())

    def _on_convert_to_project(self) -> None:
        if not self._selected_idea_id:
            return
        idea = self._controller.get_idea_sync(self._selected_idea_id)
        if not idea:
            return
            
        reply = QMessageBox.question(
            self,
            "Projeye Dönüştür",
            "Bu fikir için proje formu açılacak. Bilgileri kontrol edip onaylayın.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            dialog = ProjectDialog(parent=self)
            prefill = {
                "title": idea.title,
                "short_description": idea.expected_value or idea.problem,
                "problem_statement": idea.problem,
                "full_description": idea.solution,
                "target_outcome": idea.expected_value,
                "docs_url": idea.source_link,
            }
            dialog.set_prefill(prefill)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                self._controller.convert_to_project(self._selected_idea_id, **data)
                self._project_controller.load_projects()

    def _on_idea_changed(self, *args) -> None:
        if args:
            first = args[0]
            if hasattr(first, "id"):
                self._selected_idea_id = first.id
        self._controller.load_ideas()

    def _on_error(self, msg: str) -> None:
        QMessageBox.critical(self, "Hata", msg)
