"""
Proje oluşturma ve düzenleme için modal dialog.
Yeni proje için boş, var olan proje için alanlar dolu gelir.
"""
from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDateEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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
from presentation.dialogs.form_utils import (
    add_field,
    make_combo_column,
    make_field_label,
    make_two_column_row,
    select_combo_data,
    set_field_error,
)
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr


def _status_labels() -> dict[str, str]:
    """Durum etiketleri; dil değişimi dialog her açılışta yansısın diye fonksiyon."""
    return {
        ProjectStatus.PLANNED.value: tr("status_planned", "Planlandı"),
        ProjectStatus.ACTIVE.value: tr("status_active", "Aktif"),
        ProjectStatus.ON_HOLD.value: tr("status_on_hold", "Beklemede"),
        ProjectStatus.BLOCKED.value: tr("status_blocked", "Engellendi"),
        ProjectStatus.COMPLETED.value: tr("status_completed", "Tamamlandı"),
        ProjectStatus.CANCELLED.value: tr("status_cancelled", "İptal Edildi"),
    }


def _priority_labels() -> dict[str, str]:
    return {
        Priority.LOW.value: tr("priority_low", "Düşük"),
        Priority.MEDIUM.value: tr("priority_medium", "Orta"),
        Priority.HIGH.value: tr("priority_high", "Yüksek"),
        Priority.CRITICAL.value: tr("priority_critical", "Kritik"),
    }


def _health_labels() -> dict[str, str]:
    return {
        ProjectHealth.GOOD.value: tr("health_good", "Yolunda"),
        ProjectHealth.AT_RISK.value: tr("health_at_risk", "Riskli"),
        ProjectHealth.BLOCKED.value: tr("health_blocked", "Tıkandı"),
        ProjectHealth.UNKNOWN.value: tr("health_unknown", "Belirsiz"),
    }


def _project_type_items() -> list[tuple[str, str]]:
    """(görünen etiket, saklanan değer) çiftleri.

    Saklanan değer DB'de geçmiş kayıtlarla uyum için sabit tutulur;
    yalnızca görünen etiket çevrilir.
    """
    return [
        (tr("project_type_software", "Yazılım"), "Yazılım"),  # l10n: data
        (tr("project_type_education", "Eğitim"), "Eğitim"),  # l10n: data
        (tr("project_type_research", "Araştırma"), "Araştırma"),  # l10n: data
        (tr("project_type_design", "Tasarım"), "Tasarım"),  # l10n: data
        (tr("project_type_internal", "İç araç"), "İç araç"),  # l10n: data
        (tr("project_type_client", "Müşteri işi"), "Müşteri işi"),  # l10n: data
        (tr("project_type_experimental", "Deneysel"), "Deneysel"),  # l10n: data
        (tr("project_type_other", "Diğer"), "Diğer"),  # l10n: data
    ]


