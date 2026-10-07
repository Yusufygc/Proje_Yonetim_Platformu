"""QML için Hiyerarşik WBS Görev Listeleme Modeli (QAbstractListModel)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
    Slot,
)

from core.text_normalization import normalize_search_text
from domain.models.task import Task

logger = logging.getLogger(__name__)


class TaskItemData:
    """WBS ağacında düzleştirilmiş tek bir satırın meta verileri."""

    def __init__(
        self,
        task: Task,
        level: int,
        wbs_code: str,
        has_children: bool,
        is_expanded: bool,
    ) -> None:
        self.task = task
        self.level = level
        self.wbs_code = wbs_code
        self.has_children = has_children
        self.is_expanded = is_expanded


class TaskListModel(QAbstractListModel):
    """WBS hiyerarşisini QML ListView için düzleştiren ve filtreleyen model."""

    TaskIdRole = Qt.ItemDataRole.UserRole + 1
    ParentIdRole = Qt.ItemDataRole.UserRole + 2
    ProjectIdRole = Qt.ItemDataRole.UserRole + 3
    TitleRole = Qt.ItemDataRole.UserRole + 4
    DescriptionRole = Qt.ItemDataRole.UserRole + 5
    StatusRole = Qt.ItemDataRole.UserRole + 6
    PriorityRole = Qt.ItemDataRole.UserRole + 7
    TaskTypeRole = Qt.ItemDataRole.UserRole + 8
    LevelRole = Qt.ItemDataRole.UserRole + 9
    WbsCodeRole = Qt.ItemDataRole.UserRole + 10
    HasChildrenRole = Qt.ItemDataRole.UserRole + 11
    IsExpandedRole = Qt.ItemDataRole.UserRole + 12
    ChecklistTotalRole = Qt.ItemDataRole.UserRole + 13
    ChecklistDoneRole = Qt.ItemDataRole.UserRole + 14
    DueDateRole = Qt.ItemDataRole.UserRole + 15
    EstimatedMinutesRole = Qt.ItemDataRole.UserRole + 16
    SpentMinutesRole = Qt.ItemDataRole.UserRole + 17

    countChanged = Signal()

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent=parent)
        self._raw_tasks: list[Task] = []
        self._flattened: list[TaskItemData] = []
        self._expanded_overrides: dict[int, bool] = {}
        self._search_query: str = ""
        self._status_filter: str = "ALL"
        self._priority_filter: str = "ALL"
        self._type_filter: str = "ALL"

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.TaskIdRole: QByteArray(b"taskId"),
            self.ParentIdRole: QByteArray(b"parentId"),
            self.ProjectIdRole: QByteArray(b"projectId"),
            self.TitleRole: QByteArray(b"title"),
            self.DescriptionRole: QByteArray(b"description"),
            self.StatusRole: QByteArray(b"status"),
            self.PriorityRole: QByteArray(b"priority"),
            self.TaskTypeRole: QByteArray(b"taskType"),
            self.LevelRole: QByteArray(b"level"),
            self.WbsCodeRole: QByteArray(b"wbsCode"),
            self.HasChildrenRole: QByteArray(b"hasChildren"),
            self.IsExpandedRole: QByteArray(b"isExpanded"),
            self.ChecklistTotalRole: QByteArray(b"checklistTotal"),
            self.ChecklistDoneRole: QByteArray(b"checklistDone"),
            self.DueDateRole: QByteArray(b"dueDate"),
            self.EstimatedMinutesRole: QByteArray(b"estimatedMinutes"),
            self.SpentMinutesRole: QByteArray(b"spentMinutes"),
        }

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self._flattened)

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._flattened)):
            return None
        item = self._flattened[index.row()]
        t = item.task
        return self._extract_role_data(item, t, role)

    def _extract_role_data(self, item: TaskItemData, t: Task, role: int) -> Any:
        if role == self.TaskIdRole:
            return t.id
        if role == self.ParentIdRole:
            return t.parent_task_id or 0
        if role == self.ProjectIdRole:
            return t.project_id
        if role == self.TitleRole:
            return t.title
        if role == self.DescriptionRole:
            return t.description or ""
        if role == self.StatusRole:
            return t.status
        if role == self.PriorityRole:
            return t.priority
        if role == self.TaskTypeRole:
            return t.task_type
        if role == self.LevelRole:
            return item.level
        if role == self.WbsCodeRole:
            return item.wbs_code
        if role == self.HasChildrenRole:
            return item.has_children
        if role == self.IsExpandedRole:
            return item.is_expanded
        return self._extract_checklist_and_date(t, role)

    def _extract_checklist_and_date(self, t: Task, role: int) -> Any:
        items = t.checklist_items or []
        if role == self.ChecklistTotalRole:
            return len(items)
        if role == self.ChecklistDoneRole:
            return sum(1 for c in items if c.is_done)
        if role == self.DueDateRole:
            return t.due_date.isoformat() if t.due_date else ""
        if role == self.EstimatedMinutesRole:
            return t.estimated_minutes or 0
        if role == self.SpentMinutesRole:
            return t.spent_minutes or 0
        return None

    def set_tasks(self, tasks: list[Task]) -> None:
        """Yeni görev listesini yükler ve WBS ağacını yeniden kurar."""
        self._raw_tasks = list(tasks)
        self._rebuild_tree()

    @Slot(int)
    def toggleExpanded(self, task_id: int) -> None:
        """Belirtilen görevin alt dalını açar veya kapatır."""
        current_state = self.is_node_expanded(task_id)
        self._expanded_overrides[task_id] = not current_state
        self._rebuild_tree()

    def is_node_expanded(self, task_id: int) -> bool:
        """Belirtilen görevin açık mı kapalı mı olduğunu döndürür."""
        if task_id in self._expanded_overrides:
            return self._expanded_overrides[task_id]
        for item in self._flattened:
            if item.task.id == task_id:
                return item.is_expanded
        node = next((t for t in self._raw_tasks if t.id == task_id), None)
        if not node:
            return False
        children_map: dict[Optional[int], list[Task]] = {}
        for t in self._raw_tasks:
            children_map.setdefault(t.parent_task_id, []).append(t)
        if children_map.get(node.id) and self._is_subtree_all_done(node, children_map):
            return False
        return True

    def clear_overrides(self) -> None:
        """Kullanıcının açık/kapalı tercihlerini sıfırlar."""
        self._expanded_overrides.clear()

    @Slot(str)
    def setSearchQuery(self, query: str) -> None:
        self._search_query = normalize_search_text(query.strip())
        self._rebuild_tree()

    @Slot(str)
    def setStatusFilter(self, status: str) -> None:
        self._status_filter = status
        self._rebuild_tree()

    @Slot(str)
    def setPriorityFilter(self, priority: str) -> None:
        self._priority_filter = priority
        self._rebuild_tree()

    @Slot(str)
    def setTypeFilter(self, task_type: str) -> None:
        self._type_filter = task_type
        self._rebuild_tree()

    def _matches_filters(self, t: Task) -> bool:
        if self._search_query and self._search_query not in normalize_search_text(t.title):
            return False
        if self._status_filter != "ALL" and t.status != self._status_filter:
            return False
        if self._priority_filter != "ALL" and t.priority != self._priority_filter:
            return False
        if self._type_filter != "ALL" and t.task_type != self._type_filter:
            return False
        return True

    def _is_subtree_all_done(
        self, node: Task, children_map: dict[Optional[int], list[Task]]
    ) -> bool:
        """Düğümün kendisi ve tüm alt görevlerinin 'DONE' olup olmadığını kontrol eder."""
        if node.status != "DONE":
            return False
        children = children_map.get(node.id, [])
        for child in children:
            if not self._is_subtree_all_done(child, children_map):
                return False
        return True

    def _rebuild_tree(self) -> None:
        self.beginResetModel()
        self._flattened.clear()

        # Ebeveyn haritası oluştur
        children_map: dict[Optional[int], list[Task]] = {}
        for t in self._raw_tasks:
            pid = t.parent_task_id
            children_map.setdefault(pid, []).append(t)

        for clist in children_map.values():
            clist.sort(key=lambda x: (x.order_index, x.id))

        root_tasks = children_map.get(None, [])
        for i, root in enumerate(root_tasks, 1):
            self._traverse_node(root, level=0, code=str(i), children_map=children_map)

        self.endResetModel()
        self.countChanged.emit()

    def _traverse_node(
        self,
        node: Task,
        level: int,
        code: str,
        children_map: dict[Optional[int], list[Task]],
    ) -> None:
        children = children_map.get(node.id, [])
        has_children = len(children) > 0

        # Genişletilme durumu
        if node.id in self._expanded_overrides:
            is_expanded = self._expanded_overrides[node.id]
        else:
            # Alt görevleri olup da kendisi dahil tüm alt görevler bittiyse varsayılan olarak kapalı kalsın
            if has_children and self._is_subtree_all_done(node, children_map):
                is_expanded = False
            else:
                is_expanded = True

        # Arama sorgusu varsa ve alt görevlerden biri eşleşiyorsa görünür olması için zorunlu aç
        if self._search_query and has_children and self._any_child_matches(node, children_map):
            is_expanded = True

        # Filtreye uyuyorsa veya alt görevlerinden biri filtreye uyuyorsa ekle
        if self._matches_filters(node) or self._any_child_matches(node, children_map):
            self._flattened.append(
                TaskItemData(node, level, code, has_children, is_expanded)
            )

        if has_children and is_expanded:
            for idx, child in enumerate(children, 1):
                child_code = f"{code}.{idx}"
                self._traverse_node(child, level + 1, child_code, children_map)

    def _any_child_matches(
        self, node: Task, children_map: dict[Optional[int], list[Task]]
    ) -> bool:
        for c in children_map.get(node.id, []):
            if self._matches_filters(c) or self._any_child_matches(c, children_map):
                return True
        return False
