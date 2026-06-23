"""
Dashboard sayfası — Seçenek A düzeni:
4 metrik kart + sol sütun (öncelikli görevler, tıkanan projeler)
+ sağ sütun (hızlı fikir, son fikirler). QListWidget yok, kaydırma yok.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from controllers.dashboard_controller import DashboardController
from controllers.idea_controller import IdeaController
from core.events.event_bus import EventBus
from core.managers.theme_manager import ThemeManager
from presentation.dimensions import Shadow, Spacing
from presentation.utils.i18n import tr
from presentation.utils.ui_utils import apply_shadow

_MAX_ROWS = 5


def _priority_label(value: str) -> str:
    return {
        "LOW": tr("priority_low", "Düşük"),
        "MEDIUM": tr("priority_medium", "Orta"),
        "HIGH": tr("priority_high", "Yüksek"),
        "CRITICAL": tr("priority_critical", "Kritik"),
    }.get(value, value)


def _status_label(value: str) -> str:
    return {
        "PLANNED": tr("status_planned", "Planlandı"),
        "ACTIVE": tr("status_active", "Aktif"),
        "ON_HOLD": tr("status_on_hold", "Beklemede"),
        "BLOCKED": tr("status_blocked", "Engellendi"),
        "COMPLETED": tr("status_completed", "Tamamlandı"),
        "CANCELLED": tr("status_cancelled", "İptal Edildi"),
    }.get(value, value)


def _idea_status_label(value: str) -> str:
    return {
        "RAW": tr("idea_status_raw", "Ham Fikir"),
        "REVIEWING": tr("idea_status_reviewing", "İnceleniyor"),
        "VALIDATING": tr("idea_status_validating", "Doğrulanıyor"),
        "CONVERTED": tr("idea_status_converted", "Dönüştürüldü"),
        "DEFERRED": tr("idea_status_deferred", "Ertelendi"),
        "REJECTED": tr("idea_status_rejected", "Reddedildi"),
    }.get(value, value)


class DashboardPage(QWidget):
    """Ana panel — görev öncelikli, kaydırma barı olmayan düzen."""

    def __init__(
        self,
        parent: QWidget,
        controller: DashboardController,
        idea_controller: IdeaController | None = None,
        theme: ThemeManager | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._idea_controller = idea_controller
        self._theme = theme or ThemeManager.instance()
        self._last_stats: dict = {}
        self._setup_ui()
        self._connect_signals()

    # ── UI kurulumu ──────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.PAGE, Spacing.PAGE, Spacing.PAGE, Spacing.PAGE)
        root.setSpacing(Spacing.XL)

        title = QLabel(tr("dashboard_title", "Ana Panel"), parent=self)
        title.setProperty("cssClass", "title-large")
        root.addWidget(title)

        root.addLayout(self._build_stats_row())

        body = QHBoxLayout()
        body.setSpacing(Spacing.XXXL)
        body.addLayout(self._build_left_col(), 3)
        body.addLayout(self._build_right_col(), 2)
        root.addLayout(body, 1)

    def _build_stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(Spacing.XL)
        self._val_active = self._make_stat_card(row, tr("dashboard_stat_active", "Aktif Proje"))
        self._val_open_tasks = self._make_stat_card(row, tr("dashboard_stat_open_tasks", "Açık Görev"))
        self._val_blocked = self._make_stat_card(row, tr("dashboard_stat_blocked", "Tıkanan"), danger=True)
        self._val_raw_ideas = self._make_stat_card(row, tr("dashboard_stat_raw_ideas", "Ham Fikir"))
        return row

    def _make_stat_card(self, layout: QHBoxLayout, title: str, danger: bool = False) -> QLabel:
        card = QFrame(parent=self)
        card.setProperty("cssClass", "panel")
        apply_shadow(card, blur_radius=Shadow.CARD_BLUR, y_offset=Shadow.CARD_Y, alpha=Shadow.CARD_ALPHA)
        inner = QVBoxLayout(card)
        inner.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        inner.setSpacing(Spacing.XS)

        lbl_title = QLabel(title, parent=card)
        lbl_title.setProperty("cssClass", "stat-card-title")
        inner.addWidget(lbl_title)

        lbl_val = QLabel("—", parent=card)
        lbl_val.setProperty("cssClass", "stat-card-value")
        if danger:
            lbl_val.setProperty("cssClass", "stat-card-value-danger")
        inner.addWidget(lbl_val)

        layout.addWidget(card)
        return lbl_val

    def _build_left_col(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(Spacing.XL)

        self._tasks_frame, self._tasks_content = self._make_panel(
            tr("dashboard_high_priority_title", "Öncelikli Görevler")
        )
        col.addWidget(self._tasks_frame, 1)

        self._blocked_frame, self._blocked_content = self._make_panel(
            tr("dashboard_blocked_title", "Tıkanan / Riskli Projeler")
        )
        col.addWidget(self._blocked_frame, 1)
        return col

    def _build_right_col(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(Spacing.XL)
        col.addWidget(self._build_quick_idea_panel())
        self._ideas_frame, self._ideas_content = self._make_panel(
            tr("dashboard_ideas_title", "Son Fikirler")
        )
        col.addWidget(self._ideas_frame, 1)
        return col

    def _build_quick_idea_panel(self) -> QFrame:
        frame = QFrame(parent=self)
        frame.setProperty("cssClass", "panel")
        apply_shadow(frame, blur_radius=Shadow.CARD_BLUR, y_offset=Shadow.CARD_Y, alpha=Shadow.CARD_ALPHA)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.MD)

        lbl = QLabel(tr("dashboard_quick_idea_label", "Hızlı Fikir"), parent=frame)
        lbl.setProperty("cssClass", "section-header")
        layout.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(Spacing.MD)
        self._quick_idea_edit = QLineEdit(parent=frame)
        self._quick_idea_edit.setPlaceholderText(
            tr("dashboard_quick_idea_placeholder", "Aklındaki fikri yaz...")
        )
        self._quick_idea_edit.setFixedHeight(36)
        self._quick_idea_edit.returnPressed.connect(self._on_quick_idea)
        row.addWidget(self._quick_idea_edit, 1)

        btn = QPushButton(tr("dashboard_quick_idea_btn", "+ Kaydet"), parent=frame)
        btn.setFixedHeight(36)
        btn.setProperty("cssClass", "btn-primary")
        btn.clicked.connect(self._on_quick_idea)
        row.addWidget(btn)
        layout.addLayout(row)
        return frame

    def _make_panel(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        """Başlık + içerik alanı olan panel. İçerik layout'u döndürülür."""
        frame = QFrame(parent=self)
        frame.setProperty("cssClass", "panel")
        apply_shadow(frame, blur_radius=Shadow.CARD_BLUR, y_offset=Shadow.CARD_Y, alpha=Shadow.CARD_ALPHA)
        outer = QVBoxLayout(frame)
        outer.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        outer.setSpacing(Spacing.MD)

        lbl = QLabel(title, parent=frame)
        lbl.setProperty("cssClass", "section-header")
        outer.addWidget(lbl)

        sep = QFrame(parent=frame)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setProperty("cssClass", "divider")
        outer.addWidget(sep)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        outer.addLayout(content)
        outer.addStretch()
        return frame, content

    # ── Sinyal bağlantıları ──────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._controller.stats_loaded.connect(self._on_stats_loaded)
        self._theme.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, _: str) -> None:
        if self.isVisible() and self._last_stats:
            self._render(self._last_stats)

    def _on_stats_loaded(self, stats: dict) -> None:
        self._last_stats = stats
        self._render(stats)

    # ── Render ───────────────────────────────────────────────────────────────

    def _render(self, stats: dict) -> None:
        self._val_active.setText(str(stats.get("active_projects", 0)))
        self._val_open_tasks.setText(str(stats.get("open_tasks", 0)))
        self._val_raw_ideas.setText(str(stats.get("raw_ideas", 0)))

        blocked_count = stats.get("blocked_count", 0)
        self._val_blocked.setText(str(blocked_count))

        self._fill_tasks(stats.get("high_priority_tasks", []))
        self._fill_blocked(stats.get("blocked_projects", []))
        self._fill_ideas(stats.get("recent_ideas", []))

    def _fill_tasks(self, tasks: list) -> None:
        self._clear(self._tasks_content)
        if not tasks:
            self._tasks_content.addWidget(self._empty_row(tr("dashboard_no_tasks", "Yüksek öncelikli açık görev yok.")))
            return
        for t in tasks[:_MAX_ROWS]:
            self._tasks_content.addWidget(self._task_row(t))

    def _fill_blocked(self, projects: list) -> None:
        self._clear(self._blocked_content)
        if not projects:
            self._blocked_content.addWidget(self._empty_row(tr("dashboard_no_blocked", "Tıkanan veya riskli proje yok.")))
            return
        for p in projects[:_MAX_ROWS]:
            self._blocked_content.addWidget(self._blocked_row(p))

    def _fill_ideas(self, ideas: list) -> None:
        self._clear(self._ideas_content)
        if not ideas:
            self._ideas_content.addWidget(self._empty_row(tr("dashboard_no_ideas", "Henüz fikir yok.")))
            return
        for idea in ideas[:_MAX_ROWS]:
            self._ideas_content.addWidget(self._idea_row(idea))

    # ── Satır widget'ları ────────────────────────────────────────────────────

    def _task_row(self, task: dict) -> QWidget:
        priority = task.get("priority", "")
        is_critical = priority == "CRITICAL"

        row = QWidget(parent=self)
        row.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, Spacing.SM, 0, Spacing.SM)
        layout.setSpacing(Spacing.MD)

        badge = QLabel(_priority_label(priority), parent=row)
        badge.setFixedWidth(52)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        danger_color = self._theme.color("danger")
        warning_color = self._theme.color("warning")
        badge_color = danger_color if is_critical else warning_color
        badge.setStyleSheet(
            f"QLabel {{ color: {badge_color}; font-size: 11px; font-weight: 700; }}"
        )

        title = QLabel(task.get("title", ""), parent=row)
        title.setProperty("cssClass", "text-primary")
        title.setStyleSheet("QLabel { font-size: 13px; }")

        project = QLabel(f"[{task.get('project_name', '')}]", parent=row)
        project.setProperty("cssClass", "text-muted")
        project.setStyleSheet("QLabel { font-size: 11px; }")
        project.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(badge)
        layout.addWidget(title, 1)
        layout.addWidget(project)
        return row

    def _blocked_row(self, project: dict) -> QWidget:
        status = project.get("status", "")
        health = project.get("health", "")
        is_blocked = status == "BLOCKED"

        row = QWidget(parent=self)
        row.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, Spacing.SM, 0, Spacing.SM)
        layout.setSpacing(Spacing.MD)

        danger_color = self._theme.color("danger")
        warning_color = self._theme.color("warning")
        dot_color = danger_color if is_blocked else warning_color

        dot = QLabel("●", parent=row)
        dot.setFixedWidth(12)
        dot.setStyleSheet(f"QLabel {{ color: {dot_color}; font-size: 10px; }}")

        name = QLabel(project.get("name", ""), parent=row)
        name.setProperty("cssClass", "text-primary")
        name.setStyleSheet("QLabel { font-size: 13px; }")

        badge_text = _status_label(status) if is_blocked else tr("health_at_risk", "Riskli")
        badge = QLabel(badge_text, parent=row)
        badge.setStyleSheet(
            f"QLabel {{ color: {dot_color}; font-size: 11px; font-weight: 600; }}"
        )

        layout.addWidget(dot)
        layout.addWidget(name, 1)
        layout.addWidget(badge)
        return row

    def _idea_row(self, idea: dict) -> QWidget:
        row = QWidget(parent=self)
        row.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, Spacing.SM, 0, Spacing.SM)
        layout.setSpacing(Spacing.MD)

        title = QLabel(idea.get("title", ""), parent=row)
        title.setProperty("cssClass", "text-primary")
        title.setStyleSheet("QLabel { font-size: 13px; }")

        status_lbl = QLabel(_idea_status_label(idea.get("status", "")), parent=row)
        status_lbl.setProperty("cssClass", "text-muted")
        status_lbl.setStyleSheet("QLabel { font-size: 11px; }")
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(title, 1)
        layout.addWidget(status_lbl)
        return row

    def _empty_row(self, text: str) -> QLabel:
        lbl = QLabel(text, parent=self)
        lbl.setProperty("cssClass", "text-muted")
        lbl.setStyleSheet("QLabel { font-size: 12px; padding: 8px 0; }")
        return lbl

    # ── Yardımcılar ──────────────────────────────────────────────────────────

    @staticmethod
    def _clear(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _on_quick_idea(self) -> None:
        title = self._quick_idea_edit.text().strip()
        if not title:
            EventBus.instance().publish(
                "toast.show",
                message=tr("toast_idea_empty", "Fikir başlığı boş olamaz."),
                type_="warning",
            )
            return
        if self._idea_controller is None:
            return
        self._idea_controller.create_idea(title)
        self._quick_idea_edit.clear()
        self._controller.load_stats()
        EventBus.instance().publish(
            "toast.show",
            message=tr("toast_idea_saved", "Fikir kaydedildi."),
            type_="success",
        )

    def showEvent(self, event: object) -> None:
        super().showEvent(event)  # type: ignore[arg-type]
        self._controller.load_stats()
