"""QML Notlarım (Memo) Görünümü için ViewModel Köprüsü."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from domain.models.memo import Memo
from presentation.viewmodels.memo_list_model import MemoListModel

if TYPE_CHECKING:
    from app.di_container import DIContainer

logger = logging.getLogger(__name__)


class MemoViewModel(QObject):
    """Notlarım (Memo) modülünün QML kullanıcı arayüzü ile iş katmanı arasındaki köprüsü."""

    selectedMemoChanged = Signal()
    statsChanged = Signal()

    def __init__(self, container: DIContainer, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._container = container
        self._controller = container.memo_controller
        self._event_bus = container.event_bus

        self._memo_model = MemoListModel(parent=self)
        self._selected_memo_id: int = 0
        self._selected_memo_data: dict[str, Any] = {}
        self._memos_cache: list[Memo] = []

        self._connect_signals()
        self.loadMemos()

    def _connect_signals(self) -> None:
        self._controller.memos_loaded.connect(self._on_memos_loaded)
        self._controller.memo_created.connect(self._on_memo_created)
        self._controller.memo_updated.connect(self._on_memo_updated)
        self._controller.memo_deleted.connect(self._on_memo_deleted)

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(QObject, constant=True)
    def memoModel(self) -> MemoListModel:
        return self._memo_model

    @Property(int, notify=selectedMemoChanged)
    def selectedMemoId(self) -> int:
        return self._selected_memo_id

    @Property("QVariantMap", notify=selectedMemoChanged)
    def selectedMemo(self) -> dict[str, Any]:
        return self._selected_memo_data

    @Property(int, notify=statsChanged)
    def totalMemos(self) -> int:
        return len(self._memos_cache)

    # ── Controller Callbacks ────────────────────────────────────────────────

    def _on_memos_loaded(self, memos: list[Memo]) -> None:
        self._memos_cache = list(memos)
        self._memo_model.set_memos(memos)
        self.statsChanged.emit()

        if self._selected_memo_id == 0 and memos:
            self.selectMemo(memos[0].id)
        else:
            self._refresh_selected_memo()

    def _on_memo_created(self, memo: Memo) -> None:
        self.loadMemos()
        self.selectMemo(memo.id)
        self._event_bus.publish("toast.show", message="Yeni not oluşturuldu", type_="success")  # l10n: data

    def _on_memo_updated(self, memo: Memo) -> None:
        self.loadMemos()
        if self._selected_memo_id == memo.id:
            self._refresh_selected_memo()
        self._event_bus.publish("toast.show", message="Not kaydedildi", type_="success")  # l10n: data

    def _on_memo_deleted(self, memo_id: int) -> None:
        if self._selected_memo_id == memo_id:
            self._selected_memo_id = 0
            self._refresh_selected_memo()
        self.loadMemos()
        self._event_bus.publish("toast.show", message="Not silindi", type_="info")  # l10n: data

    # ── Public Slots ────────────────────────────────────────────────────────

    @Slot()
    def loadMemos(self) -> None:
        self._controller.load_all()

    @Slot(int)
    def selectMemo(self, memo_id: int) -> None:
        self._selected_memo_id = memo_id
        self._refresh_selected_memo()

    def _refresh_selected_memo(self) -> None:
        m = next((x for x in self._memos_cache if x.id == self._selected_memo_id), None)
        if not m:
            self._selected_memo_data = {}
        else:
            self._selected_memo_data = {
                "id": m.id,
                "title": m.title,
                "body": m.body or "",
                "drawingData": m.drawing_data or "",
                "updatedAt": m.updated_at.strftime("%d.%m.%Y %H:%M") if m.updated_at else "",
            }
        self.selectedMemoChanged.emit()

    @Slot()
    @Slot(str)
    def createMemo(self, title: str = "Yeni Not") -> None:
        t = title.strip() if title else "Yeni Not"  # l10n: data
        self._controller.create(title=t, body="", drawing_data=None)

    @Slot(int, str, str, str)
    def saveMemo(self, memo_id: int, title: str, body: str, drawing_data: str = "") -> None:
        t = title.strip() or "İsimsiz Not"  # l10n: data
        self._controller.update(
            memo_id,
            title=t,
            body=body,
            drawing_data=drawing_data if drawing_data else None,
        )

    @Slot(int)
    def deleteMemo(self, memo_id: int) -> None:
        self._controller.delete(memo_id)

    @Slot(str)
    def setSearchQuery(self, query: str) -> None:
        self._memo_model.setSearchQuery(query)
