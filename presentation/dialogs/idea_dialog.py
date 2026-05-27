from typing import Optional

from PySide6.QtCore import Qt
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

from domain.enums.idea_priority import IdeaPriority
from domain.enums.idea_status import IdeaStatus
from domain.models.idea import Idea


class IdeaDialog(QDialog):
    """Yeni fikir ekleme veya düzenleme penceresi."""

    def __init__(self, parent: QWidget, idea: Optional[Idea] = None) -> None:
        super().__init__(parent=parent)
        self._idea = idea
        self._is_edit = idea is not None
        self._setup_ui()
        if self._is_edit:
            self._populate_fields()

    def _setup_ui(self) -> None:
        title = "Fikri Düzenle" if self._is_edit else "Yeni Fikir Ekle"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setStyleSheet(
            "QDialog { background-color: #1E2130; }"
            "QLabel { color: #8B8FA8; font-weight: 600; font-size: 13px; }"
            "QLineEdit, QTextEdit { background-color: #161820; border: 1px solid #2A2D38; border-radius: 6px; padding: 8px; color: #E8EAF0; }"
            "QLineEdit:focus, QTextEdit:focus { border: 1px solid #6366F1; }"
            "QComboBox { background-color: #161820; border: 1px solid #2A2D38; border-radius: 6px; padding: 8px; color: #E8EAF0; }"
            "QPushButton { background-color: #2A2D38; color: #E8EAF0; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 600; }"
            "QPushButton:hover { background-color: #3B3E4D; }"
            "QPushButton#accent_button { background-color: #6366F1; color: white; }"
            "QPushButton#accent_button:hover { background-color: #4F46E5; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Başlık
        layout.addWidget(QLabel("Fikir Başlığı *", parent=self))
        self._title_edit = QLineEdit(parent=self)
        self._title_edit.setPlaceholderText("Örn: Yeni mobil uygulama fikri...")
        layout.addWidget(self._title_edit)

        # Durum ve Öncelik Yan Yana
        combo_row = QHBoxLayout()
        combo_row.setSpacing(16)
        
        status_col = QVBoxLayout()
        status_col.addWidget(QLabel("Durum", parent=self))
        self._status_combo = QComboBox(parent=self)
        for s in IdeaStatus:
            self._status_combo.addItem(s.value, s.value)
        status_col.addWidget(self._status_combo)
        combo_row.addLayout(status_col)

        priority_col = QVBoxLayout()
        priority_col.addWidget(QLabel("Öncelik", parent=self))
        self._priority_combo = QComboBox(parent=self)
        for p in IdeaPriority:
            self._priority_combo.addItem(p.value, p.value)
        priority_col.addWidget(self._priority_combo)
        combo_row.addLayout(priority_col)

        layout.addLayout(combo_row)

        # Problem
        layout.addWidget(QLabel("Çözülen Problem", parent=self))
        self._problem_edit = QTextEdit(parent=self)
        self._problem_edit.setPlaceholderText("Bu fikir hangi problemi çözüyor?")
        self._problem_edit.setMaximumHeight(80)
        layout.addWidget(self._problem_edit)

        # Çözüm (Solution)
        layout.addWidget(QLabel("Önerilen Çözüm", parent=self))
        self._solution_edit = QTextEdit(parent=self)
        self._solution_edit.setPlaceholderText("Önerdiğiniz çözüm detayları...")
        self._solution_edit.setMaximumHeight(80)
        layout.addWidget(self._solution_edit)

        # Hedef Çıktı / Değer (Expected Value)
        layout.addWidget(QLabel("Beklenen Değer / Çıktı", parent=self))
        self._expected_edit = QLineEdit(parent=self)
        self._expected_edit.setPlaceholderText("Örn: Aylık %10 ciro artışı")
        layout.addWidget(self._expected_edit)

        # Kaynak URL
        layout.addWidget(QLabel("Kaynak URL", parent=self))
        self._source_edit = QLineEdit(parent=self)
        self._source_edit.setPlaceholderText("Örn: https://github.com/ornek")
        layout.addWidget(self._source_edit)

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
        if not self._idea:
            return
        self._title_edit.setText(self._idea.title)
        if self._idea.problem:
            self._problem_edit.setText(self._idea.problem)
        if self._idea.solution:
            self._solution_edit.setText(self._idea.solution)
        if self._idea.expected_value:
            self._expected_edit.setText(self._idea.expected_value)
        if self._idea.source_link:
            self._source_edit.setText(self._idea.source_link)
        
        self._status_combo.setCurrentText(self._idea.status)
        self._priority_combo.setCurrentText(self._idea.priority)

    def get_data(self) -> dict:
        return {
            "title": self._title_edit.text(),
            "problem": self._problem_edit.toPlainText(),
            "solution": self._solution_edit.toPlainText(),
            "expected_value": self._expected_edit.text(),
            "source_link": self._source_edit.text(),
            "status": self._status_combo.currentText(),
            "priority": self._priority_combo.currentText(),
        }
