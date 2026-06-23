"""WBS ağacı: sürükle-bırak ile görev taşıma ve tema duyarlı render."""
from __future__ import annotations

from PySide6.QtCore import QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QColor, QDropEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGraphicsOpacityEffect,
    QHeaderView,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from core.managers.theme_manager import ThemeManager
from domain.enums.task_status import TaskStatus
from domain.models.task import Task
from presentation.utils.i18n import tr


def _label_status(value: str) -> str:
    return {
        "TODO":        tr("task_status_todo",        "Yapılacak"),
        "IN_PROGRESS": tr("task_status_in_progress", "Devam Ediyor"),
        "WAITING":     tr("task_status_waiting",     "Bekliyor"),
        "BLOCKED":     tr("task_status_blocked",     "Engellendi"),
        "DONE":        tr("task_status_done",        "Tamamlandı"),
        "CANCELLED":   tr("task_status_cancelled",   "İptal Edildi"),
    }.get(value, value)


def _label_priority(value: str) -> str:
    return {
        "LOW":      tr("priority_low",      "Düşük"),
        "MEDIUM":   tr("priority_medium",   "Orta"),
        "HIGH":     tr("priority_high",     "Yüksek"),
        "CRITICAL": tr("priority_critical", "Kritik"),
    }.get(value, value)


def _label_task_type(value: str) -> str:
    return {
        "TASK":          tr("task_type_task",          "Görev"),
        "GROUP":         tr("task_type_group",         "Grup"),
        "BUG":           tr("task_type_bug",           "Hata"),
        "IMPROVEMENT":   tr("task_type_improvement",   "İyileştirme"),
        "RESEARCH":      tr("task_type_research",      "Araştırma"),
        "DOCUMENTATION": tr("task_type_documentation", "Dokümantasyon"),
        "DESIGN":        tr("task_type_design",        "Tasarım"),
        "TEST":          tr("task_type_test",          "Test"),
        "REVIEW":        tr("task_type_review",        "İnceleme"),
    }.get(value, value)


# Durum sütunu rengi QSS ile verilemez (satır bazlı dinamik veri);
# bu yüzden palet anahtarından programatik çözülür.
_STATUS_THEME_KEYS: dict[str, str] = {
    "TODO": "text_secondary",
    "IN_PROGRESS": "accent_start",
    "WAITING": "warning",
    "BLOCKED": "danger",
    "DONE": "success",
    "CANCELLED": "text_muted",
}


