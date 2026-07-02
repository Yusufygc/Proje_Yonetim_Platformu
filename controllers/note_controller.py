import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from core.exceptions.base_exception import AppBaseException
from core.workers.worker import Worker
from domain.models.note import Note
from services.note_service import NoteService

logger = logging.getLogger(__name__)


class NoteController(QObject):
    """Proje Notları için olay ve sinyal yönetimi."""

    notes_loaded = Signal(list)
    note_created = Signal(object)
    note_updated = Signal(object)
    note_deleted = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, service: NoteService) -> None:
        super().__init__()
        self._service = service

    def load_project_notes(self, project_id: int) -> None:
        def _fetch() -> list[Note]:
            return self._service.get_project_notes(project_id)

        def _on_error(err: str) -> None:
            logger.error("Notlar yüklenemedi: %s", err)
            self.error_occurred.emit(str(err))

        worker = Worker(_fetch)
        worker.signals.result.connect(self.notes_loaded.emit)
        worker.signals.error.connect(_on_error)
        worker.start()

    def create_note(self, project_id: int, title: str, body: str, **kwargs: Any) -> None:
        try:
            note = self._service.create_note(project_id, title, body, **kwargs)
            self.note_created.emit(note)
        except (AppBaseException, ValueError) as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Not oluşturulamadı: %s", exc)
            self.error_occurred.emit("Not oluşturulurken hata oluştu.")

    def update_note(self, note_id: int, **kwargs: Any) -> None:
        try:
            note = self._service.update_note(note_id, **kwargs)
            self.note_updated.emit(note)
        except (AppBaseException, ValueError) as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Not güncellenemedi: %s", exc)
            self.error_occurred.emit("Not güncellenirken hata oluştu.")

    def delete_note(self, note_id: int) -> None:
        try:
            self._service.delete_note(note_id)
            self.note_deleted.emit(note_id)
        except Exception as exc:
            logger.error("Not silinemedi: %s", exc)
            self.error_occurred.emit("Not silinirken hata oluştu.")

    def get_note_sync(self, note_id: int) -> Optional[Note]:
        return self._service.get_note(note_id)

    def reorder(self, ordered_ids: list[int]) -> None:
        try:
            self._service.reorder(ordered_ids)
        except Exception as exc:
            logger.error("Notlar yeniden siralanamadi: %s", exc)
            self.error_occurred.emit("Notlar sıralanırken hata oluştu.")
