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
        title = "Kararı Düzenle" if self._is_edit else "Yeni Karar Ekle"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Başlık
        layout.addWidget(QLabel("Karar Başlığı *", parent=self))
        self._title_edit = QLineEdit(parent=self)
        self._title_edit.setPlaceholderText("Örn: Veritabanı seçimi...")
        layout.addWidget(self._title_edit)

        # Durum
        layout.addWidget(QLabel("Durum", parent=self))
        self._status_combo = QComboBox(parent=self)
        for s in DecisionStatus:
            self._status_combo.addItem(s.value, s.value)
        layout.addWidget(self._status_combo)

        # Karar
        layout.addWidget(QLabel("Karar *", parent=self))
        self._decision_edit = QTextEdit(parent=self)
        self._decision_edit.setPlaceholderText("Verilen karar nedir?")
        self._decision_edit.setMaximumHeight(80)
        layout.addWidget(self._decision_edit)

        # Gerekçe
        layout.addWidget(QLabel("Gerekçe", parent=self))
        self._rationale_edit = QTextEdit(parent=self)
        self._rationale_edit.setPlaceholderText("Neden bu karar alındı?")
        self._rationale_edit.setMaximumHeight(80)
        layout.addWidget(self._rationale_edit)

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
        if not self._decision:
            return
        self._title_edit.setText(self._decision.title)
        self._decision_edit.setText(self._decision.decision)
        if self._decision.rationale:
            self._rationale_edit.setText(self._decision.rationale)
        self._status_combo.setCurrentText(self._decision.status)

    def get_data(self) -> dict:
        return {
            "title": self._title_edit.text(),
            "decision": self._decision_edit.toPlainText(),
            "rationale": self._rationale_edit.toPlainText(),
            "status": self._status_combo.currentText(),
        }
