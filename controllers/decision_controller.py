import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from domain.models.decision_record import DecisionRecord
from services.decision_service import DecisionService

logger = logging.getLogger(__name__)


class DecisionController(QObject):
    """Proje Kararları için olay ve sinyal yönetimi."""

    decisions_loaded = Signal(list)
    decision_created = Signal(object)
    decision_updated = Signal(object)
    decision_deleted = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, service: DecisionService) -> None:
        super().__init__()
        self._service = service

    def load_project_decisions(self, project_id: int) -> None:
        try:
            decisions = self._service.get_project_decisions(project_id)
            self.decisions_loaded.emit(decisions)
        except Exception as exc:
            logger.error("Kararlar yüklenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def create_decision(self, project_id: int, title: str, decision: str, **kwargs: Any) -> None:
        try:
            record = self._service.create_decision(project_id, title, decision, **kwargs)
            self.decision_created.emit(record)
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Karar oluşturulamadı: %s", exc)
            self.error_occurred.emit("Karar oluşturulurken hata oluştu.")

    def update_decision(self, decision_id: int, **kwargs: Any) -> None:
        try:
            record = self._service.update_decision(decision_id, **kwargs)
            self.decision_updated.emit(record)
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Karar güncellenemedi: %s", exc)
            self.error_occurred.emit("Karar güncellenirken hata oluştu.")

    def delete_decision(self, decision_id: int) -> None:
        try:
            self._service.delete_decision(decision_id)
            self.decision_deleted.emit(decision_id)
        except Exception as exc:
            logger.error("Karar silinemedi: %s", exc)
            self.error_occurred.emit("Karar silinirken hata oluştu.")

    def get_decision_sync(self, decision_id: int) -> Optional[DecisionRecord]:
        return self._service.get_decision(decision_id)
