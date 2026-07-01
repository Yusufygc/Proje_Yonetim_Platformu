"""
Görev tamamlanma analitiği — günlük/haftalık/aylık/yıllık dönem bazlı
istatistik ve grafik verisi üretir.
"""
from __future__ import annotations

import logging
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable

from sqlalchemy import func, select

from domain.enums.task_status import TaskStatus
from domain.models.project import Project
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

_MONTHS_TR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def _fmt_daily(key: str) -> str:
    d = date.fromisoformat(key)
    return f"{d.day} {_MONTHS_TR[d.month - 1]}"


def _fmt_weekly(key: str) -> str:
    year, week = key.split("-W")
    return f"H{week}/{year[2:]}"


def _fmt_monthly(key: str) -> str:
    year, month = key.split("-")
    return f"{_MONTHS_TR[int(month) - 1]} {year}"


def _fmt_yearly(key: str) -> str:
    return key


class AnalyticsService:
    """Dönem bazlı görev tamamlanma analitiği üretir."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_analytics(self, period: str, project_id: int | None) -> dict[str, Any]:
        start_dt, all_keys, fmt, label_fn = self._resolve_range(period)
        end_dt = datetime.now(timezone.utc)
        with self._db.session() as sess:
            time_series = self._time_series(sess, start_dt, end_dt, fmt, all_keys, label_fn, project_id)
            priority_dist = self._priority_dist(sess, start_dt, end_dt, project_id)
            project_dist = self._project_dist(sess, start_dt, end_dt, project_id)
            kpis = self._kpis(sess, start_dt, end_dt, project_id, time_series)
        return {
            "time_series": time_series,
            "priority_distribution": priority_dist,
            "project_distribution": project_dist,
            "kpis": kpis,
            "period": period,
            "project_id": project_id,
        }

    def _resolve_range(self, period: str) -> tuple[datetime, list[str], str, Callable[[str], str]]:
        now = datetime.now(timezone.utc)
        today = now.date()
        if period == "daily":
            start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc) - timedelta(days=29)
            keys = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
            return start, keys, "%Y-%m-%d", _fmt_daily
        if period == "weekly":
            start = now - timedelta(weeks=11)
            keys = self._weekly_keys(today, 12)
            return start, keys, "%Y-W%W", _fmt_weekly
        if period == "monthly":
            start = self._months_ago(today, 11)
            keys = self._monthly_keys(today, 12)
            return start, keys, "%Y-%m", _fmt_monthly
        # yearly (default)
        start = datetime(today.year - 4, 1, 1, tzinfo=timezone.utc)
        keys = [str(today.year - i) for i in range(4, -1, -1)]
        return start, keys, "%Y", _fmt_yearly

    def _time_series(
        self,
        sess: Any,
        start: datetime,
        end: datetime,
        fmt: str,
        all_keys: list[str],
        label_fn: Callable[[str], str],
        project_id: int | None,
    ) -> list[tuple[str, int]]:
        period_col = func.strftime(fmt, Task.completed_at).label("period")
        stmt = (
            select(period_col, func.count(Task.id).label("cnt"))
            .where(Task.status == TaskStatus.DONE.value)
            .where(Task.completed_at >= start)
            .where(Task.completed_at <= end)
            .group_by(period_col)
        )
        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)
        raw = {row.period: row.cnt for row in sess.execute(stmt)}
        return [(label_fn(k), raw.get(k, 0)) for k in all_keys]

    def _priority_dist(
        self, sess: Any, start: datetime, end: datetime, project_id: int | None
    ) -> dict[str, int]:
        stmt = (
            select(Task.priority, func.count(Task.id))
            .where(Task.status == TaskStatus.DONE.value)
            .where(Task.completed_at >= start)
            .where(Task.completed_at <= end)
            .group_by(Task.priority)
        )
        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)
        # Öncelik enum değeri (LOW/MEDIUM/HIGH/CRITICAL) döner; ekranda gösterilecek
        # Türkçe/İngilizce etiket UI katmanında tr() ile üretilir (RULES.md katman ayrımı).
        return {row[0]: row[1] for row in sess.execute(stmt)}

    def _project_dist(
        self, sess: Any, start: datetime, end: datetime, project_id: int | None
    ) -> list[tuple[str, int]]:
        stmt = (
            select(Project.title, func.count(Task.id).label("cnt"))
            .join(Project, Task.project_id == Project.id)
            .where(Task.status == TaskStatus.DONE.value)
            .where(Task.completed_at >= start)
            .where(Task.completed_at <= end)
            .group_by(Project.id)
            .order_by(func.count(Task.id).desc())
            .limit(8)
        )
        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)
        return [(row.title, row.cnt) for row in sess.execute(stmt)]

    def _kpis(
        self,
        sess: Any,
        start: datetime,
        end: datetime,
        project_id: int | None,
        time_series: list[tuple[str, int]],
    ) -> dict[str, Any]:
        total_completed = self._total_completed(sess, start, end, project_id)
        best_label, best_count = self._best_period(time_series)
        return {
            "total_completed": total_completed,
            "completion_rate": self._completion_rate(sess, start, end, project_id),
            "streak_days": self._streak_days(sess, project_id),
            "best_period_label": best_label,
            "best_period_count": best_count,
            "on_time_rate": self._on_time_rate(sess, start, end, project_id),
        }

    def _total_completed(
        self, sess: Any, start: datetime, end: datetime, project_id: int | None
    ) -> int:
        stmt = (
            select(func.count(Task.id))
            .where(Task.status == TaskStatus.DONE.value)
            .where(Task.completed_at >= start)
            .where(Task.completed_at <= end)
        )
        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)
        return sess.scalar(stmt) or 0

    def _completion_rate(
        self, sess: Any, start: datetime, end: datetime, project_id: int | None
    ) -> float:
        done = self._total_completed(sess, start, end, project_id)
        open_stmt = select(func.count(Task.id)).where(
            Task.status.not_in([TaskStatus.DONE.value, TaskStatus.CANCELLED.value])
        )
        if project_id is not None:
            open_stmt = open_stmt.where(Task.project_id == project_id)
        open_count = sess.scalar(open_stmt) or 0
        total = done + open_count
        return round(done / total * 100, 1) if total else 0.0

    def _streak_days(self, sess: Any, project_id: int | None) -> int:
        stmt = select(func.strftime("%Y-%m-%d", Task.completed_at)).where(
            Task.status == TaskStatus.DONE.value
        ).where(Task.completed_at.is_not(None))
        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)
        done_dates = {date.fromisoformat(r[0]) for r in sess.execute(stmt) if r[0]}
        today = date.today()
        streak = 0
        current = today
        while current in done_dates:
            streak += 1
            current -= timedelta(days=1)
        return streak

    def _on_time_rate(
        self, sess: Any, start: datetime, end: datetime, project_id: int | None
    ) -> float:
        base = (
            select(Task.due_date, Task.completed_at)
            .where(Task.status == TaskStatus.DONE.value)
            .where(Task.completed_at >= start)
            .where(Task.completed_at <= end)
            .where(Task.due_date.is_not(None))
        )
        if project_id is not None:
            base = base.where(Task.project_id == project_id)
        rows = list(sess.execute(base))
        if not rows:
            return 0.0
        on_time = sum(1 for r in rows if r.completed_at and r.completed_at.date() <= r.due_date)
        return round(on_time / len(rows) * 100, 1)

    @staticmethod
    def _best_period(time_series: list[tuple[str, int]]) -> tuple[str, int]:
        if not time_series:
            return "—", 0
        label, count = max(time_series, key=lambda x: x[1])
        return label, count

    @staticmethod
    def _weekly_keys(today: date, n: int) -> list[str]:
        keys = []
        for i in range(n - 1, -1, -1):
            d = today - timedelta(weeks=i)
            keys.append(d.strftime("%Y-W%W"))
        return keys

    @staticmethod
    def _monthly_keys(today: date, n: int) -> list[str]:
        keys = []
        year, month = today.year, today.month
        for i in range(n - 1, -1, -1):
            m = month - i
            y = year
            while m <= 0:
                m += 12
                y -= 1
            keys.append(f"{y}-{m:02d}")
        return keys

    @staticmethod
    def _months_ago(today: date, n: int) -> datetime:
        month = today.month - n
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        day = min(today.day, monthrange(year, month)[1])
        return datetime(year, month, day, tzinfo=timezone.utc)
