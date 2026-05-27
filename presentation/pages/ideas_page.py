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
from domain.models.idea import Idea
from domain.enums.idea_status import IdeaStatus
from presentation.dialogs.idea_dialog import IdeaDialog

_STATUS_COLORS = {
    IdeaStatus.DRAFT.value: "#4A4D5C",
    IdeaStatus.REVIEWING.value: "#F59E0B",
    IdeaStatus.VALIDATING.value: "#6366F1",
    IdeaStatus.CONVERTED.value: "#22C55E",
    IdeaStatus.POSTPONED.value: "#8B8FA8",
    IdeaStatus.REJECTED.value: "#EF4444",
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
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #E8EAF0;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        add_btn = QPushButton("+ Yeni Fikir", parent=header)
        add_btn.setMinimumSize(140, 40)
        add_btn.setObjectName("accent_button")
        add_btn.setStyleSheet(
            "QPushButton { background-color: #6366F1; color: white; border: none; border-radius: 6px; font-weight: 600; }"
            "QPushButton:hover { background-color: #4F46E5; }"
        )
        add_btn.clicked.connect(self._on_add_idea)
        header_layout.addWidget(add_btn)

        layout.addWidget(header)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal, parent=self)
        splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        # Sol Liste
        list_container = QFrame(parent=splitter)
        list_container.setStyleSheet(
            "QFrame { background-color: #1E2130; border: 1px solid #2A2D38; border-radius: 12px; }"
        )
        list_layout = QVBoxLayout(list_container)
        
        self._list_widget = QListWidget(parent=list_container)
        self._list_widget.setStyleSheet(
            "QListWidget { background: transparent; border: none; color: #E8EAF0; font-size: 14px; }"
            "QListWidget::item { padding: 12px; border-bottom: 1px solid #2A2D38; }"
            "QListWidget::item:selected { background-color: #2A2D38; border-radius: 6px; }"
        )
        self._list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self._list_widget)

        self._empty_label = QLabel("Henüz fikir yok.\nYeni oluşturmak için\n+ Yeni Fikir'e basın.", parent=list_container)
        self._empty_label.setStyleSheet("color: #8B8FA8; font-size: 13px;")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        list_layout.addWidget(self._empty_label)

        # Sağ Detay Paneli
        self._detail_panel = QFrame(parent=splitter)
        self._detail_panel.setStyleSheet(
            "QFrame { background-color: #1E2130; border: 1px solid #2A2D38; border-radius: 12px; }"
        )
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
        self._idea_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        self._idea_title.setWordWrap(True)
        dh_layout.addWidget(self._idea_title, 1)
        
        self._idea_status = QLabel("", parent=self._detail_header)
        self._idea_status.setStyleSheet("padding: 4px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;")
        dh_layout.addWidget(self._idea_status)
        
        self._detail_layout.addWidget(self._detail_header)
        self._detail_layout.addSpacing(20)

        # Detay alanları
        self._desc_lbl = QLabel("", parent=self._detail_panel)
        self._desc_lbl.setStyleSheet("color: #8B8FA8; font-size: 14px; line-height: 1.5;")
        self._desc_lbl.setWordWrap(True)
        self._detail_layout.addWidget(self._desc_lbl)
        
        self._detail_layout.addStretch()

        # Butonlar
        btn_row = QWidget(parent=self._detail_panel)
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(0,0,0,0)
        
        self._edit_btn = QPushButton("Düzenle", parent=btn_row)
        self._edit_btn.setMinimumHeight(36)
        self._edit_btn.setStyleSheet("background-color: #2A2D38; color: white; border-radius: 6px;")
        self._edit_btn.clicked.connect(self._on_edit_idea)
        btn_layout.addWidget(self._edit_btn)
        
        self._convert_btn = QPushButton("Projeye Dönüştür", parent=btn_row)
        self._convert_btn.setMinimumHeight(36)
        self._convert_btn.setStyleSheet("background-color: #22C55E; color: white; border-radius: 6px; font-weight: bold;")
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
        
        color = _STATUS_COLORS.get(idea.status, "#8B8FA8")
        self._idea_status.setText(idea.status)
        self._idea_status.setStyleSheet(f"background-color: {color}22; color: {color}; padding: 4px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;")
        
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
            
        reply = QMessageBox.question(
            self,
            "Projeye Dönüştür",
            "Bu fikir için yeni bir proje oluşturulacak. Onaylıyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._controller.convert_to_project(self._selected_idea_id)
            # Projeler yenilenmeli
            self._project_controller.load_projects()

    def _on_idea_changed(self, *args) -> None:
        self._controller.load_ideas()

    def _on_error(self, msg: str) -> None:
        QMessageBox.critical(self, "Hata", msg)
