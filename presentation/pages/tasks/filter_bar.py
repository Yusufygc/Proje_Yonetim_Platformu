"""Görevler sayfası başlık ve filtre çubuğu (proje seçimi + durum/öncelik/tür/aşama)."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from domain.enums.priority import Priority
from domain.enums.task_status import TaskStatus
from domain.enums.task_type import TaskType
from domain.models.project import Project
from domain.models.task import Task
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr


class TaskFilterBar(QWidget):
    """
    Başlık satırı + filtre satırından oluşan üst çubuk.

    Filtreleme mantığının tek sahibi budur: sayfa, görev listesini
    `apply()` ile süzdürür ve hızlı eklemede `filter_values()` kullanır.
    """

    project_changed = Signal(object)  # project_id | None
    filters_changed = Signal()
    add_root_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(Spacing.MD)

        row1 = QWidget(parent=self)
        r1 = QHBoxLayout(row1)
        r1.setContentsMargins(0, 0, 0, 0)
        title = QLabel(tr("tasks_wbs_title", "İş Kırılım Yapısı (WBS)"), parent=row1)
        title.setProperty("cssClass", "title-medium")
        r1.addWidget(title)
        r1.addStretch()
        add_btn = QPushButton(tr("task_add_root", "+ Ana Görev Ekle"), parent=row1)
        add_btn.setProperty("cssClass", "btn-primary")
        add_btn.setMinimumSize(Size.BTN_MD_W + 40, Size.BTN_SM_H)
        add_btn.clicked.connect(self.add_root_requested.emit)
        r1.addWidget(add_btn)
        outer.addWidget(row1)

        row2 = QWidget(parent=self)
        r2 = QHBoxLayout(row2)
        r2.setContentsMargins(0, 0, 0, 0)
        r2.setSpacing(Spacing.SM)
        lbl = QLabel(tr("label_project", "Proje:"), parent=row2)
        lbl.setProperty("cssClass", "text-secondary")
        r2.addWidget(lbl)
        self._project_combo = QComboBox(parent=row2)
        self._project_combo.setMinimumWidth(120)
        self._project_combo.setMinimumHeight(Size.BTN_SM_H)
        self._project_combo.currentIndexChanged.connect(self._on_project_index_changed)
        r2.addWidget(self._project_combo, 1)
        self._status_filter = self._make_filter_combo(
            tr("filter_status", "Durum"), [(s.value, s.value) for s in TaskStatus]
        )
        r2.addWidget(self._status_filter)
        self._priority_filter = self._make_filter_combo(
            tr("filter_priority", "Öncelik"), [(p.value, p.value) for p in Priority]
        )
        r2.addWidget(self._priority_filter)
        self._type_filter = self._make_filter_combo(
            tr("filter_type", "Tür"), [(t.value, t.value) for t in TaskType]
        )
        r2.addWidget(self._type_filter)
        self._stage_filter = self._make_filter_combo(tr("filter_stage", "Aşama"), [])
        r2.addWidget(self._stage_filter)
        outer.addWidget(row2)

    def _make_filter_combo(self, label: str, values: list[tuple[str, str]]) -> QComboBox:
        combo = QComboBox(parent=self)
        combo.setMinimumHeight(Size.BTN_SM_H)
        combo.setMinimumWidth(70)
        combo.addItem(label, None)
        for text, value in values:
            combo.addItem(text, value)
        combo.currentIndexChanged.connect(lambda _idx: self.filters_changed.emit())
        return combo

    def _on_project_index_changed(self, index: int) -> None:
        self.project_changed.emit(self._project_combo.itemData(index))

    # ── Proje seçimi ─────────────────────────────────────────────────────────

    def set_projects(self, projects: list[Project], selected_id: int | None) -> None:
        """Combobox'ı doldurur; sinyal tetiklemeden mevcut seçimi korur."""
        self._project_combo.blockSignals(True)
        self._project_combo.clear()
        if not projects:
            self._project_combo.addItem(tr("project_not_found", "Proje Bulunamadı"))
        else:
            for project in projects:
                self._project_combo.addItem(project.title, project.id)
            if selected_id is not None:
                idx = self._project_combo.findData(selected_id)
                if idx >= 0:
                    self._project_combo.setCurrentIndex(idx)
        self._project_combo.blockSignals(False)

    def select_project(self, project_id: int) -> None:
        idx = self._project_combo.findData(project_id)
        if idx >= 0:
            self._project_combo.setCurrentIndex(idx)

    # ── Filtreleme ───────────────────────────────────────────────────────────

    def apply(self, tasks: list[Task]) -> list[Task]:
        """Aktif filtre değerleriyle görev listesini süzer."""
        status = self._status_filter.currentData()
        priority = self._priority_filter.currentData()
        task_type = self._type_filter.currentData()
        stage_id = self._stage_filter.currentData()
        result = []
        for task in tasks:
            if status and task.status != status:
                continue
            if priority and task.priority != priority:
                continue
            if task_type and task.task_type != task_type:
                continue
            if stage_id is not None and task.stage_id != stage_id:
                continue
            result.append(task)
        return result

    def filter_values(self) -> dict[str, object]:
        """Hızlı eklemede yeni göreve uygulanacak aktif filtre değerleri."""
        values: dict[str, object] = {}
        if self._status_filter.currentData():
            values["status"] = self._status_filter.currentData()
        if self._priority_filter.currentData():
            values["priority"] = self._priority_filter.currentData()
        if self._type_filter.currentData():
            values["task_type"] = self._type_filter.currentData()
        if self._stage_filter.currentData():
            values["stage_id"] = self._stage_filter.currentData()
        return values

    def reload_stage_filter(self, tasks: list[Task]) -> None:
        """Aşama filtresini görevlerde geçen stage_id'lerle tazeler, seçimi korur."""
        current = self._stage_filter.currentData()
        self._stage_filter.blockSignals(True)
        self._stage_filter.clear()
        self._stage_filter.addItem(tr("filter_stage", "Aşama"), None)
        stage_ids = sorted({task.stage_id for task in tasks if task.stage_id is not None})
        for stage_id in stage_ids:
            self._stage_filter.addItem(
                tr("filter_stage_item", "Aşama #{id}").format(id=stage_id), stage_id
            )
        if current is not None:
            idx = self._stage_filter.findData(current)
            if idx >= 0:
                self._stage_filter.setCurrentIndex(idx)
        self._stage_filter.blockSignals(False)
