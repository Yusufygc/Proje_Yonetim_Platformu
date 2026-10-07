"""Analitik sayfasının genel bakış verileri: aktivite ısı haritası, durum dağılımı, açılan/biten akışı ve ortalama süre."""
from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select

from domain.enums.task_status import TaskStatus
from domain.models.task import Task

HEATMAP_WEEKS = 12
_MONTHS_TR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]  # l10n: data


def _naive_utc(value: datetime) -> datetime:
    """Saat dilimli ve dilimsiz kayıtları aynı ölçüye getirir (çıkarma işlemi için)."""
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def activity_heatmap(sess: Any, project_id: int | None, today: date) -> dict[str, Any]:
    """Son 12 haftanın gün gün tamamlanan görev sayısı; sütun = hafta, satır = gün (0: pazartesi)."""
    first_monday = today - timedelta(days=today.weekday()) - timedelta(weeks=HEATMAP_WEEKS - 1)
    start = datetime(first_monday.year, first_monday.month, first_monday.day, tzinfo=timezone.utc)
    day_col = func.strftime("%Y-%m-%d", Task.completed_at).label("day")
    stmt = (
        select(day_col, func.count(Task.id).label("cnt"))
        .where(Task.status == TaskStatus.DONE.value)
        .where(Task.completed_at >= start)
        .group_by(day_col)
    )
    if project_id is not None:
        stmt = stmt.where(Task.project_id == project_id)
    counts = {row.day: row.cnt for row in sess.execute(stmt)}

    cells = []
    for offset in range(HEATMAP_WEEKS * 7):
        day = first_monday + timedelta(days=offset)
        cells.append({
            "date": day.isoformat(),
            "label": f"{day.day} {_MONTHS_TR[day.month - 1]} {day.year}",
            "count": counts.get(day.isoformat(), 0),
            "col": offset // 7,
            "row": offset % 7,
            "future": day > today,
        })
    return {"cells": cells, "max": max((c["count"] for c in cells), default=0)}


def status_distribution(sess: Any, project_id: int | None) -> dict[str, int]:
    """Her görev durumundaki görev sayısı (enum değeriyle anahtarlı)."""
    stmt = select(Task.status, func.count(Task.id)).group_by(Task.status)
    if project_id is not None:
        stmt = stmt.where(Task.project_id == project_id)
    return {row[0]: row[1] for row in sess.execute(stmt)}


def flow_series(
    sess: Any,
    start: datetime,
    end: datetime,
    fmt: str,
    all_keys: list[str],
    label_fn: Callable[[str], str],
    project_id: int | None,
) -> list[tuple[str, int, int]]:
    """Dönem başına (etiket, açılan görev, tamamlanan görev); çizgiler ayrışıyorsa iş birikiyordur."""
    created = _count_by_period(sess, Task.created_at, start, end, fmt, project_id, done_only=False)
    completed = _count_by_period(sess, Task.completed_at, start, end, fmt, project_id, done_only=True)
    return [(label_fn(k), created.get(k, 0), completed.get(k, 0)) for k in all_keys]


def _count_by_period(
    sess: Any, column: Any, start: datetime, end: datetime, fmt: str, project_id: int | None, done_only: bool
) -> dict[str, int]:
    period_col = func.strftime(fmt, column).label("period")
    stmt = (
        select(period_col, func.count(Task.id).label("cnt"))
        .where(column >= start)
        .where(column <= end)
        .group_by(period_col)
    )
    if done_only:
        stmt = stmt.where(Task.status == TaskStatus.DONE.value)
    if project_id is not None:
        stmt = stmt.where(Task.project_id == project_id)
    return {row.period: row.cnt for row in sess.execute(stmt)}


def avg_completion_days(sess: Any, start: datetime, end: datetime, project_id: int | None) -> float:
    """Dönemde biten görevlerin oluşturulmadan tamamlanmaya geçen ortalama süresi (gün)."""
    stmt = (
        select(Task.created_at, Task.completed_at)
        .where(Task.status == TaskStatus.DONE.value)
        .where(Task.completed_at >= start)
        .where(Task.completed_at <= end)
    )
    if project_id is not None:
        stmt = stmt.where(Task.project_id == project_id)
    spans = [
        (_naive_utc(row.completed_at) - _naive_utc(row.created_at)).total_seconds() / 86400
        for row in sess.execute(stmt)
        if row.created_at is not None and row.completed_at is not None
    ]
    if not spans:
        return 0.0
    return round(max(0.0, sum(spans) / len(spans)), 1)
