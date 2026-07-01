"""Manuel QVBoxLayout tabanlı satır listeleri için sürükle-bırak sıralama.

QListWidget'in InternalMove modunun eşdeğerini, elle çizilen satır widget'ları
(ör. NoteListWidget'taki _NoteRow, ProjectsPage'teki ProjectListItem) için
sağlar. Fikirler sayfası zaten QListWidget kullandığından bu yardımcıyı
gerektirmez (bkz. ideas_page.py — setDragDropMode ile çözülür).
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Optional

from PySide6.QtCore import QEvent, QMimeData, QObject, QPoint, Qt
from PySide6.QtGui import QDrag, QMouseEvent, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

_MIME_ROW_ID = "application/x-ptp-row-id"
_GHOST_OPACITY = 0.7


class DragReorderController(QObject):
    """Bir `QVBoxLayout` içindeki satırlara sürükle-bırak sıralama ekler.

    Kullanım: her satır widget'ı oluşturulduğunda `install(row)` çağrılır.
    Bırakma tamamlanınca güncel sıradaki id listesi `on_reorder`'a iletilir.
    """

    def __init__(
        self,
        layout: QVBoxLayout,
        row_id: Callable[[QWidget], Optional[int]],
        on_reorder: Callable[[list[int]], None],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._layout = layout
        self._row_id = row_id
        self._on_reorder = on_reorder
        self._press_pos: QPoint | None = None
        self._press_row: QWidget | None = None

    def install(self, row: QWidget) -> None:
        """Satırı sürüklenebilir + bırakma hedefi yapar."""
        row.setAcceptDrops(True)
        row.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802 (Qt API)
        if not isinstance(watched, QWidget):
            return False
        event_type = event.type()
        if event_type == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent):
            return self._on_mouse_press(watched, event)
        if event_type == QEvent.Type.MouseMove and isinstance(event, QMouseEvent):
            return self._on_mouse_move(watched, event)
        if event_type == QEvent.Type.DragEnter:
            return self._on_drag_enter(event)
        if event_type == QEvent.Type.Drop:
            return self._on_drop(watched, event)
        return False

    def _on_mouse_press(self, row: QWidget, event: QMouseEvent) -> bool:
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.position().toPoint()
            self._press_row = row
        return False  # tıklama/seçim davranışı (ör. clicked sinyali) bozulmasın

    def _on_mouse_move(self, row: QWidget, event: QMouseEvent) -> bool:
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return False
        if self._press_row is not row or self._press_pos is None:
            return False
        moved = (event.position().toPoint() - self._press_pos).manhattanLength()
        if moved < QApplication.startDragDistance():
            return False
        self._start_drag(row)
        return False

    def _start_drag(self, row: QWidget) -> None:
        row_id = self._row_id(row)
        if row_id is None:
            return
        drag = QDrag(row)
        mime = QMimeData()
        mime.setData(_MIME_ROW_ID, str(row_id).encode("utf-8"))
        drag.setMimeData(mime)
        drag.setPixmap(self._ghost_pixmap(row))
        drag.exec(Qt.DropAction.MoveAction)
        self._press_row = None
        self._press_pos = None

    @staticmethod
    def _ghost_pixmap(row: QWidget) -> QPixmap:
        # Sürüklenen satırın %70 opaklıkta kopyası — sürükleme hissiyatı (UX plan §5).
        source = row.grab()
        ghost = QPixmap(source.size())
        ghost.fill(Qt.GlobalColor.transparent)
        painter = QPainter(ghost)
        painter.setOpacity(_GHOST_OPACITY)
        painter.drawPixmap(0, 0, source)
        painter.end()
        return ghost

    def _on_drag_enter(self, event: QEvent) -> bool:
        mime = event.mimeData()  # type: ignore[attr-defined]
        if mime.hasFormat(_MIME_ROW_ID):
            event.acceptProposedAction()  # type: ignore[attr-defined]
            return True
        return False

    def _on_drop(self, target_row: QWidget, event: QEvent) -> bool:
        mime = event.mimeData()  # type: ignore[attr-defined]
        if not mime.hasFormat(_MIME_ROW_ID):
            return False
        dragged_id = int(bytes(mime.data(_MIME_ROW_ID)).decode("utf-8"))
        target_id = self._row_id(target_row)
        if target_id is None or dragged_id == target_id:
            return False
        dragged_row = self._find_row(dragged_id)
        if dragged_row is None:
            return False
        insert_after = self._drop_in_lower_half(target_row, event)
        self._move_row(dragged_row, target_row, insert_after)
        event.acceptProposedAction()  # type: ignore[attr-defined]
        self._on_reorder(self._current_row_ids())
        return True

    @staticmethod
    def _drop_in_lower_half(target_row: QWidget, event: QEvent) -> bool:
        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()  # type: ignore[attr-defined]
        return pos.y() > target_row.height() / 2

    def _find_row(self, row_id: int) -> QWidget | None:
        for index in range(self._layout.count()):
            widget = self._layout.itemAt(index).widget()
            if widget is not None and self._row_id(widget) == row_id:
                return widget
        return None

    def _move_row(self, dragged_row: QWidget, target_row: QWidget, insert_after: bool) -> None:
        self._layout.removeWidget(dragged_row)
        target_index = self._layout.indexOf(target_row)
        insert_index = target_index + 1 if insert_after else target_index
        self._layout.insertWidget(insert_index, dragged_row)

    def _current_row_ids(self) -> list[int]:
        ids: list[int] = []
        for index in range(self._layout.count()):
            widget = self._layout.itemAt(index).widget()
            if widget is None:
                continue
            row_id = self._row_id(widget)
            if row_id is not None:
                ids.append(row_id)
        return ids
