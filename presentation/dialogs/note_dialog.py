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
        title = "Notu Düzenle" if self._is_edit else "Yeni Not Ekle"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Başlık
        layout.addWidget(QLabel("Not Başlığı *", parent=self))
        self._title_edit = QLineEdit(parent=self)
        self._title_edit.setPlaceholderText("Örn: Toplantı Notları...")
        layout.addWidget(self._title_edit)

        # Tür
        layout.addWidget(QLabel("Tür", parent=self))
        self._type_combo = QComboBox(parent=self)
        for t in NoteType:
            self._type_combo.addItem(t.value, t.value)
        layout.addWidget(self._type_combo)

        # İçerik
        layout.addWidget(QLabel("İçerik *", parent=self))
        self._body_edit = QTextEdit(parent=self)
        self._body_edit.setPlaceholderText("Notunuz...")
        self._body_edit.setMinimumHeight(150)
        layout.addWidget(self._body_edit)

        layout.addStretch()

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("İptal", parent=self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Kaydet", parent=self)
        save_btn.setObjectName("accent_button")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)

    def _populate_fields(self) -> None:
        if not self._note:
            return
        self._title_edit.setText(self._note.title)
        self._body_edit.setText(self._note.body)
        self._type_combo.setCurrentText(self._note.note_type)

    def get_data(self) -> dict:
        return {
            "title": self._title_edit.text(),
            "body": self._body_edit.toPlainText(),
            "note_type": self._type_combo.currentText(),
        }
