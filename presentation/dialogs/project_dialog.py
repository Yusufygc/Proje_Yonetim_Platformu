"""
Proje oluşturma ve düzenleme için modal dialog.
Yeni proje için boş, var olan proje için alanlar dolu gelir.
"""
from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from domain.enums.priority import Priority
from domain.enums.project_health import ProjectHealth
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

_HEALTH_LABELS: dict[str, str] = {
    ProjectHealth.GOOD.value: "Yolunda",
    ProjectHealth.AT_RISK.value: "Riskli",
    ProjectHealth.BLOCKED.value: "Tıkandı",
    ProjectHealth.UNKNOWN.value: "Belirsiz",
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
        self.setMinimumWidth(620)
        self.setModal(True)

        # Ekran yüksekliğine göre maksimum yükseklik sınırı
        screen = QApplication.primaryScreen()
        if screen:
            screen_height = screen.availableGeometry().height()
            self.setMaximumHeight(int(screen_height * 0.85))

        # Ana layout: başlık + scroll + butonlar
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(28, 24, 28, 20)
        outer_layout.setSpacing(0)

        dialog_title = QLabel(title_text, parent=self)
        dialog_title.setProperty("cssClass", "title-small")
        outer_layout.addWidget(dialog_title)
        outer_layout.addSpacing(16)

        # Kaydırılabilir form alanları
        scroll = QScrollArea(parent=self)
        scroll.setObjectName("dialog_scroll")
        scroll.viewport().setAutoFillBackground(False)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        form_widget = QWidget(parent=scroll)
        form_widget.setObjectName("form_container")
        form_widget.setAutoFillBackground(False)
        layout = QVBoxLayout(form_widget)
        layout.setContentsMargins(0, 4, 24, 4)
        layout.setSpacing(0)

        layout.addWidget(self._make_field_label("Proje Başlığı *"))
        self._error_label = QLabel(parent=form_widget)
        self._error_label.setProperty("cssClass", "text-danger")
        self._error_label.hide()
        layout.addWidget(self._error_label)
        layout.addSpacing(6)
        self._title_edit = QLineEdit(parent=form_widget)
        self._title_edit.setPlaceholderText("Projenin adını girin...")
        self._title_edit.setMinimumHeight(38)
        layout.addWidget(self._title_edit)
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("Kısa Açıklama"))
        layout.addSpacing(6)
        self._desc_edit = QTextEdit(parent=form_widget)
        self._desc_edit.setPlaceholderText("Projeyi kısaca açıklayın (isteğe bağlı)...")
        self._desc_edit.setMaximumHeight(80)
        layout.addWidget(self._desc_edit)
        layout.addSpacing(16)

        layout.addWidget(self._build_status_priority_row(form_widget))
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("Detaylı Açıklama"))
        layout.addSpacing(6)
        self._full_desc_edit = QTextEdit(parent=form_widget)
        self._full_desc_edit.setMaximumHeight(72)
        layout.addWidget(self._full_desc_edit)
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("Problem Tanımı"))
        layout.addSpacing(6)
        self._problem_edit = QTextEdit(parent=form_widget)
        self._problem_edit.setMaximumHeight(72)
        layout.addWidget(self._problem_edit)
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("Hedef Çıktı"))
        layout.addSpacing(6)
        self._target_edit = QTextEdit(parent=form_widget)
        self._target_edit.setMaximumHeight(72)
        layout.addWidget(self._target_edit)
        layout.addSpacing(16)

        layout.addWidget(self._build_type_health_row(form_widget))
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("Demo URL"))
        layout.addSpacing(6)
        self._demo_edit = QLineEdit(parent=form_widget)
        self._demo_edit.setMinimumHeight(38)
        layout.addWidget(self._demo_edit)
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("Doküman URL"))
        layout.addSpacing(6)
        self._docs_edit = QLineEdit(parent=form_widget)
        self._docs_edit.setMinimumHeight(38)
        layout.addWidget(self._docs_edit)
        layout.addSpacing(16)

        layout.addWidget(self._build_target_date_row(form_widget))
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("Etiketler"))
        layout.addSpacing(6)
        self._tags_edit = QLineEdit(parent=form_widget)
        self._tags_edit.setPlaceholderText("virgülle ayırın: mvp, ui, araştırma")
        self._tags_edit.setMinimumHeight(38)
        layout.addWidget(self._tags_edit)
        layout.addSpacing(16)

        self._featured_check = QCheckBox("Portfolyoya eklensin", parent=form_widget)
        layout.addWidget(self._featured_check)
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("GitHub URL"))
        layout.addSpacing(6)
        self._github_edit = QLineEdit(parent=form_widget)
        self._github_edit.setPlaceholderText("https://github.com/kullanici/repo")
        self._github_edit.setMinimumHeight(38)
        layout.addWidget(self._github_edit)
        layout.addSpacing(8)

        scroll.setWidget(form_widget)
        outer_layout.addWidget(scroll, 1)
        outer_layout.addSpacing(12)

        # Ayraç çizgisi
        sep = QFrame(parent=self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setProperty("cssClass", "divider")
        outer_layout.addWidget(sep)
        outer_layout.addSpacing(12)

        # Butonlar scroll dışında, her zaman görünür
        outer_layout.addWidget(self._build_button_row())

    def _make_field_label(self, text: str) -> QLabel:
        lbl = QLabel(text, parent=self)
        lbl.setProperty("cssClass", "field-label")
        return lbl

    def _build_status_priority_row(self, parent: QWidget | None = None) -> QWidget:
        row = QWidget(parent=parent or self)
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

    def _build_type_health_row(self, parent: QWidget | None = None) -> QWidget:
        row = QWidget(parent=parent or self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        type_col = QWidget(parent=row)
        tc_layout = QVBoxLayout(type_col)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.setSpacing(6)
        tc_layout.addWidget(self._make_field_label("Proje Türü"))
        self._type_combo = QComboBox(parent=type_col)
        self._type_combo.setMinimumHeight(38)
        for label in ["Yazılım", "Eğitim", "Araştırma", "Tasarım", "İç araç", "Müşteri işi", "Deneysel", "Diğer"]:
            self._type_combo.addItem(label, label)
        tc_layout.addWidget(self._type_combo)
        layout.addWidget(type_col)

        health_col = QWidget(parent=row)
        hc_layout = QVBoxLayout(health_col)
        hc_layout.setContentsMargins(0, 0, 0, 0)
        hc_layout.setSpacing(6)
        hc_layout.addWidget(self._make_field_label("Sağlık"))
        self._health_combo = QComboBox(parent=health_col)
        self._health_combo.setMinimumHeight(38)
        for health in ProjectHealth:
            self._health_combo.addItem(_HEALTH_LABELS.get(health.value, health.value), health.value)
        hc_layout.addWidget(self._health_combo)
        layout.addWidget(health_col)

        return row

    def _build_target_date_row(self, parent: QWidget | None = None) -> QWidget:
        row = QWidget(parent=parent or self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        self._target_date_enabled = QCheckBox("Hedef tarih", parent=row)
        layout.addWidget(self._target_date_enabled)
        self._target_date_edit = QDateEdit(parent=row)
        self._target_date_edit.setCalendarPopup(True)
        self._target_date_edit.setMinimumHeight(38)
        self._target_date_edit.setEnabled(False)
        self._target_date_enabled.toggled.connect(self._target_date_edit.setEnabled)
        layout.addWidget(self._target_date_edit, 1)
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
        if p.full_description:
            self._full_desc_edit.setPlainText(p.full_description)
        if p.problem_statement:
            self._problem_edit.setPlainText(p.problem_statement)
        if p.target_outcome:
            self._target_edit.setPlainText(p.target_outcome)
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
        if p.demo_url:
            self._demo_edit.setText(p.demo_url)
        if p.docs_url:
            self._docs_edit.setText(p.docs_url)
        if p.project_type:
            self._type_combo.setCurrentText(p.project_type)
        for i in range(self._health_combo.count()):
            if self._health_combo.itemData(i) == p.health:
                self._health_combo.setCurrentIndex(i)
                break
        if p.target_end_date:
            self._target_date_enabled.setChecked(True)
            self._target_date_edit.setDate(
                QDate(p.target_end_date.year, p.target_end_date.month, p.target_end_date.day)
            )
        self._featured_check.setChecked(p.is_featured)

    def set_prefill(self, data: dict) -> None:
        """Fikirden projeye dönüş gibi akışlarda formu önceden doldurur."""
        if title := data.get("title"):
            self._title_edit.setText(str(title))
        if short_desc := data.get("short_description"):
            self._desc_edit.setPlainText(str(short_desc))
        if full_desc := data.get("full_description"):
            self._full_desc_edit.setPlainText(str(full_desc))
        if problem := data.get("problem_statement"):
            self._problem_edit.setPlainText(str(problem))
        if target := data.get("target_outcome"):
            self._target_edit.setPlainText(str(target))
        if docs_url := data.get("docs_url"):
            self._docs_edit.setText(str(docs_url))

    def _on_save(self) -> None:
        title = self._title_edit.text().strip()
        if not title:
            self._error_label.setText("Proje başlığı boş olamaz.")
            self._error_label.show()
            self._set_field_error(self._title_edit, True)
            self._title_edit.setFocus()
            return

        self._error_label.hide()
        self._set_field_error(self._title_edit, False)
        self.accept()

    def _set_field_error(self, widget: QWidget, error: bool) -> None:
        """QSS error[=true/false] property'sini ayarlar ve stili yeniler."""
        widget.setProperty("error", "true" if error else "false")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def get_data(self) -> dict[str, object]:
        """Dialog kabul edildikten sonra çağrılır; dolu alanları sözlük olarak döndürür."""
        return {
            "title": self._title_edit.text().strip(),
            "short_description": self._desc_edit.toPlainText().strip() or None,
            "full_description": self._full_desc_edit.toPlainText().strip() or None,
            "problem_statement": self._problem_edit.toPlainText().strip() or None,
            "target_outcome": self._target_edit.toPlainText().strip() or None,
            "project_type": self._type_combo.currentData(),
            "status": self._status_combo.currentData(),
            "priority": self._priority_combo.currentData(),
            "health": self._health_combo.currentData(),
            "github_url": self._github_edit.text().strip() or None,
            "demo_url": self._demo_edit.text().strip() or None,
            "docs_url": self._docs_edit.text().strip() or None,
            "target_end_date": self._target_date_edit.date().toPython() if self._target_date_enabled.isChecked() else None,
            "is_featured": self._featured_check.isChecked(),
            "tags": [tag.strip() for tag in self._tags_edit.text().split(",") if tag.strip()],
        }
