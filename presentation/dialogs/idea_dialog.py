from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
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

_IDEA_STATUS_LABELS: dict[str, str] = {
    IdeaStatus.RAW.value: "Ham Fikir",
    IdeaStatus.REVIEWING.value: "İnceleniyor",
    IdeaStatus.VALIDATING.value: "Doğrulanıyor",
    IdeaStatus.CONVERTED.value: "Projeye Dönüştürüldü",
    IdeaStatus.DEFERRED.value: "Ertelendi",
    IdeaStatus.REJECTED.value: "Reddedildi",
}

_IDEA_PRIORITY_LABELS: dict[str, str] = {
    IdeaPriority.LOW.value: "Düşük",
    IdeaPriority.MEDIUM.value: "Orta",
    IdeaPriority.HIGH.value: "Yüksek",
    IdeaPriority.CRITICAL.value: "Kritik",
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
        title = "Fikri Düzenle" if self._is_edit else "Yeni Fikir Ekle"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)

        # Ekran yüksekliğine göre maksimum yükseklik sınırı
        screen = QApplication.primaryScreen()
        if screen:
            screen_height = screen.availableGeometry().height()
            self.setMaximumHeight(int(screen_height * 0.85))

        # Ana layout: başlık + scroll + butonlar
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 20, 24, 16)
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
        layout.addWidget(self._make_label("Fikir Başlığı *"))
        self._error_label = QLabel(parent=form_widget)
        self._error_label.setProperty("cssClass", "text-danger")
        self._error_label.hide()
        layout.addWidget(self._error_label)
        self._title_edit = QLineEdit(parent=form_widget)
        self._title_edit.setPlaceholderText("Örn: Yeni mobil uygulama fikri...")
        self._title_edit.setMinimumHeight(36)
        layout.addWidget(self._title_edit)

        # Durum ve Öncelik Yan Yana
        combo_row = QWidget(parent=form_widget)
        combo_row_layout = QHBoxLayout(combo_row)
        combo_row_layout.setContentsMargins(0, 0, 0, 0)
        combo_row_layout.setSpacing(16)

        status_col = QWidget(parent=combo_row)
        sc_layout = QVBoxLayout(status_col)
        sc_layout.setContentsMargins(0, 0, 0, 0)
        sc_layout.setSpacing(6)
        sc_layout.addWidget(self._make_label("Durum"))
        self._status_combo = QComboBox(parent=status_col)
        self._status_combo.setMinimumHeight(36)
        for s in IdeaStatus:
            self._status_combo.addItem(_IDEA_STATUS_LABELS.get(s.value, s.value), s.value)
        sc_layout.addWidget(self._status_combo)
        combo_row_layout.addWidget(status_col)

        priority_col = QWidget(parent=combo_row)
        pc_layout = QVBoxLayout(priority_col)
        pc_layout.setContentsMargins(0, 0, 0, 0)
        pc_layout.setSpacing(6)
        pc_layout.addWidget(self._make_label("Öncelik"))
        self._priority_combo = QComboBox(parent=priority_col)
        self._priority_combo.setMinimumHeight(36)
        for p in IdeaPriority:
            self._priority_combo.addItem(_IDEA_PRIORITY_LABELS.get(p.value, p.value), p.value)
        pc_layout.addWidget(self._priority_combo)
        combo_row_layout.addWidget(priority_col)

        layout.addWidget(combo_row)

        # Hedef Kullanıcı
        layout.addWidget(self._make_label("Hedef Kullanıcı"))
        self._target_user_edit = QLineEdit(parent=form_widget)
        self._target_user_edit.setPlaceholderText("Kim için?")
        self._target_user_edit.setMinimumHeight(36)
        layout.addWidget(self._target_user_edit)

        layout.addWidget(self._make_label("Çözülen Problem"))
        self._problem_edit = QTextEdit(parent=form_widget)
        self._problem_edit.setPlaceholderText("Bu fikir hangi problemi çözüyor?")
        self._problem_edit.setMaximumHeight(80)
        layout.addWidget(self._problem_edit)

        # Çözüm
        layout.addWidget(self._make_label("Önerilen Çözüm"))
        self._solution_edit = QTextEdit(parent=form_widget)
        self._solution_edit.setPlaceholderText("Önerdiğiniz çözüm detayları...")
        self._solution_edit.setMaximumHeight(80)
        layout.addWidget(self._solution_edit)

        # Beklenen Değer
        layout.addWidget(self._make_label("Beklenen Değer / Çıktı"))
        self._expected_edit = QLineEdit(parent=form_widget)
        self._expected_edit.setPlaceholderText("Örn: Aylık %10 ciro artışı")
        self._expected_edit.setMinimumHeight(36)
        layout.addWidget(self._expected_edit)

        # Skor satırı
        score_row = QWidget(parent=form_widget)
        score_row_layout = QHBoxLayout(score_row)
        score_row_layout.setContentsMargins(0, 0, 0, 0)
        score_row_layout.setSpacing(16)
        self._difficulty_spin = self._make_score_spin("Zorluk", score_row_layout, score_row)
        self._effort_spin = self._make_score_spin("Efor", score_row_layout, score_row)
        self._confidence_spin = self._make_score_spin("Güven", score_row_layout, score_row)
        layout.addWidget(score_row)

        layout.addWidget(self._make_label("Notlar"))
        self._notes_edit = QTextEdit(parent=form_widget)
        self._notes_edit.setMaximumHeight(70)
        layout.addWidget(self._notes_edit)

        layout.addWidget(self._make_label("Kaynak URL"))
        self._source_edit = QLineEdit(parent=form_widget)
        self._source_edit.setPlaceholderText("Örn: https://github.com/ornek")
        self._source_edit.setMinimumHeight(36)
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

        cancel_btn = QPushButton("İptal", parent=self)
        cancel_btn.setMinimumSize(90, 36)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Kaydet", parent=self)
        save_btn.setObjectName("accent_button")
        save_btn.setMinimumSize(90, 36)
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
        spin.setMinimumHeight(36)
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
        
        for i in range(self._status_combo.count()):
            if self._status_combo.itemData(i) == self._idea.status:
                self._status_combo.setCurrentIndex(i)
                break
        for i in range(self._priority_combo.count()):
            if self._priority_combo.itemData(i) == self._idea.priority:
                self._priority_combo.setCurrentIndex(i)
                break

    def _on_save(self) -> None:
        title = self._title_edit.text().strip()
        if not title:
            self._error_label.setText("Fikir başlığı boş olamaz.")
            self._error_label.show()
            self._set_field_error(self._title_edit, True)
            self._title_edit.setFocus()
            return

        self._error_label.hide()
        self._set_field_error(self._title_edit, False)
        self.accept()

    def _set_field_error(self, widget: QWidget, error: bool) -> None:
        widget.setProperty("error", "true" if error else "false")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

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
