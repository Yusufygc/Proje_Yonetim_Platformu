"""
Görev oluşturma ve düzenleme için modal dialog.
Yeni görev için boş, var olan görev için alanlar dolu gelir.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from controllers.task_controller import TaskController
from domain.enums.priority import Priority
from domain.enums.task_status import TaskStatus
from domain.enums.task_type import TaskType
from domain.models.task import Task
from presentation.dialogs.form_utils import (
    make_combo_column,
    select_combo_data,
    set_field_error,
)
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr


def _task_status_items() -> list[tuple[str, str]]:
    """(etiket, enum değeri) — dil değişimi dialog her açılışta yansısın diye fonksiyon."""
    return [
        (tr("task_status_todo", "Yapılacak"), TaskStatus.TODO.value),
        (tr("task_status_in_progress", "Devam Ediyor"), TaskStatus.IN_PROGRESS.value),
        (tr("task_status_waiting", "Bekliyor"), TaskStatus.WAITING.value),
        (tr("task_status_blocked", "Engellendi"), TaskStatus.BLOCKED.value),
        (tr("task_status_done", "Tamamlandı"), TaskStatus.DONE.value),
        (tr("task_status_cancelled", "İptal Edildi"), TaskStatus.CANCELLED.value),
    ]


def _task_priority_items() -> list[tuple[str, str]]:
    return [
        (tr("priority_low", "Düşük"), Priority.LOW.value),
        (tr("priority_medium", "Orta"), Priority.MEDIUM.value),
        (tr("priority_high", "Yüksek"), Priority.HIGH.value),
        (tr("priority_critical", "Kritik"), Priority.CRITICAL.value),
    ]


def _task_type_items() -> list[tuple[str, str]]:
    return [
        (tr("task_type_task", "Görev"), TaskType.TASK.value),
        (tr("task_type_group", "Grup"), TaskType.GROUP.value),
        (tr("task_type_bug", "Hata"), TaskType.BUG.value),
        (tr("task_type_improvement", "İyileştirme"), TaskType.IMPROVEMENT.value),
        (tr("task_type_research", "Araştırma"), TaskType.RESEARCH.value),
        (tr("task_type_documentation", "Dokümantasyon"), TaskType.DOCUMENTATION.value),
        (tr("task_type_design", "Tasarım"), TaskType.DESIGN.value),
        (tr("task_type_test", "Test"), TaskType.TEST.value),
        (tr("task_type_review", "İnceleme"), TaskType.REVIEW.value),
    ]


class TaskDialog(QDialog):
    """Görev oluşturma (task=None) veya düzenleme modal dialog'u."""

    def __init__(
        self,
        parent: QWidget,
        task: Task | None = None,
        task_controller: TaskController | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._task = task
        self._is_edit = task is not None
        self._task_controller = task_controller
        # Yeni görev modunda checklist maddeleri geçici olarak burada tutulur
        self._chk_pending: list[str] = []
        self._setup_ui()
        if self._is_edit:
            self._populate_fields()

        if self._task_controller:
            self._task_controller.task_updated.connect(self._on_task_updated_event)

    def _setup_ui(self) -> None:
        title_text = (
            tr("task_dialog_edit_title", "Görevi Düzenle")
            if self._is_edit
            else tr("task_dialog_new_title", "Yeni Görev Ekle")
        )
        self.setWindowTitle(title_text)
        self.setMinimumWidth(Size.DIALOG_TASK_MIN_W)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXXL, Spacing.XXXL, Spacing.XXXL, Spacing.XXL)
        layout.setSpacing(0)

        dialog_title = QLabel(title_text, parent=self)
        dialog_title.setProperty("cssClass", "title-small")
        layout.addWidget(dialog_title)
        layout.addSpacing(20)

        layout.addWidget(self._make_field_label(tr("task_dialog_title_label", "Görev Başlığı *")))
        self._error_label = QLabel(parent=self)
        self._error_label.setProperty("cssClass", "text-danger")
        self._error_label.hide()
        layout.addWidget(self._error_label)
        layout.addSpacing(6)
        self._title_edit = QLineEdit(parent=self)
        self._title_edit.setPlaceholderText(tr("task_dialog_title_placeholder", "Görevin adını girin..."))
        self._title_edit.setMinimumHeight(Size.INPUT_H_LG)
        layout.addWidget(self._title_edit)
        layout.addSpacing(16)

        layout.addWidget(self._make_field_label(tr("label_description", "Açıklama")))
        layout.addSpacing(6)
        self._desc_edit = QTextEdit(parent=self)
        self._desc_edit.setPlaceholderText(tr("task_dialog_desc_placeholder", "Görevi açıklayın (isteğe bağlı)..."))
        self._desc_edit.setMaximumHeight(Size.TEXTAREA_H_MD)
        layout.addWidget(self._desc_edit)
        layout.addSpacing(16)

        layout.addWidget(self._build_combos_row())
        layout.addSpacing(28)

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
        layout.setSpacing(Spacing.LG)

        status_col, self._status_combo = make_combo_column(
            row, tr("label_status", "Durum"), _task_status_items()
        )
        layout.addWidget(status_col)

        priority_col, self._priority_combo = make_combo_column(
            row, tr("label_priority", "Öncelik"), _task_priority_items()
        )
        layout.addWidget(priority_col)

        type_col, self._type_combo = make_combo_column(
            row, tr("label_type", "Tip"), _task_type_items()
        )
        layout.addWidget(type_col)

        return row

    def _build_button_row(self) -> QWidget:
        row = QWidget(parent=self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MD)

        if self._is_edit:
            delete_btn = QPushButton(tr("action_delete", "Sil"), parent=row)
            delete_btn.setMinimumSize(Size.BTN_MD_W, Size.BTN_MD_H38)
            delete_btn.setProperty("cssClass", "btn-danger")
            delete_btn.clicked.connect(self._on_delete)
            layout.addWidget(delete_btn)

        layout.addStretch()

        cancel_btn = QPushButton(tr("action_cancel", "İptal"), parent=row)
        cancel_btn.setMinimumSize(Size.BTN_MD_W, Size.BTN_MD_H38)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        save_label = tr("action_save", "Kaydet") if self._is_edit else tr("action_add", "Ekle")
        self._save_btn = QPushButton(save_label, parent=row)
        self._save_btn.setMinimumSize(Size.BTN_MD_W, Size.BTN_MD_H38)
        self._save_btn.setObjectName("accent_button")
        self._save_btn.clicked.connect(self._on_save)
        layout.addWidget(self._save_btn)

        return row

    def _build_checklist_section(self, main_layout: QVBoxLayout) -> None:
        main_layout.addWidget(self._make_field_label(tr("label_checklist", "Checklist")))
        main_layout.addSpacing(8)

        add_layout = QHBoxLayout()
        add_layout.setContentsMargins(0, 0, 0, 0)

        self._chk_edit = QLineEdit(parent=self)
        self._chk_edit.setPlaceholderText(tr("task_dialog_checklist_placeholder", "Yeni madde..."))
        self._chk_edit.setMinimumHeight(Size.INPUT_H_SM)
        self._chk_edit.returnPressed.connect(self._on_add_checklist_item)
        add_layout.addWidget(self._chk_edit, 1)

        add_btn = QPushButton(tr("action_add", "Ekle"), parent=self)
        add_btn.setMinimumSize(Size.BTN_SM_W, Size.INPUT_H_SM)
        add_btn.clicked.connect(self._on_add_checklist_item)
        add_layout.addWidget(add_btn)

        main_layout.addLayout(add_layout)
        main_layout.addSpacing(8)

        self._chk_container = QWidget(parent=self)
        self._chk_layout = QVBoxLayout(self._chk_container)
        self._chk_layout.setContentsMargins(0, 0, 0, 0)
        self._chk_layout.setSpacing(4)
        main_layout.addWidget(self._chk_container)

        if self._is_edit:
            self._render_checklist()

    def _render_checklist(self) -> None:
        """Edit modunda DB'deki checklist item'larını render eder (toggle + sil destekler)."""
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
            rl.setContentsMargins(Spacing.XS, Spacing.XS, Spacing.XS, Spacing.XS)
            rl.setSpacing(Spacing.MD)

            status_char = "●" if item.is_done else "○"
            chk_btn = QPushButton(status_char, parent=row)
            chk_btn.setFixedSize(Size.BTN_ICON_SM, Size.BTN_ICON_SM)
            chk_btn.setProperty("cssClass", "chk-done" if item.is_done else "chk-pending")
            chk_btn.clicked.connect(lambda checked=False, i_id=item.id: self._on_toggle_checklist_item(i_id))
            rl.addWidget(chk_btn)

            lbl = QLabel(item.text, parent=row)
            lbl.setProperty("cssClass", "text-muted" if item.is_done else "text-secondary")
            rl.addWidget(lbl, 1)

            del_btn = QPushButton("×", parent=row)
            del_btn.setFixedSize(Size.BTN_ICON_SM, Size.BTN_ICON_SM)
            del_btn.setProperty("cssClass", "chk-delete")
            del_btn.clicked.connect(lambda checked=False, i_id=item.id: self._on_delete_checklist_item(i_id))
            rl.addWidget(del_btn)

            self._chk_layout.addWidget(row)

    def _render_pending_checklist(self) -> None:
        """Yeni görev modunda geçici listeyi render eder (sadece sil destekler)."""
        while self._chk_layout.count():
            item = self._chk_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for idx, text in enumerate(self._chk_pending):
            row = QWidget(parent=self._chk_container)
            row.setProperty("cssClass", "panel-raised")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(Spacing.XS, Spacing.XS, Spacing.XS, Spacing.XS)
            rl.setSpacing(Spacing.MD)

            lbl = QLabel(f"○  {text}", parent=row)
            lbl.setProperty("cssClass", "text-secondary")
            rl.addWidget(lbl, 1)

            del_btn = QPushButton("×", parent=row)
            del_btn.setFixedSize(Size.BTN_ICON_SM, Size.BTN_ICON_SM)
            del_btn.setProperty("cssClass", "chk-delete")
            del_btn.clicked.connect(lambda checked=False, i=idx: self._on_remove_pending_item(i))
            rl.addWidget(del_btn)

            self._chk_layout.addWidget(row)

    def _on_add_checklist_item(self) -> None:
        text = self._chk_edit.text().strip()
        if not text:
            return
        self._chk_edit.clear()
        if self._is_edit:
            if self._task and self._task_controller:
                self._task_controller.add_checklist_item(self._task.id, text)
        else:
            self._chk_pending.append(text)
            self._render_pending_checklist()

    def _on_remove_pending_item(self, index: int) -> None:
        if 0 <= index < len(self._chk_pending):
            self._chk_pending.pop(index)
            self._render_pending_checklist()

    def _on_toggle_checklist_item(self, item_id: int) -> None:
        if self._task and self._task_controller:
            self._task_controller.toggle_checklist_item(item_id, self._task.id)

    def _on_delete_checklist_item(self, item_id: int) -> None:
        if self._task and self._task_controller:
            self._task_controller.delete_checklist_item(item_id, self._task.id)

    def _on_task_updated_event(self, task: object) -> None:
        if self._task and hasattr(task, "id") and getattr(task, "id") == self._task.id:
            self._task = task
            self._render_checklist()

    def _populate_fields(self) -> None:
        t = self._task
        if t is None:
            return
        self._title_edit.setText(t.title)
        if t.description:
            self._desc_edit.setPlainText(t.description)
        select_combo_data(self._status_combo, t.status)
        select_combo_data(self._priority_combo, t.priority)
        select_combo_data(self._type_combo, t.task_type)

    def _on_save(self) -> None:
        title = self._title_edit.text().strip()
        if not title:
            self._error_label.setText(tr("task_dialog_title_required", "Görev başlığı boş olamaz."))
            self._error_label.show()
            set_field_error(self._title_edit, True)
            self._title_edit.setFocus()
            return

        self._error_label.hide()
        set_field_error(self._title_edit, False)
        self.accept()

    def _on_delete(self) -> None:
        # Silme kararını çağırana bırak; özel result kodu ile sinyalleşir
        self.done(2)

    def get_data(self) -> dict[str, object]:
        """Dialog kabul edildikten sonra çağrılır; dolu alanları döndürür."""
        data: dict[str, object] = {
            "title": self._title_edit.text().strip(),
            "description": self._desc_edit.toPlainText().strip() or None,
            "status": self._status_combo.currentData(),
            "priority": self._priority_combo.currentData(),
            "task_type": self._type_combo.currentData(),
        }
        if not self._is_edit and self._chk_pending:
            data["checklist_items"] = list(self._chk_pending)
        return data
