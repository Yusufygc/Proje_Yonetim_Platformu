"""QML Notlarım (Memo) Görünümü için ViewModel Köprüsü."""
from __future__ import annotations

import logging
import shutil
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QFileDialog

from app import config
from domain.models.memo import Memo
from presentation.viewmodels.error_reporting import forward_errors_to_toast
from presentation.viewmodels.memo_list_model import MemoListModel, _clean_body_markdown
from presentation.viewmodels.qt_properties import variant_map_property

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
        forward_errors_to_toast(self._event_bus, self._controller)
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

    @variant_map_property(notify=selectedMemoChanged)
    def selectedMemo(self) -> dict[str, Any]:
        return self._selected_memo_data

    @Property(int, notify=statsChanged)
    def totalMemos(self) -> int:
        return len(self._memos_cache)

    # ── Controller Callbacks ────────────────────────────────────────────────

    def _on_memos_loaded(self, memos: list[Memo]) -> None:
        for m in memos:
            if m.body:
                m.body = _clean_body_markdown(m.body)
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
                "body": _clean_body_markdown(m.body),
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

    # ── Resim İşlemleri (Görsel Yükleme & Pano) ──────────────────────────

    @Slot(result=str)
    def pickAndSaveImage(self) -> str:
        """Kullanıcının diskten bir görsel seçmesini sağlar, kopyalar ve dosya URL'si döndürür."""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Görsel Seç",  # l10n: data
            "",
            "Görseller (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;Tüm Dosyalar (*.*)",  # l10n: data
        )
        if not file_path:
            return ""
        return self._save_image_file(Path(file_path))

    @Slot(result=str)
    def saveClipboardImage(self) -> str:
        """Panoda (clipboard) bir görsel varsa bunu dosyaya kaydeder ve dosya URL'sini döndürür."""
        clipboard = QGuiApplication.clipboard()
        if not clipboard:
            return ""
        image = clipboard.image()
        if image.isNull():
            return ""

        config.MEMO_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"memo_img_{uuid.uuid4().hex[:12]}.png"
        target_path = config.MEMO_IMAGES_DIR / filename
        saved = image.save(str(target_path))
        if not saved:
            return ""
        return target_path.as_uri()

    @Slot(result=bool)
    def hasClipboardImage(self) -> bool:
        """Panoda görsel bulunup bulunmadığını kontrol eder."""
        clipboard = QGuiApplication.clipboard()
        if not clipboard:
            return False
        mime_data = clipboard.mimeData()
        return mime_data.hasImage() if mime_data else False

    def _save_image_file(self, src_path: Path) -> str:
        if not src_path.exists():
            return ""
        config.MEMO_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        ext = src_path.suffix.lower() or ".png"
        filename = f"memo_img_{uuid.uuid4().hex[:12]}{ext}"
        target_path = config.MEMO_IMAGES_DIR / filename
        try:
            shutil.copy2(src_path, target_path)
            return target_path.as_uri()
        except Exception as exc:
            logger.error("Görsel kopyalanamadı: %s", exc)  # l10n: log
            return ""

