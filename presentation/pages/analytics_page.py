"""
Analitik sayfası — tamamlanan görevlerin dönem bazlı analizi.
Düzen: üstte filtreler → KPI kartları → zaman serisi grafiği → alt satır (pie + proje bar).
"""
from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from controllers.analytics_controller import AnalyticsController
from controllers.project_controller import ProjectController
from core.managers.theme_manager import ThemeManager
from domain.models.project import Project
from presentation.dimensions import Shadow, Spacing
from presentation.utils.i18n import tr
from presentation.utils.ui_utils import apply_shadow
from presentation.widgets.analytics_chart_widget import AnalyticsChartWidget

logger = logging.getLogger(__name__)

_PERIODS = [
    ("daily", "analytics_period_daily", "Günlük"),  # l10n: data — tr() ile _build_header'da tüketilir
    ("weekly", "analytics_period_weekly", "Haftalık"),  # l10n: data
    ("monthly", "analytics_period_monthly", "Aylık"),  # l10n: data
    ("yearly", "analytics_period_yearly", "Yıllık"),  # l10n: data
]


class AnalyticsPage(QWidget):
    """Görev tamamlanma analitiği ana sayfası."""

    def __init__(
        self,
        parent: QWidget,
        controller: AnalyticsController,
        project_controller: ProjectController,
        theme: ThemeManager | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._project_controller = project_controller
        self._theme = theme or ThemeManager.instance()
        self._period_buttons: dict[str, QPushButton] = {}
        self._period_group = QButtonGroup(parent=self)
        self._project_combo: QComboBox | None = None
        self._project_id_map: dict[str, int | None] = {}
        self._kpi_labels: dict[str, QLabel] = {}
        self._time_chart: AnalyticsChartWidget | None = None
        self._pie_chart: AnalyticsChartWidget | None = None
        self._project_chart: AnalyticsChartWidget | None = None
        self._setup_ui()
        self._connect_signals()
        self._project_controller.load_projects()

    # ── UI kurulumu ──────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(Spacing.PAGE, Spacing.PAGE, Spacing.PAGE, Spacing.PAGE)
        outer.setSpacing(Spacing.XL)

        title = QLabel(tr("analytics_title", "Analitik"), parent=self)
        title.setProperty("cssClass", "title-large")
        outer.addWidget(title)

        outer.addWidget(self._build_header())
        outer.addLayout(self._build_kpi_row())

        scroll = QScrollArea(parent=self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        charts_container = self._build_charts_area()
        scroll.setWidget(charts_container)
        outer.addWidget(scroll, 1)

    def _build_header(self) -> QWidget:
        header = QWidget(parent=self)
        row = QHBoxLayout(header)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(Spacing.MD)
        for key, label_key, label_default in _PERIODS:
            btn = QPushButton(tr(label_key, label_default), parent=header)
            btn.setCheckable(True)
            btn.setProperty("cssClass", "btn-toggle")
            btn.setFixedHeight(32)
            self._period_group.addButton(btn)
            self._period_buttons[key] = btn
            row.addWidget(btn)
        self._period_buttons["weekly"].setChecked(True)
        row.addStretch()
        self._project_combo = QComboBox(parent=header)
        self._project_combo.setFixedHeight(32)
        self._project_combo.setMinimumWidth(160)
        self._project_combo.addItem(tr("analytics_all_projects", "Tüm Projeler"), userData=None)
        row.addWidget(self._project_combo)
        return header

    def _build_kpi_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(Spacing.XL)
        # l10n: data — bu tuple'ların *_default alanları tr() ile satır 122'de tüketilir
        kpi_defs = [
            ("total_completed", "analytics_kpi_total_completed", "Tamamlanan", "analytics_kpi_total_completed_desc", "Dönemde biten görev"),  # l10n: data
            ("completion_rate", "analytics_kpi_completion_rate", "Oran %", "analytics_kpi_completion_rate_desc", "Biten / (biten + açık)"),  # l10n: data
            ("streak_days", "analytics_kpi_streak_days", "Seri (gün)", "analytics_kpi_streak_days_desc", "Arka arkaya aktif gün"),  # l10n: data
            ("on_time_rate", "analytics_kpi_on_time_rate", "Zamanında %", "analytics_kpi_on_time_rate_desc", "Vadesi geçmeden biten"),  # l10n: data
        ]
        for key, label_key, label_default, desc_key, desc_default in kpi_defs:
            val_label = self._make_kpi_card(row, tr(label_key, label_default), tr(desc_key, desc_default))
            self._kpi_labels[key] = val_label
        return row

    def _make_kpi_card(self, layout: QHBoxLayout, title: str, description: str = "") -> QLabel:
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
        inner.addWidget(lbl_val)
        if description:
            lbl_desc = QLabel(description, parent=card)
            lbl_desc.setProperty("cssClass", "project-list-meta")
            inner.addWidget(lbl_desc)
        layout.addWidget(card)
        return lbl_val

    def _build_charts_area(self) -> QWidget:
        container = QWidget(parent=self)
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(Spacing.LG)

        self._time_chart = AnalyticsChartWidget(tr("analytics_chart_completed_title", "Tamamlanan Görev"), parent=container)
        self._time_chart.setMinimumHeight(170)
        vbox.addWidget(self._build_chart_panel(
            container,
            tr("analytics_panel_time_title", "Zaman İçinde Tamamlanan Görevler"),
            tr("analytics_panel_time_desc", "Seçilen dönemde her zaman biriminde biten görev adedi"),
            self._time_chart,
        ))

        bottom = QHBoxLayout()
        bottom.setSpacing(Spacing.LG)
        self._pie_chart = AnalyticsChartWidget(tr("analytics_panel_priority_title", "Öncelik Dağılımı"), parent=container)
        self._pie_chart.setMinimumHeight(150)
        bottom.addWidget(self._build_chart_panel(
            container,
            tr("analytics_panel_priority_title", "Öncelik Dağılımı"),
            tr("analytics_panel_priority_desc", "Tamamlanan görevlerin öncelik sınıflarına göre dağılımı"),
            self._pie_chart,
        ), 1)
        self._project_chart = AnalyticsChartWidget(tr("analytics_panel_project_title", "Proje Dağılımı"), parent=container)
        self._project_chart.setMinimumHeight(150)
        bottom.addWidget(self._build_chart_panel(
            container,
            tr("analytics_panel_project_title", "Proje Dağılımı"),
            tr("analytics_panel_project_desc", "Hangi projede kaç görev tamamlandığı"),
            self._project_chart,
        ), 1)
        vbox.addLayout(bottom)

        vbox.addWidget(self._build_time_totals_band(container))
        return container

    def _build_chart_panel(
        self, parent: QWidget, title: str, description: str, chart: AnalyticsChartWidget
    ) -> QFrame:
        panel = QFrame(parent=parent)
        panel.setProperty("cssClass", "panel")
        apply_shadow(panel, blur_radius=Shadow.CARD_BLUR, y_offset=Shadow.CARD_Y, alpha=Shadow.CARD_ALPHA)
        inner = QVBoxLayout(panel)
        inner.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        inner.setSpacing(Spacing.XS)
        lbl_title = QLabel(title, parent=panel)
        lbl_title.setProperty("cssClass", "section-header")
        inner.addWidget(lbl_title)
        lbl_desc = QLabel(description, parent=panel)
        lbl_desc.setProperty("cssClass", "project-list-meta")
        inner.addWidget(lbl_desc)
        chart.setParent(panel)
        inner.addWidget(chart, 1)
        return panel

    def _build_time_totals_band(self, parent: QWidget) -> QFrame:
        band = QFrame(parent=parent)
        band.setProperty("cssClass", "panel")
        apply_shadow(band, blur_radius=Shadow.CARD_BLUR, y_offset=Shadow.CARD_Y, alpha=Shadow.CARD_ALPHA)
        row = QHBoxLayout(band)
        row.setContentsMargins(Spacing.XL, Spacing.MD, Spacing.XL, Spacing.MD)
        row.setSpacing(Spacing.XXXL)
        self._kpi_labels["estimated"] = self._add_inline_kpi(row, band, tr("analytics_kpi_estimated", "Tahmini Süre"))
        self._kpi_labels["spent"] = self._add_inline_kpi(row, band, tr("analytics_kpi_spent", "Harcanan Süre"))
        self._kpi_labels["best_period"] = self._add_inline_kpi(row, band, tr("analytics_kpi_best_period", "En İyi Dönem"))
        row.addStretch()
        return band

    @staticmethod
    def _add_inline_kpi(layout: QHBoxLayout, parent: QWidget, title: str) -> QLabel:
        grp = QVBoxLayout()
        grp.setSpacing(2)
        t = QLabel(title, parent=parent)
        t.setProperty("cssClass", "stat-card-title")
        grp.addWidget(t)
        v = QLabel("—", parent=parent)
        v.setProperty("cssClass", "section-header")
        grp.addWidget(v)
        layout.addLayout(grp)
        return v

    # ── Sinyal bağlantıları ──────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._controller.analytics_loaded.connect(self._on_analytics_loaded)
        self._controller.error_occurred.connect(self._on_error)
        self._project_controller.projects_loaded.connect(self._on_projects_loaded)
        self._theme.theme_changed.connect(self._on_theme_changed)
        for key, btn in self._period_buttons.items():
            btn.toggled.connect(lambda checked, k=key: self._on_period_toggled(checked, k))
        if self._project_combo:
            self._project_combo.currentIndexChanged.connect(self._on_project_changed)

    def _on_period_toggled(self, checked: bool, key: str) -> None:
        if checked:
            self._load_data()

    def _on_project_changed(self, _index: int) -> None:
        self._load_data()

    def _load_data(self) -> None:
        period = next((k for k, btn in self._period_buttons.items() if btn.isChecked()), "weekly")
        project_id: int | None = None
        if self._project_combo:
            project_id = self._project_combo.currentData()
        self._controller.load_analytics(period, project_id)

    def _on_projects_loaded(self, projects: list[Project]) -> None:
        if not self._project_combo:
            return
        self._project_combo.blockSignals(True)
        current = self._project_combo.currentData()
        self._project_combo.clear()
        self._project_combo.addItem(tr("analytics_all_projects", "Tüm Projeler"), userData=None)
        for p in projects:
            self._project_combo.addItem(p.title, userData=p.id)
        idx = self._project_combo.findData(current)
        self._project_combo.setCurrentIndex(max(idx, 0))
        self._project_combo.blockSignals(False)
        self._load_data()

    def _on_analytics_loaded(self, data: dict[str, Any]) -> None:
        self._update_kpi_cards(data.get("kpis", {}))
        ts = data.get("time_series", [])
        pd = data.get("priority_distribution", {})
        proj = data.get("project_distribution", [])
        self._update_time_chart(ts)
        self._update_pie_chart(pd)
        self._update_project_chart(proj)
        self._apply_chart_theme()

    def _update_kpi_cards(self, kpis: dict[str, Any]) -> None:
        self._kpi_labels["total_completed"].setText(str(kpis.get("total_completed", 0)))
        rate = kpis.get("completion_rate", 0.0)
        self._kpi_labels["completion_rate"].setText(f"{rate:.1f} %")
        self._kpi_labels["streak_days"].setText(str(kpis.get("streak_days", 0)))
        on_time = kpis.get("on_time_rate", 0.0)
        self._kpi_labels["on_time_rate"].setText(f"{on_time:.1f} %")
        est = kpis.get("estimated_minutes_total", 0)
        spent = kpis.get("spent_minutes_total", 0)
        self._kpi_labels["estimated"].setText(_fmt_minutes(est))
        self._kpi_labels["spent"].setText(_fmt_minutes(spent))
        best = kpis.get("best_period_label", "—")
        best_cnt = kpis.get("best_period_count", 0)
        self._kpi_labels["best_period"].setText(f"{best} ({best_cnt})")

    def _update_time_chart(self, ts: list[tuple[str, int]]) -> None:
        if not self._time_chart:
            return
        if not ts:
            self._time_chart.show_empty()
            return
        labels = [t[0] for t in ts]
        values = [t[1] for t in ts]
        self._time_chart.set_bar_chart(labels, values, color="#5C6BC0")

    def _update_pie_chart(self, pd: dict[str, int]) -> None:
        if not self._pie_chart:
            return
        if not any(pd.values()):
            self._pie_chart.show_empty()
            return
        self._pie_chart.set_pie_chart(pd)

    def _update_project_chart(self, proj: list[tuple[str, int]]) -> None:
        if not self._project_chart:
            return
        if not proj:
            self._project_chart.show_empty()
            return
        labels = [p[0] for p in proj]
        values = [p[1] for p in proj]
        self._project_chart.set_horizontal_bar_chart(labels, values, color="#42A5F5")

    def _apply_chart_theme(self) -> None:
        dark = self._theme.current_theme == "dark"
        surface = self._theme.color("surface")
        text = self._theme.color("text_primary")
        for chart in (self._time_chart, self._pie_chart, self._project_chart):
            if chart:
                chart.apply_theme(dark, surface, text)

    def _on_theme_changed(self, _theme: str) -> None:
        self._apply_chart_theme()

    def _on_error(self, message: str) -> None:
        logger.error("Analitik sayfası hatası: %s", message)  # l10n: log


def _fmt_minutes(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes} dk"
    h, m = divmod(minutes, 60)
    return f"{h}s {m}dk" if m else f"{h}s"
