"""
Görev oluşturma ve düzenleme için modal dialog.
Yeni görev için boş, var olan görev için alanlar dolu gelir.
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
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Qt

from domain.enums.priority import Priority
from domain.enums.task_status import TaskStatus
from domain.enums.task_type import TaskType
from domain.models.task import Task
from domain.models.project_stage import ProjectStage
from controllers.task_controller import TaskController

_STATUS_LABELS: dict[str, str] = {
    TaskStatus.TODO.value: "Yapılacak",
    TaskStatus.IN_PROGRESS.value: "Devam Ediyor",
    TaskStatus.WAITING.value: "Bekliyor",
    TaskStatus.BLOCKED.value: "Engellendi",
    TaskStatus.DONE.value: "Tamamlandı",
    TaskStatus.CANCELLED.value: "İptal Edildi",
}

_PRIORITY_LABELS: dict[str, str] = {
    Priority.LOW.value: "Düşük",
    Priority.MEDIUM.value: "Orta",
    Priority.HIGH.value: "Yüksek",
    Priority.CRITICAL.value: "Kritik",
}

_TYPE_LABELS: dict[str, str] = {
    TaskType.TASK.value: "Görev",
    TaskType.GROUP.value: "Grup",
    TaskType.BUG.value: "Hata",
    TaskType.IMPROVEMENT.value: "İyileştirme",
    TaskType.RESEARCH.value: "Araştırma",
    TaskType.DOCUMENTATION.value: "Dokümantasyon",
    TaskType.DESIGN.value: "Tasarım",
    TaskType.TEST.value: "Test",
    TaskType.REVIEW.value: "İnceleme",
}


class TaskDialog(QDialog):
    """Görev oluşturma (task=None) veya düzenleme modal dialog'u."""

    def __init__(
        self,
        parent: QWidget,
        task: Task | None = None,
        stages: list[ProjectStage] | None = None,
        task_controller: TaskController | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._task = task
        self._is_edit = task is not None
        self._stages = stages or []
        self._task_controller = task_controller
        self._setup_ui()
        if self._is_edit:
            self._populate_fields()
            
        if self._task_controller:
            self._task_controller.task_updated.connect(self._on_task_updated_event)

    def _setup_ui(self) -> None:
        title_text = "Görevi Düzenle" if self._is_edit else "Yeni Görev Ekle"
        self.setWindowTitle(title_text)
        self.setMinimumWidth(480)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(0)

        dialog_title = QLabel(title_text, parent=self)
        dialog_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #E8EAF0;")
        layout.addWidget(dialog_title)
        layout.addSpacing(20)

        layout.addWidget(self._make_field_label("Görev Başlığı *"))
        layout.addSpacing(6)
        self._title_edit = QLineEdit(parent=self)
        self._title_edit.setPlaceholderText("Görevin adını girin...")
        self._title_edit.setMinimumHeight(38)
        layout.addWidget(self._title_edit)
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label("Açıklama"))
        layout.addSpacing(6)
        self._desc_edit = QTextEdit(parent=self)
        self._desc_edit.setPlaceholderText("Görevi açıklayın (isteğe bağlı)...")
        self._desc_edit.setMaximumHeight(72)
        layout.addWidget(self._desc_edit)
        layout.addSpacing(16)

        layout.addWidget(self._build_combos_row())
        layout.addSpacing(28)

        if self._is_edit:
            self._build_checklist_section(layout)
            layout.addSpacing(28)

        layout.addWidget(self._build_button_row())

    def _make_field_label(self, text: str) -> QLabel:
        lbl = QLabel(text, parent=self)
        lbl.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #8B8FA8; letter-spacing: 0.5px;"
        )
        return lbl

    def _build_combos_row(self) -> QWidget:
        row = QWidget(parent=self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Durum
        status_col = QWidget(parent=row)
        sc = QVBoxLayout(status_col)
        sc.setContentsMargins(0, 0, 0, 0)
        sc.setSpacing(6)
        sc.addWidget(self._make_field_label("Durum"))
        self._status_combo = QComboBox(parent=status_col)
        self._status_combo.setMinimumHeight(36)
        for s in TaskStatus:
            self._status_combo.addItem(_STATUS_LABELS.get(s.value, s.value), s.value)
        sc.addWidget(self._status_combo)
        layout.addWidget(status_col)

        # Öncelik
        priority_col = QWidget(parent=row)
        pc = QVBoxLayout(priority_col)
        pc.setContentsMargins(0, 0, 0, 0)
        pc.setSpacing(6)
        pc.addWidget(self._make_field_label("Öncelik"))
        self._priority_combo = QComboBox(parent=priority_col)
        self._priority_combo.setMinimumHeight(36)
        for p in Priority:
            self._priority_combo.addItem(_PRIORITY_LABELS.get(p.value, p.value), p.value)
        pc.addWidget(self._priority_combo)
        layout.addWidget(priority_col)

        # Tip
        type_col = QWidget(parent=row)
        tc = QVBoxLayout(type_col)
        tc.setContentsMargins(0, 0, 0, 0)
        tc.setSpacing(6)
        tc.addWidget(self._make_field_label("Tip"))
        self._type_combo = QComboBox(parent=type_col)
        self._type_combo.setMinimumHeight(36)
        for t in TaskType:
            self._type_combo.addItem(_TYPE_LABELS.get(t.value, t.value), t.value)
        tc.addWidget(self._type_combo)
        layout.addWidget(type_col)

        # Aşama (Stage)
        stage_col = QWidget(parent=row)
        stc = QVBoxLayout(stage_col)
        stc.setContentsMargins(0, 0, 0, 0)
        stc.setSpacing(6)
        stc.addWidget(self._make_field_label("Aşama"))
        self._stage_combo = QComboBox(parent=stage_col)
        self._stage_combo.setMinimumHeight(36)
        self._stage_combo.addItem("Yok", None)
        for s in self._stages:
            self._stage_combo.addItem(s.name, s.id)
        stc.addWidget(self._stage_combo)
        layout.addWidget(stage_col)

        return row

    def _build_button_row(self) -> QWidget:
        row = QWidget(parent=self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        if self._is_edit:
            delete_btn = QPushButton("Sil", parent=row)
            delete_btn.setMinimumSize(80, 38)
            delete_btn.setStyleSheet("color: #EF4444;")
            delete_btn.clicked.connect(self._on_delete)
            layout.addWidget(delete_btn)

        layout.addStretch()

        cancel_btn = QPushButton("İptal", parent=row)
        cancel_btn.setMinimumSize(80, 38)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        save_label = "Kaydet" if self._is_edit else "Ekle"
        self._save_btn = QPushButton(save_label, parent=row)
        self._save_btn.setMinimumSize(80, 38)
        self._save_btn.setObjectName("accent_button")
        self._save_btn.clicked.connect(self._on_save)
        layout.addWidget(self._save_btn)

        return row

    def _build_checklist_section(self, main_layout: QVBoxLayout) -> None:
        main_layout.addWidget(self._make_field_label("Checklist"))
        main_layout.addSpacing(8)

        add_layout = QHBoxLayout()
        add_layout.setContentsMargins(0, 0, 0, 0)
        
        self._chk_edit = QLineEdit(parent=self)
        self._chk_edit.setPlaceholderText("Yeni madde...")
        self._chk_edit.setMinimumHeight(32)
        add_layout.addWidget(self._chk_edit, 1)

        add_btn = QPushButton("Ekle", parent=self)
        add_btn.setMinimumSize(60, 32)
        add_btn.clicked.connect(self._on_add_checklist_item)
        add_layout.addWidget(add_btn)

        main_layout.addLayout(add_layout)
        main_layout.addSpacing(8)

        self._chk_container = QWidget(parent=self)
        self._chk_layout = QVBoxLayout(self._chk_container)
        self._chk_layout.setContentsMargins(0, 0, 0, 0)
        self._chk_layout.setSpacing(4)
        main_layout.addWidget(self._chk_container)
        
        self._render_checklist()

    def _render_checklist(self) -> None:
        # Eski itemları temizle
        while self._chk_layout.count():
            item = self._chk_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self._task or not hasattr(self._task, 'checklist_items'):
            return

        for item in self._task.checklist_items:
            row = QWidget(parent=self._chk_container)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(4, 4, 4, 4)
            rl.setSpacing(8)

            status_char = "●" if item.is_done else "○"
            status_color = "#22C55E" if item.is_done else "#4A4D5C"
            chk_btn = QPushButton(status_char, parent=row)
            chk_btn.setFixedSize(20, 20)
            chk_btn.setStyleSheet(f"color: {status_color}; font-size: 14px; border: none; background: transparent;")
            chk_btn.clicked.connect(lambda checked=False, i_id=item.id: self._on_toggle_checklist_item(i_id))
            rl.addWidget(chk_btn)

            lbl = QLabel(item.text, parent=row)
            text_color = "#6B7280" if item.is_done else "#C8CAD4"
            lbl.setStyleSheet(f"color: {text_color}; font-size: 13px;")
            rl.addWidget(lbl, 1)

            del_btn = QPushButton("×", parent=row)
            del_btn.setFixedSize(20, 20)
            del_btn.setStyleSheet("color: #EF4444; border: none; background: transparent; font-weight: bold; font-size: 16px;")
            del_btn.clicked.connect(lambda checked=False, i_id=item.id: self._on_delete_checklist_item(i_id))
            rl.addWidget(del_btn)

            row.setStyleSheet("QWidget { background: #1E2130; border-radius: 4px; }")
            self._chk_layout.addWidget(row)

    def _on_add_checklist_item(self) -> None:
        text = self._chk_edit.text().strip()
        if text and self._task and self._task_controller:
            self._task_controller.add_checklist_item(self._task.id, text)
            self._chk_edit.clear()

    def _on_toggle_checklist_item(self, item_id: int) -> None:
        if self._task and self._task_controller:
            self._task_controller.toggle_checklist_item(item_id, self._task.id)

    def _on_delete_checklist_item(self, item_id: int) -> None:
        if self._task and self._task_controller:
            self._task_controller.delete_checklist_item(item_id, self._task.id)

    def _on_task_updated_event(self, task: object) -> None:
        if self._task and hasattr(task, 'id') and getattr(task, 'id') == self._task.id:
            self._task = task
            self._render_checklist()

    def _populate_fields(self) -> None:
        t = self._task
        if t is None:
            return
        self._title_edit.setText(t.title)
        if t.description:
            self._desc_edit.setPlainText(t.description)
        for i in range(self._status_combo.count()):
            if self._status_combo.itemData(i) == t.status:
                self._status_combo.setCurrentIndex(i)
                break
        for i in range(self._priority_combo.count()):
            if self._priority_combo.itemData(i) == t.priority:
                self._priority_combo.setCurrentIndex(i)
                break
        for i in range(self._type_combo.count()):
            if self._type_combo.itemData(i) == t.task_type:
                self._type_combo.setCurrentIndex(i)
                break
        
        for i in range(self._stage_combo.count()):
            if self._stage_combo.itemData(i) == t.stage_id:
                self._stage_combo.setCurrentIndex(i)
                break

    def _on_save(self) -> None:
        title = self._title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Geçersiz Giriş", "Görev başlığı boş olamaz.")
            self._title_edit.setFocus()
            return
        self.accept()

    def _on_delete(self) -> None:
        # Silme kararını çağırana bırak; özel result kodu ile sinyalleşir
        self.done(2)

    def get_data(self) -> dict[str, object]:
        """Dialog kabul edildikten sonra çağrılır; dolu alanları döndürür."""
        stage_id = self._stage_combo.currentData()
        return {
            "title": self._title_edit.text().strip(),
            "description": self._desc_edit.toPlainText().strip() or None,
            "status": self._status_combo.currentData(),
            "priority": self._priority_combo.currentData(),
            "task_type": self._type_combo.currentData(),
            "stage_id": stage_id,
        }
