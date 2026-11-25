"""WBS görev sürükle-bırak hedefi ve yeni sıra indeksini hesaplayan saf yardımcı."""
from __future__ import annotations

from domain.models.task import Task


def is_descendant(tasks: list[Task], candidate_id: int, ancestor_id: int) -> bool:
    """candidate_id görevinin ancestor_id görevinin alt soyunda olup olmadığını döndürür."""
    parent_map = {t.id: t.parent_task_id for t in tasks}
    current_id: int | None = candidate_id
    seen: set[int] = set()
    while current_id is not None and current_id not in seen:
        if current_id == ancestor_id:
            return True
        seen.add(current_id)
        current_id = parent_map.get(current_id)
    return False


def compute_relative_move(
    tasks: list[Task],
    dragged_id: int,
    target_id: int,
    position: str,
) -> tuple[int | None, int] | None:
    """Bırakma pozisyonuna ('before' | 'after' | 'into') göre (new_parent_id, new_order_index) hesaplar."""
    if dragged_id <= 0 or target_id <= 0 or dragged_id == target_id:
        return None
    dragged = next((t for t in tasks if t.id == dragged_id), None)
    target = next((t for t in tasks if t.id == target_id), None)
    if dragged is None or target is None or is_descendant(tasks, target_id, dragged_id):
        return None

    if position == "into":
        children = [t for t in tasks if t.parent_task_id == target.id and t.id != dragged_id]
        return target.id, len(children)

    if position in ("before", "after"):
        new_parent_id = target.parent_task_id
        siblings = sorted(
            [t for t in tasks if t.parent_task_id == new_parent_id and t.id != dragged_id],
            key=lambda item: (item.order_index, item.id),
        )
        target_idx = next((i for i, t in enumerate(siblings) if t.id == target_id), len(siblings))
        return new_parent_id, (target_idx if position == "before" else target_idx + 1)

    return None