class WBSTreeWidget(QTreeWidget):
    """
    Görev hiyerarşisini çizen ve içsel taşımaları sinyalle raporlayan ağaç.

    Render, tema rengi çözümleme ve fade-in animasyonu bu sınıfın
    sorumluluğundadır; sayfa yalnızca veri sağlar ve sinyalleri dinler.
    """

    # (task_id, new_parent_task_id | None, new_order_index)
    task_moved = Signal(int, object, int)

    def __init__(self, parent: QWidget | None = None, theme: ThemeManager | None = None) -> None:
        super().__init__(parent=parent)
        # Constructor injection tercih edilir; None ise singleton'a düşülür.
        self._theme = theme or ThemeManager.instance()
        self._drag_task_id: int | None = None
        self._configure()

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(150)

    def _configure(self) -> None:
        self.setHeaderLabels([
            tr("task_tree_title", "Görev Başlığı"),
            tr("task_tree_status", "Durum"),
            tr("task_tree_priority", "Öncelik"),
            tr("task_tree_type", "Tip"),
        ])
        header = self.header()
        for i in range(4):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAlternatingRowColors(True)

    def resizeEvent(self, event: object) -> None:
        super().resizeEvent(event)
        total_width = self.viewport().width()
        self.setColumnWidth(0, int(total_width * 0.55))
        self.setColumnWidth(1, int(total_width * 0.15))
        self.setColumnWidth(2, int(total_width * 0.15))
        self.setColumnWidth(3, int(total_width * 0.15))

    # ── Render ───────────────────────────────────────────────────────────────

    def render_tasks(self, tasks: list[Task]) -> None:
        """Görev listesini hiyerarşik olarak çizer ve fade-in oynatır."""
        self.blockSignals(True)
        items_dict: dict[int, QTreeWidgetItem] = {}

        # Renkler döngü dışında bir kez çözülür; her görev için palet sorgusu
        # ve QColor üretimi tekrarlanmaz.
        status_colors = {
            status: QColor(self._theme.color(key))
            for status, key in _STATUS_THEME_KEYS.items()
        }
        default_color = QColor(self._theme.color("text_secondary"))
        muted_color = QColor(self._theme.color("text_muted"))

        # Toplu ekleme sırasında ara boyamaları engellemek için güncelleme kapatılır.
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            for task in tasks:
                item = QTreeWidgetItem([
                    task.title,
                    _label_status(task.status),
                    _label_priority(task.priority),
                    _label_task_type(task.task_type),
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, task.id)
                item.setData(0, Qt.ItemDataRole.UserRole + 1, "task")
                item.setToolTip(0, task.title)
                if task.description:
                    item.setToolTip(1, task.description)
                
                # Checkbox durumunu ayarla
                item.setCheckState(0, Qt.CheckState.Checked if task.status == TaskStatus.DONE.value else Qt.CheckState.Unchecked)

                if task.status == TaskStatus.DONE.value:
                    for col in range(4):
                        font = item.font(col)
                        font.setStrikeOut(True)
                        item.setFont(col, font)
                        item.setForeground(col, muted_color)
                else:
                    item.setForeground(1, status_colors.get(task.status, default_color))
                
                items_dict[task.id] = item

            root_items: list[QTreeWidgetItem] = []
            for task in tasks:
                item = items_dict[task.id]
                if task.parent_task_id and task.parent_task_id in items_dict:
                    items_dict[task.parent_task_id].addChild(item)
                else:
                    root_items.append(item)

            # Checklist maddelerini hiyerarşik olarak ekle
            for task in tasks:
                item = items_dict[task.id]
                if task.checklist_items:
                    for cl_item in task.checklist_items:
                        cl_widget_item = QTreeWidgetItem([
                            cl_item.text,
                            tr("task_status_done", "Tamamlandı") if cl_item.is_done else tr("task_status_todo", "Yapılacak"),
                            "-",
                            tr("checklist", "Checklist"),
                        ])
                        cl_widget_item.setData(0, Qt.ItemDataRole.UserRole, cl_item.id)
                        cl_widget_item.setData(0, Qt.ItemDataRole.UserRole + 1, "checklist")
                        cl_widget_item.setData(0, Qt.ItemDataRole.UserRole + 2, task.id)
                        cl_widget_item.setCheckState(0, Qt.CheckState.Checked if cl_item.is_done else Qt.CheckState.Unchecked)

                        if cl_item.is_done:
                            for col in range(4):
                                font = cl_widget_item.font(col)
                                font.setStrikeOut(True)
                                cl_widget_item.setFont(col, font)
                                cl_widget_item.setForeground(col, muted_color)
                        else:
                            cl_widget_item.setForeground(1, status_colors.get("TODO", default_color))

                        item.addChild(cl_widget_item)

            self.addTopLevelItems(root_items)
            self.expandAll()
        finally:
            self.setUpdatesEnabled(True)
            self.blockSignals(False)

        self._opacity.setOpacity(0.0)
        self._fade.stop()
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.start()

    # ── Sürükle-bırak ────────────────────────────────────────────────────────

    def startDrag(self, supported_actions: object) -> None:  # type: ignore[override]
        item = self.currentItem()
        if item:
            item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
            if item_type == "checklist":
                return
        self._drag_task_id = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        super().startDrag(supported_actions)  # type: ignore[arg-type]

    def dropEvent(self, event: QDropEvent) -> None:
        dragged_id = self._drag_task_id
        super().dropEvent(event)
        self._drag_task_id = None
        if dragged_id is None:
            return
        moved_item = self._find_item_by_task_id(dragged_id)
        if moved_item is None:
            return
        parent_item = moved_item.parent()
        if parent_item and parent_item.data(0, Qt.ItemDataRole.UserRole + 1) == "checklist":
            parent_item = parent_item.parent()
        new_parent_id = parent_item.data(0, Qt.ItemDataRole.UserRole) if parent_item else None
        new_order = parent_item.indexOfChild(moved_item) if parent_item else self.indexOfTopLevelItem(moved_item)
        self.task_moved.emit(dragged_id, new_parent_id, new_order)

    def _find_item_by_task_id(self, task_id: int) -> QTreeWidgetItem | None:
        stack = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]
        while stack:
            item = stack.pop()
            if item is None:
                continue
            if item.data(0, Qt.ItemDataRole.UserRole) == task_id and item.data(0, Qt.ItemDataRole.UserRole + 1) == "task":
                return item
            stack.extend(item.child(i) for i in range(item.childCount()))
        return None
