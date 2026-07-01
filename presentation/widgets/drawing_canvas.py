"""Fare ile serbest çizim tuvali widget'ı ve araç çubuğu."""
from __future__ import annotations

import base64

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QToolButton,
    QWidget,
)

from presentation.utils.i18n import tr

_Stroke = tuple[QPainterPath, QColor, int]


class DrawingCanvas(QWidget):
    """Fare/kalem ile serbest çizim destekleyen beyaz zemin tuval."""

    drawing_modified = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._strokes: list[_Stroke] = []
        self._current_path: QPainterPath | None = None
        self._pen_color = QColor("#222222")
        self._pen_width = 3
        self._eraser_mode = False
        self._background: QPixmap | None = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(300)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setStyleSheet("background: white; border-radius: 6px;")

    # ── Çizim olayları ────────────────────────────────────────────────────────

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._current_path = QPainterPath()
            self._current_path.moveTo(event.position())

    def mouseMoveEvent(self, event) -> None:
        if self._current_path is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._current_path.lineTo(event.position())
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._current_path is None:
            return
        color = QColor("white") if self._eraser_mode else QColor(self._pen_color)
        width = self._pen_width * (8 if self._eraser_mode else 1)
        self._strokes.append((self._current_path, color, width))
        self._current_path = None
        self.update()
        self.drawing_modified.emit()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("white"))
        if self._background:
            painter.drawPixmap(
                0, 0,
                self._background.scaled(
                    self.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ),
            )
        for path, color, width in self._strokes:
            pen = QPen(color, width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)
        if self._current_path is not None:
            color = QColor("white") if self._eraser_mode else self._pen_color
            width = self._pen_width * (8 if self._eraser_mode else 1)
            pen = QPen(color, width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(self._current_path)
        painter.end()

    # ── Kontrol metodları ─────────────────────────────────────────────────────

    def set_pen_color(self, color: QColor) -> None:
        self._pen_color = color

    def set_pen_width(self, width: int) -> None:
        self._pen_width = width

    def set_eraser_mode(self, enabled: bool) -> None:
        self._eraser_mode = enabled
        self.setCursor(
            Qt.CursorShape.ArrowCursor if enabled else Qt.CursorShape.CrossCursor
        )

    def clear_canvas(self) -> None:
        self._strokes.clear()
        self._background = None
        self.update()

    def is_empty(self) -> bool:
        return not self._strokes and self._background is None

    # ── Kayıt / yükleme ──────────────────────────────────────────────────────

    def to_base64_png(self) -> str:
        size = self.size()
        if size.isEmpty():
            return ""
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.white)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._background:
            painter.drawPixmap(
                0, 0,
                self._background.scaled(
                    size,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ),
            )
        for path, color, width in self._strokes:
            pen = QPen(color, width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)
        painter.end()
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buf, "PNG")
        buf.close()
        return base64.b64encode(bytes(ba)).decode("ascii")

    def load_from_base64(self, data: str) -> None:
        if not data:
            return
        raw = base64.b64decode(data.encode("ascii"))
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(raw))
        self._background = pixmap
        self._strokes.clear()
        self.update()


class DrawingToolbar(QWidget):
    """Çizim tuvali için araç çubuğu: renk, kalınlık, silgi, temizle."""

    def __init__(self, canvas: DrawingCanvas, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._canvas = canvas
        self._current_color = QColor("#222222")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        self._color_btn = self._make_color_btn()

        lbl = QLabel(tr("drawing_toolbar_width_label", "Kalınlık:"), parent=self)
        lbl.setProperty("cssClass", "text-muted")

        self._width_slider = QSlider(Qt.Orientation.Horizontal, parent=self)
        self._width_slider.setRange(1, 20)
        self._width_slider.setValue(3)
        self._width_slider.setFixedWidth(100)
        self._width_slider.setToolTip(tr("drawing_toolbar_width_tooltip", "Kalem kalınlığı"))
        self._width_slider.valueChanged.connect(self._canvas.set_pen_width)

        sep = QFrame(parent=self)
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedSize(1, 20)

        self._eraser_btn = self._make_eraser_btn()
        clear_btn = self._make_clear_btn()

        for w in [self._color_btn, lbl, self._width_slider, sep, self._eraser_btn, clear_btn]:
            layout.addWidget(w)
        layout.addStretch()

    def _make_color_btn(self) -> QPushButton:
        btn = QPushButton("●", parent=self)
        btn.setToolTip(tr("drawing_toolbar_pen_color_tooltip", "Kalem rengi seç"))
        btn.setFixedSize(28, 26)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            f"QPushButton {{ color: {self._current_color.name()}; border: 1px solid rgba(128,128,128,0.4);"
            f" border-radius: 4px; background: transparent; font-size: 18px; }}"
            f" QPushButton:hover {{ background: rgba(128,128,128,0.1); }}"
        )
        btn.clicked.connect(self._pick_color)
        return btn

    def _make_eraser_btn(self) -> QToolButton:
        btn = QToolButton(parent=self)
        btn.setText("◻ Silgi")
        btn.setCheckable(True)
        btn.setFixedHeight(26)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QToolButton { border: none; border-radius: 4px; background: transparent; padding: 0 6px; }"
            " QToolButton:hover { background: rgba(128,128,128,0.15); }"
            " QToolButton:checked { background: rgba(244,67,54,0.2); color: #f44336; }"
        )
        btn.toggled.connect(self._canvas.set_eraser_mode)
        return btn

    def _make_clear_btn(self) -> QPushButton:
        btn = QPushButton("Temizle", parent=self)
        btn.setFixedHeight(26)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { border: 1px solid rgba(128,128,128,0.4); border-radius: 4px;"
            " background: transparent; padding: 0 8px; }"
            " QPushButton:hover { background: rgba(244,67,54,0.1); color: #f44336;"
            " border-color: #f44336; }"
        )
        btn.clicked.connect(self._canvas.clear_canvas)
        return btn

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(
            self._current_color, parent=self, title=tr("drawing_toolbar_pen_color_tooltip", "Kalem rengi seç")
        )
        if not color.isValid():
            return
        self._current_color = color
        self._canvas.set_pen_color(color)
        self._color_btn.setStyleSheet(
            f"QPushButton {{ color: {color.name()}; border: 1px solid rgba(128,128,128,0.4);"
            f" border-radius: 4px; background: transparent; font-size: 18px; }}"
            f" QPushButton:hover {{ background: rgba(128,128,128,0.1); }}"
        )
