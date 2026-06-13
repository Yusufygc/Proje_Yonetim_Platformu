from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from controllers.note_controller import NoteController
from domain.enums.note_type import NoteType
from domain.models.note import Note
from presentation.dialogs.note_dialog import NoteDialog
from presentation.dimensions import Spacing
from presentation.utils.i18n import tr


class NoteListWidget(QWidget):
    """Proje notlarını listeleyen sekme widget'ı."""

    def __init__(self, controller: NoteController, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._project_id: int | None = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.XL)

        header = QHBoxLayout()
        title = QLabel(tr("notes_title", "Proje Notları"), parent=self)
        title.setProperty("cssClass", "title-small")
        header.addWidget(title)

        header.addStretch()

        self._add_btn = QPushButton(tr("notes_add_btn", "+ Not Ekle"), parent=self)
        self._add_btn.setProperty("cssClass", "btn-primary")
        self._add_btn.clicked.connect(self._on_add_note)
        header.addWidget(self._add_btn)
        
        layout.addLayout(header)

        self._list_widget = QListWidget(parent=self)
        self._list_widget.setProperty("cssClass", "panel")
        self._list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list_widget.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self._list_widget)

    def _connect_signals(self) -> None:
        self._controller.notes_loaded.connect(self._on_notes_loaded)
        self._controller.note_created.connect(self._refresh)
        self._controller.note_updated.connect(self._refresh)
        self._controller.note_deleted.connect(self._refresh)

    def set_project(self, project_id: int) -> None:
        self._project_id = project_id
        self._refresh()

    def _refresh(self, *args) -> None:
        if self._project_id:
            self._controller.load_project_notes(self._project_id)

    def _on_notes_loaded(self, notes: list[Note]) -> None:
        self._list_widget.clear()
        for n in notes:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, n.id)
            
            _type_labels = {
                NoteType.GENERAL.value:        tr("note_type_general",        "Genel"),
                NoteType.MEETING.value:        tr("note_type_meeting",        "Toplantı"),
                NoteType.RESEARCH.value:       tr("note_type_research",       "Araştırma"),
                NoteType.DEBUG.value:          tr("note_type_debug",          "Hata Ayıklama"),
                NoteType.LESSON_LEARNED.value: tr("note_type_lesson_learned", "Öğrenilen Ders"),
                NoteType.RELEASE.value:        tr("note_type_release",        "Yayın"),
            }
            note_type_label = _type_labels.get(n.note_type, n.note_type)
            text = f"[{note_type_label}] {n.title}\n{n.body}"
            item.setText(text)
            self._list_widget.addItem(item)

    def _on_add_note(self) -> None:
        if not self._project_id:
            return
            
        dialog = NoteDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            body = str(data.pop("body"))
            self._controller.create_note(self._project_id, title, body, **data)

    def _on_context_menu(self, pos) -> None:
        item = self._list_widget.itemAt(pos)
        if not item:
            return
            
        note_id = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
                           
        edit_action = menu.addAction(tr("action_edit", "Düzenle"))
        delete_action = menu.addAction(tr("action_delete", "Sil"))
        
        action = menu.exec(self._list_widget.mapToGlobal(pos))
        if action == edit_action:
            note = self._controller.get_note_sync(note_id)
            if note:
                dialog = NoteDialog(parent=self, note=note)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self._controller.update_note(note_id, **dialog.get_data())
        elif action == delete_action:
            reply = QMessageBox.question(
                self,
                tr("action_delete", "Sil"),
                tr("notes_delete_confirm", "Bu notu silmek istediğinize emin misiniz?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._controller.delete_note(note_id)
