"""
Fikir havuzu sayfası.
Sol tarafta fikir listesi, sağ tarafta seçili fikrin detayları ve projeye dönüştürme seçeneği yer alır.
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
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
from presentation.dialogs.idea_dialog import IdeaDialog, _idea_status_labels
from presentation.dialogs.project_dialog import ProjectDialog
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr
from presentation.widgets.delete_icon_button import DeleteIconButton

_STATUS_THEME_KEYS = {
    IdeaStatus.RAW.value: "text_muted",
    IdeaStatus.REVIEWING.value: "warning",
    IdeaStatus.VALIDATING.value: "accent_start",
    IdeaStatus.CONVERTED.value: "success",
    IdeaStatus.DEFERRED.value: "text_secondary",
    IdeaStatus.REJECTED.value: "danger",
}

_IDEA_ROW_H = 52


class IdeaRowWidget(QWidget):
    """Fikir satırı: başlık + sağ tarafta çöp kutusu ikonu."""

    delete_requested = Signal(int)

    def __init__(self, idea: Idea, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.idea_id = idea.id
        # setItemWidget içinde QSS class'ları uygulanmadığı için arka plan şeffaf tutulur
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(self)
        # Item padding sıfırlandığı için dikey boşluğu satır widget'ı yönetir;
        # buton dikey ortalanır, hover zemini divider'a değmez.
        layout.setContentsMargins(12, 6, 10, 6)
        layout.setSpacing(8)

        title_lbl = QLabel(idea.title, parent=self)
        title_lbl.setStyleSheet(
            "color: #888888;" if idea.status == IdeaStatus.CONVERTED.value else ""
        )
        layout.addWidget(title_lbl, 1)

        del_btn = DeleteIconButton(parent=self)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.idea_id))
        layout.addWidget(del_btn, 0, Qt.AlignmentFlag.AlignVCenter)


class IdeaListItem(QListWidgetItem):
    def __init__(self, idea: Idea) -> None:
        super().__init__()
        self.idea = idea
        self.setData(Qt.ItemDataRole.UserRole, idea.id)
        self.setSizeHint(QSize(0, _IDEA_ROW_H))


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
        layout.setContentsMargins(Spacing.PAGE, Spacing.PAGE, Spacing.PAGE, Spacing.PAGE)
        layout.setSpacing(Spacing.XXXL)

        header = QWidget(parent=self)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(tr("ideas_title", "Fikir Havuzu"), parent=header)
        title.setProperty("cssClass", "title-medium")
        header_layout.addWidget(title)
        header_layout.addStretch()

        add_btn = QPushButton(tr("ideas_add_btn", "+ Yeni Fikir"), parent=header)
        add_btn.setMinimumSize(Size.BTN_IDEA_W, Size.BTN_IDEA_H)
        add_btn.setProperty("cssClass", "btn-primary")
        add_btn.clicked.connect(self._on_add_idea)
        header_layout.addWidget(add_btn)
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal, parent=self)
        splitter.setObjectName("ideas_splitter")

        list_container = QFrame(parent=splitter)
        list_container.setProperty("cssClass", "panel")
        list_layout = QVBoxLayout(list_container)

        self._list_widget = QListWidget(parent=list_container)
        self._list_widget.setObjectName("ideas_list")
        self._list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self._list_widget)

        self._empty_label = QLabel(
            tr("ideas_empty", "Henüz fikir yok.\nYeni oluşturmak için\n+ Yeni Fikir'e basın."),
            parent=list_container,
        )
        self._empty_label.setProperty("cssClass", "text-secondary")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        list_layout.addWidget(self._empty_label)

        self._detail_panel = QFrame(parent=splitter)
        self._detail_panel.setProperty("cssClass", "panel")
        self._detail_layout = QVBoxLayout(self._detail_panel)
        self._detail_layout.setContentsMargins(Spacing.PAGE, Spacing.PAGE, Spacing.PAGE, Spacing.PAGE)
        self._detail_layout.setSpacing(Spacing.XL)
        self._build_detail_panel()

        splitter.addWidget(list_container)
        splitter.addWidget(self._detail_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, 1)
        self._show_empty_state()

    def _build_detail_panel(self) -> None:
        self._detail_header = QWidget(parent=self._detail_panel)
        dh_layout = QHBoxLayout(self._detail_header)
        dh_layout.setContentsMargins(0, 0, 0, 0)

        self._idea_title = QLabel("", parent=self._detail_header)
        self._idea_title.setProperty("cssClass", "title-small")
        self._idea_title.setWordWrap(True)
        dh_layout.addWidget(self._idea_title, 1)

        self._idea_status = QLabel("", parent=self._detail_header)
        self._idea_status.setProperty("badge-type", "idea-status")
        dh_layout.addWidget(self._idea_status)

        self._detail_layout.addWidget(self._detail_header)
        self._detail_layout.addSpacing(20)

        self._desc_lbl = QLabel("", parent=self._detail_panel)
        self._desc_lbl.setProperty("cssClass", "text-secondary")
        self._desc_lbl.setWordWrap(True)
        self._detail_layout.addWidget(self._desc_lbl)
        self._detail_layout.addStretch()

        btn_row = QWidget(parent=self._detail_panel)
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()

        self._edit_btn = QPushButton(tr("action_edit", "Düzenle"), parent=btn_row)
        self._edit_btn.setMinimumHeight(Size.ACTION_BTN_H)
        self._edit_btn.setProperty("cssClass", "btn-secondary")
        self._edit_btn.clicked.connect(self._on_edit_idea)
        btn_layout.addWidget(self._edit_btn)

        self._convert_btn = QPushButton(tr("ideas_convert_btn", "Projeye Dönüştür"), parent=btn_row)
        self._convert_btn.setMinimumHeight(Size.ACTION_BTN_H)
        self._convert_btn.setProperty("cssClass", "btn-primary")
        self._convert_btn.clicked.connect(self._on_convert_to_project)
        btn_layout.addWidget(self._convert_btn)

        self._detail_layout.addWidget(btn_row)

    def _connect_signals(self) -> None:
        self._controller.ideas_loaded.connect(self._on_ideas_loaded)
        self._controller.idea_created.connect(self._on_idea_changed)
        self._controller.idea_updated.connect(self._on_idea_changed)
        self._controller.idea_deleted.connect(self._on_idea_deleted)
        self._controller.idea_converted.connect(self._on_idea_changed)
        self._controller.error_occurred.connect(self._on_error)
        self._list_widget.model().rowsMoved.connect(self._on_ideas_row_moved)

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
                row_widget = IdeaRowWidget(idea, parent=self._list_widget)
                row_widget.delete_requested.connect(self._on_delete_idea_by_id)
                self._list_widget.setItemWidget(item, row_widget)
                if self._selected_idea_id == idea.id:
                    item.setSelected(True)

        if not self._selected_idea_id or not self._list_widget.selectedItems():
            self._show_empty_state()

    def _on_ideas_row_moved(self, *_args: object) -> None:
        ordered_ids = [self._list_widget.item(i).idea.id for i in range(self._list_widget.count())]
        self._controller.reorder(ordered_ids)

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

        status_label = _idea_status_labels().get(idea.status, idea.status)
        self._idea_status.setText(status_label)
        self._idea_status.setProperty("badge-value", idea.status)
        self._idea_status.style().unpolish(self._idea_status)
        self._idea_status.style().polish(self._idea_status)

        desc = ""
        if idea.problem:
            desc += f"<b>{tr('idea_dialog_problem_label', 'Çözülen Problem')}:</b><br>{idea.problem}<br><br>"
        if idea.solution:
            desc += f"<b>{tr('idea_dialog_solution_label', 'Önerilen Çözüm')}:</b><br>{idea.solution}<br><br>"

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
            tr("ideas_convert_btn", "Projeye Dönüştür"),
            tr("ideas_convert_confirm", "Bu fikir için proje formu açılacak. Bilgileri kontrol edip onaylayın."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            dialog = ProjectDialog(parent=self)
            prefill = {
                "title": idea.title,
                "short_description": idea.problem,
                "problem_statement": idea.problem,
                "docs_url": idea.source_link,
            }
            dialog.set_prefill(prefill)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                self._controller.convert_to_project(self._selected_idea_id, **data)
                self._project_controller.load_projects()

    def _on_delete_idea_by_id(self, idea_id: int) -> None:
        reply = QMessageBox.question(
            self,
            tr("action_delete", "Sil"),
            tr("ideas_delete_confirm", "Bu fikri silmek istediğinizden emin misiniz?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._controller.delete_idea(idea_id)

    def _on_idea_deleted(self, _idea_id: int) -> None:
        self._selected_idea_id = None
        self._show_empty_state()
        self._controller.load_ideas()

    def _on_idea_changed(self, *args) -> None:
        if args:
            first = args[0]
            if hasattr(first, "id"):
                self._selected_idea_id = first.id
        self._controller.load_ideas()

    def _on_error(self, msg: str) -> None:
        QMessageBox.critical(self, tr("error_title", "Hata"), msg)
