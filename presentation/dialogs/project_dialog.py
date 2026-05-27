"""
Proje oluşturma ve düzenleme için modal dialog.
Yeni proje için boş, var olan proje için alanlar dolu gelir.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from domain.enums.priority import Priority
from domain.enums.project_status import ProjectStatus
from domain.models.project import Project

_STATUS_LABELS: dict[str, str] = {
    ProjectStatus.PLANNED.value: "Planlandı",
    ProjectStatus.ACTIVE.value: "Aktif",
    ProjectStatus.ON_HOLD.value: "Beklemede",
    ProjectStatus.BLOCKED.value: "Engellendi",
    ProjectStatus.COMPLETED.value: "Tamamlandı",
    ProjectStatus.CANCELLED.value: "İptal Edildi",
}

_PRIORITY_LABELS: dict[str, str] = {
    Priority.LOW.value: "Düşük",
    Priority.MEDIUM.value: "Orta",
    Priority.HIGH.value: "Yüksek",
    Priority.CRITICAL.value: "Kritik",
}


class ProjectDialog(QDialog):
    """Proje oluşturma (project=None) veya düzenleme modal dialog'u."""

    def __init__(self, parent: QWidget, project: Project | None = None) -> None:
        super().__init__(parent=parent)
        self._project = project
        self._is_edit = project is not None
        self._setup_ui()
        if self._is_edit:
            self._populate_fields()

    def _setup_ui(self) -> None:
        title_text = "Projeyi Düzenle" if self._is_edit else "Yeni Proje Oluştur"
        self.setWindowTitle(title_text)
        self.setMinimumWidth(520)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(0)

        dialog_title = QLabel(title_text, parent=self)
        dialog_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #E8EAF0;")
        layout.addWidget(dialog_title)
        layout.addSpacing(20)

        layout.addWidget(self._make_field_label("Proje Başlığı *"))
        layout.addSpacing(6)
        self._title_edit = QLineEdit(parent=self)
        self._title_edit.setPlaceholderText("Projenin adını girin...")
        self._title_edit.setMinimumHeight(38)
        layout.addWidget(self._title_edit)
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("Kısa Açıklama"))
        layout.addSpacing(6)
        self._desc_edit = QTextEdit(parent=self)
        self._desc_edit.setPlaceholderText("Projeyi kısaca açıklayın (isteğe bağlı)...")
        self._desc_edit.setMaximumHeight(80)
        layout.addWidget(self._desc_edit)
        layout.addSpacing(16)

        layout.addWidget(self._build_status_priority_row())
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("GitHub URL"))
        layout.addSpacing(6)
        self._github_edit = QLineEdit(parent=self)
        self._github_edit.setPlaceholderText("https://github.com/kullanici/repo")
        self._github_edit.setMinimumHeight(38)
        layout.addWidget(self._github_edit)
        layout.addSpacing(28)

        layout.addWidget(self._build_button_row())

    def _make_field_label(self, text: str) -> QLabel:
        lbl = QLabel(text, parent=self)
        lbl.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #8B8FA8; letter-spacing: 0.5px;"
        )
        return lbl

    def _build_status_priority_row(self) -> QWidget:
        row = QWidget(parent=self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        status_col = QWidget(parent=row)
        sc_layout = QVBoxLayout(status_col)
        sc_layout.setContentsMargins(0, 0, 0, 0)
        sc_layout.setSpacing(6)
        sc_layout.addWidget(self._make_field_label("Durum"))
        self._status_combo = QComboBox(parent=status_col)
        self._status_combo.setMinimumHeight(38)
        for status in ProjectStatus:
            if status == ProjectStatus.ARCHIVED:
                continue
            label = _STATUS_LABELS.get(status.value, status.value)
            self._status_combo.addItem(label, status.value)
        sc_layout.addWidget(self._status_combo)
        layout.addWidget(status_col)

        priority_col = QWidget(parent=row)
        pc_layout = QVBoxLayout(priority_col)
        pc_layout.setContentsMargins(0, 0, 0, 0)
        pc_layout.setSpacing(6)
        pc_layout.addWidget(self._make_field_label("Öncelik"))
        self._priority_combo = QComboBox(parent=priority_col)
        self._priority_combo.setMinimumHeight(38)
        for priority in Priority:
            label = _PRIORITY_LABELS.get(priority.value, priority.value)
            self._priority_combo.addItem(label, priority.value)
        pc_layout.addWidget(self._priority_combo)
        layout.addWidget(priority_col)

        return row

    def _build_button_row(self) -> QWidget:
        row = QWidget(parent=self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()

        cancel_btn = QPushButton("İptal", parent=row)
        cancel_btn.setMinimumSize(90, 38)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        save_label = "Kaydet" if self._is_edit else "Oluştur"
        self._save_btn = QPushButton(save_label, parent=row)
        self._save_btn.setMinimumSize(90, 38)
        self._save_btn.setObjectName("accent_button")
        self._save_btn.clicked.connect(self._on_save)
        layout.addWidget(self._save_btn)

        return row

    def _populate_fields(self) -> None:
        p = self._project
        if p is None:
            return
        self._title_edit.setText(p.title)
        if p.short_description:
            self._desc_edit.setPlainText(p.short_description)
        for i in range(self._status_combo.count()):
            if self._status_combo.itemData(i) == p.status:
                self._status_combo.setCurrentIndex(i)
                break
        for i in range(self._priority_combo.count()):
            if self._priority_combo.itemData(i) == p.priority:
                self._priority_combo.setCurrentIndex(i)
                break
        if p.github_url:
            self._github_edit.setText(p.github_url)

    def _on_save(self) -> None:
        title = self._title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Geçersiz Giriş", "Proje başlığı boş olamaz.")
            self._title_edit.setFocus()
            return
        self.accept()

    def get_data(self) -> dict[str, object]:
        """Dialog kabul edildikten sonra çağrılır; dolu alanları sözlük olarak döndürür."""
        return {
            "title": self._title_edit.text().strip(),
            "short_description": self._desc_edit.toPlainText().strip() or None,
            "status": self._status_combo.currentData(),
            "priority": self._priority_combo.currentData(),
            "github_url": self._github_edit.text().strip() or None,
        }
