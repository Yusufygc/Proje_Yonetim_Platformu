from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from domain.enums.idea_priority import IdeaPriority
from domain.enums.idea_status import IdeaStatus
from domain.models.idea import Idea
from presentation.dialogs.form_utils import (
    make_combo_column,
    make_two_column_row,
    select_combo_data,
    set_field_error,
)
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr


def _idea_status_labels() -> dict[str, str]:
    """Durum etiketleri; dil değişimi dialog her açılışta yansısın diye fonksiyon."""
    return {
        IdeaStatus.RAW.value: tr("idea_status_raw", "Ham Fikir"),
        IdeaStatus.REVIEWING.value: tr("idea_status_reviewing", "İnceleniyor"),
        IdeaStatus.VALIDATING.value: tr("idea_status_validating", "Doğrulanıyor"),
        IdeaStatus.CONVERTED.value: tr("idea_status_converted", "Projeye Dönüştürüldü"),
        IdeaStatus.DEFERRED.value: tr("idea_status_deferred", "Ertelendi"),
        IdeaStatus.REJECTED.value: tr("idea_status_rejected", "Reddedildi"),
    }


def _idea_priority_labels() -> dict[str, str]:
    return {
        IdeaPriority.LOW.value: tr("priority_low", "Düşük"),
        IdeaPriority.MEDIUM.value: tr("priority_medium", "Orta"),
        IdeaPriority.HIGH.value: tr("priority_high", "Yüksek"),
        IdeaPriority.CRITICAL.value: tr("priority_critical", "Kritik"),
    }


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
        title = (
            tr("idea_dialog_edit_title", "Fikri Düzenle")
            if self._is_edit
            else tr("idea_dialog_new_title", "Yeni Fikir Ekle")
        )
        self.setWindowTitle(title)
        self.setMinimumWidth(Size.DIALOG_IDEA_MIN_W)

        # Ekran yüksekliğine göre maksimum yükseklik sınırı
        screen = QApplication.primaryScreen()
        if screen:
            screen_height = screen.availableGeometry().height()
            self.setMaximumHeight(int(screen_height * 0.85))

        # Ana layout: başlık + scroll + butonlar
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(Spacing.XXXL, Spacing.XXL, Spacing.XXXL, Spacing.XL)
        outer_layout.setSpacing(0)

        dialog_title = QLabel(title, parent=self)
        dialog_title.setProperty("cssClass", "title-small")
        outer_layout.addWidget(dialog_title)
        outer_layout.addSpacing(14)

        # Kaydırılabilir form alanı
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
        layout.setContentsMargins(0, 4, 12, 4)
        layout.setSpacing(14)

        # Başlık
        layout.addWidget(self._make_label(tr("idea_dialog_title_label", "Fikir Başlığı *")))
        self._error_label = QLabel(parent=form_widget)
        self._error_label.setProperty("cssClass", "text-danger")
        self._error_label.hide()
        layout.addWidget(self._error_label)
        self._title_edit = QLineEdit(parent=form_widget)
        self._title_edit.setPlaceholderText(tr("idea_dialog_title_placeholder", "Örn: Yeni mobil uygulama fikri..."))
        self._title_edit.setMinimumHeight(Size.INPUT_H_MD)
        layout.addWidget(self._title_edit)

        # Durum ve Öncelik yan yana
        status_labels = _idea_status_labels()
        status_col, self._status_combo = make_combo_column(
            form_widget,
            tr("label_status", "Durum"),
            [(status_labels.get(s.value, s.value), s.value) for s in IdeaStatus],
        )
        priority_labels = _idea_priority_labels()
        priority_col, self._priority_combo = make_combo_column(
            form_widget,
            tr("label_priority", "Öncelik"),
            [(priority_labels.get(p.value, p.value), p.value) for p in IdeaPriority],
        )
        layout.addWidget(make_two_column_row(form_widget, status_col, priority_col))

        # Hedef Kullanıcı
        layout.addWidget(self._make_label(tr("label_target_user", "Hedef Kullanıcı")))
        self._target_user_edit = QLineEdit(parent=form_widget)
        self._target_user_edit.setPlaceholderText(tr("idea_dialog_target_user_placeholder", "Kim için?"))
        self._target_user_edit.setMinimumHeight(Size.INPUT_H_MD)
        layout.addWidget(self._target_user_edit)

        layout.addWidget(self._make_label(tr("idea_dialog_problem_label", "Çözülen Problem")))
        self._problem_edit = QTextEdit(parent=form_widget)
        self._problem_edit.setPlaceholderText(tr("idea_dialog_problem_placeholder", "Bu fikir hangi problemi çözüyor?"))
        self._problem_edit.setMaximumHeight(Size.TEXTAREA_H_LG)
        layout.addWidget(self._problem_edit)

        # Çözüm
        layout.addWidget(self._make_label(tr("idea_dialog_solution_label", "Önerilen Çözüm")))
        self._solution_edit = QTextEdit(parent=form_widget)
        self._solution_edit.setPlaceholderText(tr("idea_dialog_solution_placeholder", "Önerdiğiniz çözüm detayları..."))
        self._solution_edit.setMaximumHeight(Size.TEXTAREA_H_LG)
        layout.addWidget(self._solution_edit)

        # Beklenen Değer
        layout.addWidget(self._make_label(tr("idea_dialog_expected_label", "Beklenen Değer / Çıktı")))
        self._expected_edit = QLineEdit(parent=form_widget)
        self._expected_edit.setPlaceholderText(tr("idea_dialog_expected_placeholder", "Örn: Aylık %10 ciro artışı"))
        self._expected_edit.setMinimumHeight(Size.INPUT_H_MD)
        layout.addWidget(self._expected_edit)

        # Skor satırı
        score_row = QWidget(parent=form_widget)
        score_row_layout = QHBoxLayout(score_row)
        score_row_layout.setContentsMargins(0, 0, 0, 0)
        score_row_layout.setSpacing(16)
        self._difficulty_spin = self._make_score_spin(tr("label_difficulty", "Zorluk"), score_row_layout, score_row)
        self._effort_spin = self._make_score_spin(tr("label_effort", "Efor"), score_row_layout, score_row)
        self._confidence_spin = self._make_score_spin(tr("label_confidence", "Güven"), score_row_layout, score_row)
        layout.addWidget(score_row)

        layout.addWidget(self._make_label(tr("label_notes", "Notlar")))
        self._notes_edit = QTextEdit(parent=form_widget)
        self._notes_edit.setMaximumHeight(Size.TEXTAREA_H_SM)
        layout.addWidget(self._notes_edit)

        layout.addWidget(self._make_label(tr("label_source_url", "Kaynak URL")))
        self._source_edit = QLineEdit(parent=form_widget)
        self._source_edit.setPlaceholderText("https://github.com/ornek")
        self._source_edit.setMinimumHeight(Size.INPUT_H_MD)
        layout.addWidget(self._source_edit)

        layout.addStretch()

        scroll.setWidget(form_widget)
        outer_layout.addWidget(scroll, 1)
        outer_layout.addSpacing(10)

        # Ayraç
        sep = QFrame(parent=self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setProperty("cssClass", "divider")
        outer_layout.addWidget(sep)
        outer_layout.addSpacing(10)

        # Butonlar — her zaman görünür
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = QPushButton(tr("action_cancel", "İptal"), parent=self)
        cancel_btn.setMinimumSize(Size.BTN_LG_W, Size.INPUT_H_MD)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton(tr("action_save", "Kaydet"), parent=self)
        save_btn.setObjectName("accent_button")
        save_btn.setMinimumSize(Size.BTN_LG_W, Size.INPUT_H_MD)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        outer_layout.addLayout(btn_layout)

    def _make_label(self, text: str) -> QLabel:
        lbl = QLabel(text, parent=self)
        lbl.setProperty("cssClass", "field-label")
        return lbl

    def _make_score_spin(self, label: str, row: QHBoxLayout, parent: QWidget | None = None) -> QSpinBox:
        col = QVBoxLayout()
        col.addWidget(self._make_label(label))
        spin = QSpinBox(parent=parent or self)
        spin.setRange(0, 10)
        spin.setSpecialValueText("-")
        spin.setMinimumHeight(Size.INPUT_H_MD)
        col.addWidget(spin)
        row.addLayout(col)
        return spin

    def _populate_fields(self) -> None:
        if not self._idea:
            return
        self._title_edit.setText(self._idea.title)
        if self._idea.problem:
            self._problem_edit.setText(self._idea.problem)
        if self._idea.target_user:
            self._target_user_edit.setText(self._idea.target_user)
        if self._idea.solution:
            self._solution_edit.setText(self._idea.solution)
        if self._idea.expected_value:
            self._expected_edit.setText(self._idea.expected_value)
        if self._idea.source_link:
            self._source_edit.setText(self._idea.source_link)
        if self._idea.notes:
            self._notes_edit.setText(self._idea.notes)
        self._difficulty_spin.setValue(self._idea.difficulty or 0)
        self._effort_spin.setValue(self._idea.effort or 0)
        self._confidence_spin.setValue(self._idea.confidence or 0)

        select_combo_data(self._status_combo, self._idea.status)
        select_combo_data(self._priority_combo, self._idea.priority)

    def _on_save(self) -> None:
        title = self._title_edit.text().strip()
        if not title:
            self._error_label.setText(tr("idea_dialog_title_required", "Fikir başlığı boş olamaz."))
            self._error_label.show()
            set_field_error(self._title_edit, True)
            self._title_edit.setFocus()
            return

        self._error_label.hide()
        set_field_error(self._title_edit, False)
        self.accept()

    def get_data(self) -> dict:
        return {
            "title": self._title_edit.text(),
            "problem": self._problem_edit.toPlainText(),
            "solution": self._solution_edit.toPlainText(),
            "target_user": self._target_user_edit.text(),
            "expected_value": self._expected_edit.text(),
            "source_link": self._source_edit.text(),
            "difficulty": self._difficulty_spin.value() or None,
            "effort": self._effort_spin.value() or None,
            "confidence": self._confidence_spin.value() or None,
            "notes": self._notes_edit.toPlainText(),
            "status": self._status_combo.currentData(),
            "priority": self._priority_combo.currentData(),
        }
