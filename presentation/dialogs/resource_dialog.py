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

from domain.enums.resource_type import ResourceType
from domain.models.resource import Resource


class ResourceDialog(QDialog):
    """Yeni kaynak ekleme veya düzenleme penceresi."""

    def __init__(self, parent: QWidget, resource: Optional[Resource] = None) -> None:
        super().__init__(parent=parent)
        self._resource = resource
        self._is_edit = resource is not None
        self._setup_ui()
        if self._is_edit:
            self._populate_fields()

    def _setup_ui(self) -> None:
        title = "Kaynağı Düzenle" if self._is_edit else "Yeni Kaynak Ekle"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Başlık
        layout.addWidget(QLabel("Kaynak Başlığı *", parent=self))
        self._title_edit = QLineEdit(parent=self)
        self._title_edit.setPlaceholderText("Örn: API Dokümantasyonu...")
        layout.addWidget(self._title_edit)

        # Tür
        layout.addWidget(QLabel("Tür", parent=self))
        self._type_combo = QComboBox(parent=self)
        for t in ResourceType:
            self._type_combo.addItem(t.value, t.value)
        layout.addWidget(self._type_combo)

        # URL
        layout.addWidget(QLabel("URL *", parent=self))
        self._url_edit = QLineEdit(parent=self)
        self._url_edit.setPlaceholderText("Örn: https://...")
        layout.addWidget(self._url_edit)

        # Açıklama
        layout.addWidget(QLabel("Açıklama", parent=self))
        self._desc_edit = QTextEdit(parent=self)
        self._desc_edit.setPlaceholderText("Kaynak hakkında ek bilgi...")
        self._desc_edit.setMaximumHeight(80)
        layout.addWidget(self._desc_edit)

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
        if not self._resource:
            return
        self._title_edit.setText(self._resource.title)
        self._url_edit.setText(self._resource.url)
        if self._resource.description:
            self._desc_edit.setText(self._resource.description)
        self._type_combo.setCurrentText(self._resource.resource_type)

    def get_data(self) -> dict:
        return {
            "title": self._title_edit.text(),
            "url": self._url_edit.text(),
            "description": self._desc_edit.toPlainText(),
            "resource_type": self._type_combo.currentText(),
        }
