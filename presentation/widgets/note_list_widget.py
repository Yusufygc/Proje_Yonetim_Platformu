from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from controllers.note_controller import NoteController
from core.managers.icon_manager import Icons
from core.managers.theme_manager import ThemeManager
from domain.models.note import Note
from presentation.dialogs.note_dialog import NoteDialog
from presentation.dimensions import Spacing
from presentation.utils.i18n import tr
from presentation.widgets.drag_reorder import DragReorderController
from presentation.widgets.icon_action_button import IconActionButton

_NOTE_TYPE_META: dict[str, tuple[str, str]] = {
    "GENERAL":        ("#78909C", "Genel"),  # l10n: data — anahtar + varsayılan, tr() ile _note_type_color_and_label'da tüketilir
    "MEETING":        ("#42A5F5", "Toplantı"),  # l10n: data
    "RESEARCH":       ("#26A69A", "Araştırma"),  # l10n: data
    "DEBUG":          ("#EF5350", "Hata Ayıklama"),  # l10n: data
    "LESSON_LEARNED": ("#66BB6A", "Öğrenilen Ders"),  # l10n: data
    "RELEASE":        ("#AB47BC", "Yayın"),  # l10n: data
}


def _note_type_color_and_label(note_type: str) -> tuple[str, str]:
    color, default_label = _NOTE_TYPE_META.get(note_type, ("#888888", note_type))
    return color, tr(f"note_type_{note_type.lower()}", default_label)


class _NoteRow(QFrame):
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, note: Note, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.note_id = note.id
        self.setProperty("cssClass", "panel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.XS)

        top = QHBoxLayout()
        top.setSpacing(Spacing.SM)

        color, label = _note_type_color_and_label(note.note_type)
        badge = QLabel(label, parent=self)
        badge.setStyleSheet(
            f"QLabel {{ background-color: transparent; color: {color};"
            f" border: 1px solid {color}; border-radius: 4px; padding: 1px 8px;"
            f" font-size: 11px; font-weight: 600; }}"
        )
        top.addWidget(badge)

        title_lbl = QLabel(note.title, parent=self)
        title_lbl.setProperty("cssClass", "text-primary")
        title_lbl.setStyleSheet("font-weight: 600; font-size: 13px;")
        top.addWidget(title_lbl, 1)

        muted = ThemeManager.instance().color("text_muted")
        edit_btn = IconActionButton(
            Icons.PENCIL, muted, "#4A90D9", tr("action_edit", "Düzenle"), parent=self
        )
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.note_id))
        top.addWidget(edit_btn)

        del_btn = IconActionButton(
            Icons.TRASH, muted, "#E53935", tr("action_delete", "Sil"), parent=self
        )
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.note_id))
        top.addWidget(del_btn)

        layout.addLayout(top)

        if note.body:
            body_lbl = QLabel(note.body, parent=self)
            body_lbl.setProperty("cssClass", "text-secondary")
            body_lbl.setWordWrap(True)
            body_lbl.setStyleSheet("font-size: 12px; padding-left: 2px;")
            layout.addWidget(body_lbl)


class NoteListWidget(QWidget):
    """Proje notlarını modern satır düzeniyle listeleyen sekme widget'ı."""

    def __init__(self, controller: NoteController, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._project_id: int | None = None
        self._rows: dict[int, _NoteRow] = {}
        self._setup_ui()
        self._drag_controller = DragReorderController(
            self._list_layout, self._row_note_id, self._on_rows_reordered, parent=self
        )
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

        scroll = QScrollArea(parent=self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setAutoFillBackground(False)
        scroll.viewport().setAutoFillBackground(False)

        self._container = QWidget(parent=scroll)
        self._container.setProperty("cssClass", "transparent-bg")
        self._list_layout = QVBoxLayout(self._container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(Spacing.SM)
        self._list_layout.addStretch()

        scroll.setWidget(self._container)
        layout.addWidget(scroll, 1)

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
        self._clear()

        if not notes:
            empty = QLabel(tr("notes_empty", "Henüz not yok."), parent=self._container)
            empty.setProperty("cssClass", "text-muted")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("padding: 24px 0;")
            self._list_layout.insertWidget(0, empty)
            return

        for n in notes:
            row = _NoteRow(n, parent=self._container)
            row.edit_requested.connect(self._on_edit)
            row.delete_requested.connect(self._on_delete_confirm)
            pos = self._list_layout.count() - 1
            self._list_layout.insertWidget(pos, row)
            self._rows[n.id] = row
            self._drag_controller.install(row)

    @staticmethod
    def _row_note_id(row: QWidget) -> int | None:
        return getattr(row, "note_id", None)

    def _on_rows_reordered(self, ordered_ids: list[int]) -> None:
        self._controller.reorder(ordered_ids)

    def _clear(self) -> None:
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._rows.clear()

    def _on_add_note(self) -> None:
        if not self._project_id:
            return
        dialog = NoteDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            body = str(data.pop("body"))
            self._controller.create_note(self._project_id, title, body, **data)

    def _on_edit(self, note_id: int) -> None:
        note = self._controller.get_note_sync(note_id)
        if note:
            dialog = NoteDialog(parent=self, note=note)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._controller.update_note(note_id, **dialog.get_data())

    def _on_delete_confirm(self, note_id: int) -> None:
        reply = QMessageBox.question(
            self,
            tr("action_delete", "Sil"),
            tr("notes_delete_confirm", "Bu notu silmek istediğinize emin misiniz?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._controller.delete_note(note_id)
