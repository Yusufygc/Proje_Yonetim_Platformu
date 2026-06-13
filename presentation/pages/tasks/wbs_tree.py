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
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAlternatingRowColors(True)

    # ── Render ───────────────────────────────────────────────────────────────

    def render_tasks(self, tasks: list[Task]) -> None:
        """Görev listesini hiyerarşik olarak çizer ve fade-in oynatır."""
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
                item = QTreeWidgetItem([task.title, task.status, task.priority, task.task_type])
                item.setData(0, Qt.ItemDataRole.UserRole, task.id)
                item.setToolTip(0, task.title)
                if task.description:
                    item.setToolTip(1, task.description)
                item.setForeground(1, status_colors.get(task.status, default_color))
                if task.status == TaskStatus.DONE.value:
                    item.setForeground(0, muted_color)
                    item.setForeground(1, muted_color)
                items_dict[task.id] = item

            root_items: list[QTreeWidgetItem] = []
            for task in tasks:
                item = items_dict[task.id]
                if task.parent_task_id and task.parent_task_id in items_dict:
                    items_dict[task.parent_task_id].addChild(item)
                else:
                    root_items.append(item)

            self.addTopLevelItems(root_items)
            self.expandAll()
        finally:
            self.setUpdatesEnabled(True)

        self._opacity.setOpacity(0.0)
        self._fade.stop()
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.start()

    # ── Sürükle-bırak ────────────────────────────────────────────────────────

    def startDrag(self, supported_actions: object) -> None:  # type: ignore[override]
        item = self.currentItem()
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
        new_parent_id = parent_item.data(0, Qt.ItemDataRole.UserRole) if parent_item else None
        new_order = parent_item.indexOfChild(moved_item) if parent_item else self.indexOfTopLevelItem(moved_item)
        self.task_moved.emit(dragged_id, new_parent_id, new_order)

    def _find_item_by_task_id(self, task_id: int) -> QTreeWidgetItem | None:
        stack = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]
        while stack:
            item = stack.pop()
            if item is None:
                continue
            if item.data(0, Qt.ItemDataRole.UserRole) == task_id:
                return item
            stack.extend(item.child(i) for i in range(item.childCount()))
        return None
