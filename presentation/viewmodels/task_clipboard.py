"""Görev ağacını panoya kopyalanacak girintili metne çeviren saf yardımcı."""
from __future__ import annotations

from domain.models.task import Task


def collect_task_copy_lines(tasks: list[Task], root_task_id: int) -> list[str]:
    """Görevi ve alt görevlerini derinliğe göre girintili, checklist maddeleriyle toplar."""
    by_id = {item.id: item for item in tasks}
    root_task = by_id.get(root_task_id)
    if root_task is None:
        return []

    children_by_parent: dict[int | None, list[Task]] = {}
    for item in tasks:
        children_by_parent.setdefault(item.parent_task_id, []).append(item)

    lines: list[str] = []
    stack: list[tuple[Task, int]] = [(root_task, 0)]
    while stack:
        current, depth = stack.pop()
        indent = "  " * depth
        lines.append(f"{indent}[{current.status}] {current.title}")
        for checklist_item in current.checklist_items or []:
            mark = "[x]" if checklist_item.is_done else "[ ]"
            lines.append(f"{indent}  {mark} {checklist_item.text}")
        for child in reversed(children_by_parent.get(current.id, [])):
            stack.append((child, depth + 1))
    return lines
