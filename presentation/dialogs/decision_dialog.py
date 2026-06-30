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

from domain.enums.decision_status import DecisionStatus
from domain.models.decision_record import DecisionRecord
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr
from presentation.widgets.voice_input_button import attach_voice_button


class DecisionDialog(QDialog):
    """Yeni karar ekleme veya düzenleme penceresi."""

    def __init__(self, parent: QWidget, decision: Optional[DecisionRecord] = None) -> None:
        super().__init__(parent=parent)
        self._decision = decision
        self._is_edit = decision is not None
        self._setup_ui()
        if self._is_edit:
            self._populate_fields()

    def _setup_ui(self) -> None:
        title = (
            tr("decision_dialog_edit_title", "Kararı Düzenle")
            if self._is_edit
            else tr("decision_dialog_new_title", "Yeni Karar Ekle")
        )
        self.setWindowTitle(title)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXXL, Spacing.XXXL, Spacing.XXXL, Spacing.XXXL)
        layout.setSpacing(Spacing.XL)

        # Başlık
        layout.addWidget(QLabel(tr("decision_dialog_title_label", "Karar Başlığı *"), parent=self))
        self._title_edit = QLineEdit(parent=self)
        self._title_edit.setPlaceholderText(tr("decision_dialog_title_placeholder", "Örn: Veritabanı seçimi..."))
        layout.addWidget(self._title_edit)

        # Durum
        layout.addWidget(QLabel(tr("label_status", "Durum"), parent=self))
        self._status_combo = QComboBox(parent=self)
        _decision_status_labels = {
            DecisionStatus.DRAFT.value:      tr("decision_status_draft",     "Taslak"),
            DecisionStatus.ACCEPTED.value:   tr("decision_status_accepted",  "✅ Kabul Edildi"),
            DecisionStatus.SUPERSEDED.value: tr("decision_status_superseded","Güncellendi"),
            DecisionStatus.CANCELLED.value:  tr("decision_status_cancelled", "❌ İptal Edildi"),
        }
        for s in DecisionStatus:
            self._status_combo.addItem(_decision_status_labels[s.value], s.value)
        layout.addWidget(self._status_combo)

        # Karar
        layout.addWidget(QLabel(tr("decision_dialog_decision_label", "Karar *"), parent=self))
        self._decision_edit = QTextEdit(parent=self)
        self._decision_edit.setPlaceholderText(tr("decision_dialog_decision_placeholder", "Verilen karar nedir?"))
        self._decision_edit.setMaximumHeight(Size.TEXTAREA_H_LG)
        layout.addWidget(attach_voice_button(self._decision_edit, self))

        # Gerekçe
        layout.addWidget(QLabel(tr("decision_dialog_rationale_label", "Gerekçe"), parent=self))
        self._rationale_edit = QTextEdit(parent=self)
        self._rationale_edit.setPlaceholderText(tr("decision_dialog_rationale_placeholder", "Neden bu karar alındı?"))
        self._rationale_edit.setMaximumHeight(Size.TEXTAREA_H_LG)
        layout.addWidget(attach_voice_button(self._rationale_edit, self))

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
        if not self._decision:
            return
        self._title_edit.setText(self._decision.title)
        self._decision_edit.setText(self._decision.decision)
        if self._decision.rationale:
            self._rationale_edit.setText(self._decision.rationale)
        idx = self._status_combo.findData(self._decision.status)
        if idx >= 0:
            self._status_combo.setCurrentIndex(idx)

    def get_data(self) -> dict:
        return {
            "title": self._title_edit.text(),
            "decision": self._decision_edit.toPlainText(),
            "rationale": self._rationale_edit.toPlainText(),
            "status": self._status_combo.currentData(),
        }
