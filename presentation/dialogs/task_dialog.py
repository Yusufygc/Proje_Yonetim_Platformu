"""
Görev oluşturma ve düzenleme için modal dialog.
Yeni görev için boş, var olan görev için alanlar dolu gelir.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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

from controllers.task_controller import TaskController
from domain.enums.priority import Priority
from domain.enums.task_status import TaskStatus
from domain.enums.task_type import TaskType
from domain.models.project_stage import ProjectStage
from domain.models.task import Task




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
        dialog_title.setProperty("cssClass", "title-small")
        layout.addWidget(dialog_title)
        layout.addSpacing(20)

        layout.addWidget(self._make_field_label("Görev Başlığı *"))
        self._error_label = QLabel(parent=self)
        self._error_label.setProperty("cssClass", "text-danger")
        self._error_label.hide()
        layout.addWidget(self._error_label)
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
        lbl.setProperty("cssClass", "field-label")
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
        self._status_combo.addItem("Yapılacak", TaskStatus.TODO.value)
        self._status_combo.addItem("Devam Ediyor", TaskStatus.IN_PROGRESS.value)
        self._status_combo.addItem("Bekliyor", TaskStatus.WAITING.value)
        self._status_combo.addItem("Engellendi", TaskStatus.BLOCKED.value)
        self._status_combo.addItem("Tamamlandı", TaskStatus.DONE.value)
        self._status_combo.addItem("İptal Edildi", TaskStatus.CANCELLED.value)
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
        self._priority_combo.addItem("Düşük", Priority.LOW.value)
        self._priority_combo.addItem("Orta", Priority.MEDIUM.value)
        self._priority_combo.addItem("Yüksek", Priority.HIGH.value)
        self._priority_combo.addItem("Kritik", Priority.CRITICAL.value)
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
        self._type_combo.addItem("Görev", TaskType.TASK.value)
        self._type_combo.addItem("Grup", TaskType.GROUP.value)
        self._type_combo.addItem("Hata", TaskType.BUG.value)
        self._type_combo.addItem("İyileştirme", TaskType.IMPROVEMENT.value)
        self._type_combo.addItem("Araştırma", TaskType.RESEARCH.value)
        self._type_combo.addItem("Dokümantasyon", TaskType.DOCUMENTATION.value)
        self._type_combo.addItem("Tasarım", TaskType.DESIGN.value)
        self._type_combo.addItem("Test", TaskType.TEST.value)
        self._type_combo.addItem("İnceleme", TaskType.REVIEW.value)
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
            delete_btn.setProperty("cssClass", "btn-danger")
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
        while self._chk_layout.count():
            item = self._chk_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._task or not hasattr(self._task, "checklist_items"):
            return

        for item in self._task.checklist_items:
            row = QWidget(parent=self._chk_container)
            row.setProperty("cssClass", "panel-raised")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(4, 4, 4, 4)
            rl.setSpacing(8)

            status_char = "●" if item.is_done else "○"
            chk_btn = QPushButton(status_char, parent=row)
            chk_btn.setFixedSize(20, 20)
            chk_btn.setProperty("cssClass", "chk-done" if item.is_done else "chk-pending")
            chk_btn.clicked.connect(lambda checked=False, i_id=item.id: self._on_toggle_checklist_item(i_id))
            rl.addWidget(chk_btn)

            lbl = QLabel(item.text, parent=row)
            lbl.setProperty("cssClass", "text-muted" if item.is_done else "text-secondary")
            rl.addWidget(lbl, 1)

            del_btn = QPushButton("×", parent=row)
            del_btn.setFixedSize(20, 20)
            del_btn.setProperty("cssClass", "chk-delete")
            del_btn.clicked.connect(lambda checked=False, i_id=item.id: self._on_delete_checklist_item(i_id))
            rl.addWidget(del_btn)

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
            self._error_label.setText("Görev başlığı boş olamaz.")
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
