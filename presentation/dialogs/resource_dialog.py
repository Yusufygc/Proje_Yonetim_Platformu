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
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr


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
        title = (
            tr("resource_dialog_edit_title", "Kaynağı Düzenle")
            if self._is_edit
            else tr("resource_dialog_new_title", "Yeni Kaynak Ekle")
        )
        self.setWindowTitle(title)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXXL, Spacing.XXXL, Spacing.XXXL, Spacing.XXXL)
        layout.setSpacing(Spacing.XL)

        # Başlık
        layout.addWidget(QLabel(tr("resource_dialog_title_label", "Kaynak Başlığı *"), parent=self))
        self._title_edit = QLineEdit(parent=self)
        self._title_edit.setPlaceholderText(tr("resource_dialog_title_placeholder", "Örn: API Dokümantasyonu..."))
        layout.addWidget(self._title_edit)

        # Tür
        layout.addWidget(QLabel(tr("label_kind", "Tür"), parent=self))
        self._type_combo = QComboBox(parent=self)
        _resource_type_labels = {
            ResourceType.DOCUMENT.value: tr("resource_type_document", "Doküman"),
            ResourceType.ARTICLE.value:  tr("resource_type_article",  "Makale"),
            ResourceType.VIDEO.value:    tr("resource_type_video",    "Video"),
            ResourceType.GITHUB.value:   tr("resource_type_github",   "GitHub / Repo"),
            ResourceType.DESIGN.value:   tr("resource_type_design",   "Tasarım"),
            ResourceType.API.value:      tr("resource_type_api",      "API Referansı"),
            ResourceType.TOOL.value:     tr("resource_type_tool",     "Araç"),
            ResourceType.OTHER.value:    tr("resource_type_other",    "Diğer"),
        }
        for t in ResourceType:
            self._type_combo.addItem(_resource_type_labels[t.value], t.value)
        layout.addWidget(self._type_combo)

        # URL
        layout.addWidget(QLabel("URL *", parent=self))
        self._url_edit = QLineEdit(parent=self)
        self._url_edit.setPlaceholderText("https://...")
        layout.addWidget(self._url_edit)

        # Açıklama
        layout.addWidget(QLabel(tr("label_description", "Açıklama"), parent=self))
        self._desc_edit = QTextEdit(parent=self)
        self._desc_edit.setPlaceholderText(tr("resource_dialog_desc_placeholder", "Kaynak hakkında ek bilgi..."))
        self._desc_edit.setMaximumHeight(Size.TEXTAREA_H_LG)
        layout.addWidget(self._desc_edit)

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
        if not self._resource:
            return
        self._title_edit.setText(self._resource.title)
        self._url_edit.setText(self._resource.url)
        if self._resource.description:
            self._desc_edit.setText(self._resource.description)
        idx = self._type_combo.findData(self._resource.resource_type)
        if idx >= 0:
            self._type_combo.setCurrentIndex(idx)

    def get_data(self) -> dict:
        return {
            "title": self._title_edit.text(),
            "url": self._url_edit.text(),
            "description": self._desc_edit.toPlainText(),
            "resource_type": self._type_combo.currentData(),
        }