class ProjectDialog(QDialog):
    """Proje oluşturma (project=None) veya düzenleme modal dialog'u."""

    def __init__(self, parent: QWidget, project: Project | None = None) -> None:
        super().__init__(parent=parent)
        self._project = project
        self._is_edit = project is not None
        self._setup_ui()
        if self._is_edit:
            self._populate_fields()

    # ── UI kurulumu ──────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        title_text = (
            tr("project_dialog_edit_title", "Projeyi Düzenle")
            if self._is_edit
            else tr("project_dialog_new_title", "Yeni Proje Oluştur")
        )
        self.setWindowTitle(title_text)
        self.setMinimumWidth(Size.DIALOG_PROJECT_MIN_W)
        self.setModal(True)

        # Ekran yüksekliğine göre maksimum yükseklik sınırı
        screen = QApplication.primaryScreen()
        if screen:
            screen_height = screen.availableGeometry().height()
            self.setMaximumHeight(int(screen_height * 0.85))

        # Ana layout: başlık + scroll + butonlar
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(Spacing.XXXL, Spacing.XXL, Spacing.XXXL, Spacing.XXL)
        outer_layout.setSpacing(0)

        dialog_title = QLabel(title_text, parent=self)
        dialog_title.setProperty("cssClass", "title-small")
        outer_layout.addWidget(dialog_title)
        outer_layout.addSpacing(Spacing.XL)

        outer_layout.addWidget(self._build_scroll_form(), 1)
        outer_layout.addSpacing(Spacing.LG)

        # Ayraç çizgisi
        sep = QFrame(parent=self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setProperty("cssClass", "divider")
        outer_layout.addWidget(sep)
        outer_layout.addSpacing(Spacing.LG)

        # Butonlar scroll dışında, her zaman görünür
        outer_layout.addWidget(self._build_button_row())

    def _build_scroll_form(self) -> QScrollArea:
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
        layout.setContentsMargins(0, Spacing.XS, Spacing.XXXL, Spacing.XS)
        layout.setSpacing(0)

        self._build_form_fields(form_widget, layout)

        scroll.setWidget(form_widget)
        return scroll

    def _build_form_fields(self, form_widget: QWidget, layout: QVBoxLayout) -> None:
        # Başlık alanı: validasyon hata etiketi araya girdiği için add_field kullanılmaz
        layout.addWidget(make_field_label(tr("project_dialog_title_label", "Proje Başlığı *"), form_widget))
        self._error_label = QLabel(parent=form_widget)
        self._error_label.setProperty("cssClass", "text-danger")
        self._error_label.hide()
        layout.addWidget(self._error_label)
        layout.addSpacing(Spacing.SM)
        self._title_edit = QLineEdit(parent=form_widget)
        self._title_edit.setPlaceholderText(tr("project_dialog_title_placeholder", "Projenin adını girin..."))
        self._title_edit.setMinimumHeight(Size.INPUT_H_LG)
        layout.addWidget(self._title_edit)
        layout.addSpacing(Spacing.XL)

        self._desc_edit = self._make_text_area(form_widget, Size.TEXTAREA_H_LG)
        self._desc_edit.setPlaceholderText(
            tr("project_dialog_short_desc_placeholder", "Projeyi kısaca açıklayın (isteğe bağlı)...")
        )
        add_field(layout, tr("project_dialog_short_desc", "Kısa Açıklama"), self._desc_edit)

        layout.addWidget(self._build_status_priority_row(form_widget))
        layout.addSpacing(Spacing.XL)

        self._full_desc_edit = self._make_text_area(form_widget, Size.TEXTAREA_H_MD)
        add_field(layout, tr("project_dialog_full_desc", "Detaylı Açıklama"), self._full_desc_edit)

        self._problem_edit = self._make_text_area(form_widget, Size.TEXTAREA_H_MD)
        add_field(layout, tr("project_dialog_problem", "Problem Tanımı"), self._problem_edit)

        self._target_edit = self._make_text_area(form_widget, Size.TEXTAREA_H_MD)
        add_field(layout, tr("project_dialog_target", "Hedef Çıktı"), self._target_edit)

        layout.addWidget(self._build_type_health_row(form_widget))
        layout.addSpacing(Spacing.XL)

        self._demo_edit = self._make_line_edit(form_widget)
        add_field(layout, tr("label_demo_url", "Demo URL"), self._demo_edit)

        self._docs_edit = self._make_line_edit(form_widget)
        add_field(layout, tr("label_docs_url", "Doküman URL"), self._docs_edit)

        layout.addWidget(self._build_target_date_row(form_widget))
        layout.addSpacing(Spacing.XL)

        self._tags_edit = self._make_line_edit(form_widget)
        self._tags_edit.setPlaceholderText(
            tr("project_dialog_tags_placeholder", "virgülle ayırın: mvp, ui, araştırma")
        )
        add_field(layout, tr("label_tags", "Etiketler"), self._tags_edit)

        self._featured_check = QCheckBox(tr("project_dialog_featured", "Portfolyoya eklensin"), parent=form_widget)
        layout.addWidget(self._featured_check)
        layout.addSpacing(Spacing.XL)

        self._github_edit = self._make_line_edit(form_widget)
        self._github_edit.setPlaceholderText("https://github.com/kullanici/repo")
        add_field(layout, tr("label_github_url", "GitHub URL"), self._github_edit, gap_after=Spacing.MD)

    @staticmethod
    def _make_line_edit(parent: QWidget) -> QLineEdit:
        edit = QLineEdit(parent=parent)
        edit.setMinimumHeight(Size.INPUT_H_LG)
        return edit

    @staticmethod
    def _make_text_area(parent: QWidget, max_height: int) -> QTextEdit:
        edit = QTextEdit(parent=parent)
        edit.setMaximumHeight(max_height)
        return edit

    def _build_status_priority_row(self, parent: QWidget) -> QWidget:
        status_labels = _status_labels()
        status_items = [
            (status_labels.get(s.value, s.value), s.value)
            for s in ProjectStatus
            if s != ProjectStatus.ARCHIVED
        ]
        status_col, self._status_combo = make_combo_column(
            parent, tr("label_status", "Durum"), status_items
        )
        priority_labels = _priority_labels()
        priority_items = [(priority_labels.get(p.value, p.value), p.value) for p in Priority]
        priority_col, self._priority_combo = make_combo_column(
            parent, tr("label_priority", "Öncelik"), priority_items
        )
        return make_two_column_row(parent, status_col, priority_col)

    def _build_type_health_row(self, parent: QWidget) -> QWidget:
        type_col, self._type_combo = make_combo_column(
            parent, tr("label_project_type", "Proje Türü"), _project_type_items()
        )
        health_labels = _health_labels()
        health_col, self._health_combo = make_combo_column(
            parent,
            tr("label_health", "Sağlık"),
            [(health_labels.get(h.value, h.value), h.value) for h in ProjectHealth],
        )
        return make_two_column_row(parent, type_col, health_col)

    def _build_target_date_row(self, parent: QWidget) -> QWidget:
        row = QWidget(parent=parent)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        self._target_date_enabled = QCheckBox(tr("label_target_date", "Hedef tarih"), parent=row)
        layout.addWidget(self._target_date_enabled)
        self._target_date_edit = QDateEdit(parent=row)
        self._target_date_edit.setCalendarPopup(True)
        self._target_date_edit.setMinimumHeight(Size.INPUT_H_LG)
        self._target_date_edit.setEnabled(False)
        self._target_date_enabled.toggled.connect(self._target_date_edit.setEnabled)
        layout.addWidget(self._target_date_edit, 1)
        return row

    def _build_button_row(self) -> QWidget:
        row = QWidget(parent=self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MD + 2)
        layout.addStretch()

        cancel_btn = QPushButton(tr("action_cancel", "İptal"), parent=row)
        cancel_btn.setMinimumSize(Size.BTN_LG_W, Size.BTN_LG_H)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        save_label = tr("action_save", "Kaydet") if self._is_edit else tr("action_create", "Oluştur")
        self._save_btn = QPushButton(save_label, parent=row)
        self._save_btn.setMinimumSize(Size.BTN_LG_W, Size.BTN_LG_H)
        self._save_btn.setObjectName("accent_button")
        self._save_btn.clicked.connect(self._on_save)
        layout.addWidget(self._save_btn)

        return row

    # ── Veri doldurma ────────────────────────────────────────────────────────

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
        select_combo_data(self._status_combo, p.status)
        select_combo_data(self._priority_combo, p.priority)
        select_combo_data(self._health_combo, p.health)
        if p.github_url:
            self._github_edit.setText(p.github_url)
        if p.demo_url:
            self._demo_edit.setText(p.demo_url)
        if p.docs_url:
            self._docs_edit.setText(p.docs_url)
        if p.project_type:
            select_combo_data(self._type_combo, p.project_type)
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

    # ── Doğrulama ve sonuç ───────────────────────────────────────────────────

    def _on_save(self) -> None:
        title = self._title_edit.text().strip()
        if not title:
            self._error_label.setText(tr("project_dialog_title_required", "Proje başlığı boş olamaz."))
            self._error_label.show()
            set_field_error(self._title_edit, True)
            self._title_edit.setFocus()
            return

        self._error_label.hide()
        set_field_error(self._title_edit, False)
        self.accept()

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
