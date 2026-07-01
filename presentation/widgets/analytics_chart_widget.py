"""
Reusable QChartView wrapper — bar ve pie grafikleri için tek widget.
"""
from __future__ import annotations

from PySide6.QtCharts import QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QPieSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from presentation.utils.i18n import tr

# Renkler ve varsayılan etiketler öncelik enum değeriyle (LOW/MEDIUM/HIGH/CRITICAL)
# eşleşir; analytics_service.py priority_distribution'ı bu değerlerle döndürür.
# Anahtar önceden çevrilmiş bir metin olsaydı dil değişince renk eşleşmesi bozulurdu.
_PRIORITY_COLORS = {
    "LOW": "#4CAF50",
    "MEDIUM": "#2196F3",
    "HIGH": "#FF9800",
    "CRITICAL": "#F44336",
}
_PRIORITY_LABEL_DEFAULTS = {
    "LOW": "Düşük",  # l10n: data — tr() ile set_pie_chart'ta tüketilir
    "MEDIUM": "Orta",
    "HIGH": "Yüksek",  # l10n: data
    "CRITICAL": "Kritik",  # l10n: data
}

_PIE_PALETTE = ["#5C6BC0", "#42A5F5", "#26C6DA", "#66BB6A", "#FFA726", "#EF5350"]


class AnalyticsChartWidget(QWidget):
    """Bar veya pasta grafiği gösteren yeniden kullanılabilir widget."""

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._title = title
        self._chart = QChart()
        self._chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self._chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self._chart.setMargins(_zero_margins())
        self._view = QChartView(self._chart, parent=self)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._view)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_bar_chart(
        self,
        labels: list[str],
        values: list[int],
        color: str = "#5C6BC0",
        show_legend: bool = False,
    ) -> None:
        self._chart.setTitle(self._title)
        self._chart.removeAllSeries()
        for ax in self._chart.axes():
            self._chart.removeAxis(ax)
        bar_set = QBarSet(self._title)
        bar_set.setColor(QColor(color))
        for v in values:
            bar_set.append(v)
        series = QBarSeries()
        series.append(bar_set)
        self._chart.addSeries(series)
        x_axis = QBarCategoryAxis()
        x_axis.append(labels)
        self._chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(x_axis)
        y_axis = QValueAxis()
        y_axis.setMin(0)
        y_axis.setMax(max(values) + 1 if values else 5)
        y_axis.setTickCount(min(max(values) + 2, 6) if values else 5)
        y_axis.setLabelFormat("%d")
        self._chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(y_axis)
        self._chart.legend().setVisible(show_legend)

    def set_pie_chart(self, data: dict[str, int]) -> None:
        self._chart.setTitle(self._title)
        self._chart.removeAllSeries()
        series = QPieSeries()
        for i, (key, value) in enumerate(data.items()):
            if value == 0:
                continue
            color = _PRIORITY_COLORS.get(key, _PIE_PALETTE[i % len(_PIE_PALETTE)])
            label = tr(f"analytics_priority_{key.lower()}", _PRIORITY_LABEL_DEFAULTS.get(key, key))
            slc = series.append(f"{label}\n({value})", value)
            slc.setColor(QColor(color))
        series.setHoleSize(0.35)
        self._chart.addSeries(series)
        self._chart.legend().setVisible(True)

    def set_horizontal_bar_chart(
        self, labels: list[str], values: list[int], color: str = "#42A5F5"
    ) -> None:
        self._chart.setTitle(self._title)
        self._chart.removeAllSeries()
        for ax in self._chart.axes():
            self._chart.removeAxis(ax)
        bar_set = QBarSet(self._title)
        bar_set.setColor(QColor(color))
        for v in values:
            bar_set.append(v)
        from PySide6.QtCharts import QHorizontalBarSeries
        series = QHorizontalBarSeries()
        series.append(bar_set)
        self._chart.addSeries(series)
        y_axis = QBarCategoryAxis()
        y_axis.append(labels)
        self._chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(y_axis)
        x_axis = QValueAxis()
        x_axis.setMin(0)
        x_axis.setMax(max(values) + 1 if values else 5)
        x_axis.setLabelFormat("%d")
        self._chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(x_axis)
        self._chart.legend().setVisible(False)

    def apply_theme(self, dark: bool, surface_color: str, text_color: str) -> None:
        """Qt'nin hazır koyu/açık temasını uygular, ardından arka plan/metin
        renklerini uygulamanın gerçek ThemeManager paletiyle senkronlar —
        aksi halde grafik dark modda bile beyaz zeminde kalır."""
        theme = QChart.ChartTheme.ChartThemeDark if dark else QChart.ChartTheme.ChartThemeLight
        self._chart.setTheme(theme)
        surface = QColor(surface_color)
        text = QColor(text_color)
        self._chart.setBackgroundBrush(surface)
        self._chart.setBackgroundPen(surface)
        self._chart.setTitleBrush(text)
        self._chart.legend().setLabelColor(text)
        for axis in self._chart.axes():
            axis.setLabelsColor(text)
            axis.setTitleBrush(text)
        self._view.setBackgroundBrush(surface)

    def clear(self) -> None:
        self._chart.setTitle("")
        self._chart.removeAllSeries()
        for ax in self._chart.axes():
            self._chart.removeAxis(ax)

    def show_empty(self, message: str = "Veri yok") -> None:
        self.clear()
        self._chart.setTitle(message)


def _zero_margins() -> "QMargins":
    from PySide6.QtCore import QMargins
    return QMargins(4, 4, 4, 4)
