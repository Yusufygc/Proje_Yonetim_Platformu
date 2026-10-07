"""
Settings Controller - Ayarlar sayfasındaki dışa aktarma işlemini yönetir.
"""
import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from services.export_service import ExportService

logger = logging.getLogger(__name__)


class SettingsController(QObject):
    export_completed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, service: ExportService) -> None:
        super().__init__()
        self._service = service

    def export_to_json(self, target_path: str) -> None:
        try:
            self._service.export_to_json(target_path)
            self.export_completed.emit(target_path)
        except Exception as e:
            logger.exception("JSON dışa aktarılırken hata oluştu.")
            self.error_occurred.emit(f"Dışa aktarma hatası: {e}")
