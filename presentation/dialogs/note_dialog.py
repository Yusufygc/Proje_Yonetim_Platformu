from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from domain.enums.note_type import NoteType
from domain.models.note import Note
from presentation.dimensions import Spacing
from presentation.utils.i18n import tr
from presentation.widgets.voice_input_button import attach_voice_button


class NoteDialog(QDialog):
    """Yeni not ekleme veya düzenleme penceresi."""

    def __init__(self, parent: QWidget, note: Optional[Note] = None) -> None:
        super().__init__(parent=parent)
        self._note = note
        self._is_edit = note is not None
        self._setup_ui()
        if self._is_edit:
            self._populate_fields()

    def _setup_ui(self) -> None:
        title = (
            tr("note_dialog_edit_title", "Notu Düzenle")
            if self._is_edit
            else tr("note_dialog_new_title", "Yeni Not Ekle")
        )
        self.setWindowTitle(title)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXXL, Spacing.XXXL, Spacing.XXXL, Spacing.XXXL)
        layout.setSpacing(Spacing.XL)

        # Başlık
        layout.addWidget(QLabel(tr("note_dialog_title_label", "Not Başlığı *"), parent=self))
        self._title_edit = QLineEdit(parent=self)
        self._title_edit.setPlaceholderText(tr("note_dialog_title_placeholder", "Örn: Toplantı Notları..."))
        layout.addWidget(self._title_edit)

        # Tür
        layout.addWidget(QLabel(tr("label_kind", "Tür"), parent=self))
        self._type_combo = QComboBox(parent=self)
        _note_type_labels = {
            NoteType.GENERAL.value:        tr("note_type_general",        "Genel"),
            NoteType.MEETING.value:        tr("note_type_meeting",        "Toplantı"),
            NoteType.RESEARCH.value:       tr("note_type_research",       "Araştırma"),
            NoteType.DEBUG.value:          tr("note_type_debug",          "Hata Ayıklama"),
            NoteType.LESSON_LEARNED.value: tr("note_type_lesson_learned", "Öğrenilen Ders"),
            NoteType.RELEASE.value:        tr("note_type_release",        "Yayın"),
        }
        for t in NoteType:
            self._type_combo.addItem(_note_type_labels[t.value], t.value)
        layout.addWidget(self._type_combo)

        # İçerik
        layout.addWidget(QLabel(tr("note_dialog_body_label", "İçerik *"), parent=self))
        self._body_edit = QTextEdit(parent=self)
        self._body_edit.setPlaceholderText(tr("note_dialog_body_placeholder", "Notunuz..."))
        self._body_edit.setMinimumHeight(150)
        layout.addWidget(attach_voice_button(self._body_edit, self))

        layout.addStretch()

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton(tr("action_cancel", "İptal"), parent=self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton(tr("action_save", "Kaydet"), parent=self)
        save_btn.setObjectName("accent_button")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)

    def _populate_fields(self) -> None:
        if not self._note:
            return
        self._title_edit.setText(self._note.title)
        self._body_edit.setText(self._note.body)
        idx = self._type_combo.findData(self._note.note_type)
        if idx >= 0:
            self._type_combo.setCurrentIndex(idx)

    def get_data(self) -> dict:
        return {
            "title": self._title_edit.text(),
            "body": self._body_edit.toPlainText(),
            "note_type": self._type_combo.currentData(),
        }
