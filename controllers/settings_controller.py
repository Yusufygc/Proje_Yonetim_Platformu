"""
Settings Controller - Ayarlar sayfasındaki dışa aktarma ve yedekleme işlemlerini yönetir.
"""
import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from services.export_service import ExportService

logger = logging.getLogger(__name__)


class SettingsController(QObject):
    backup_completed = Signal(str)
    export_completed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, service: ExportService) -> None:
        super().__init__()
        self._service = service

    def backup_database(self, target_path: str) -> None:
        try:
            self._service.backup_database(target_path)
            self.backup_completed.emit(target_path)
        except Exception as e:
            logger.exception("Veritabanı yedeklenirken hata oluştu.")
            self.error_occurred.emit(f"Yedekleme hatası: {e}")

    def export_to_json(self, target_path: str) -> None:
        try:
            self._service.export_to_json(target_path)
            self.export_completed.emit(target_path)
        except Exception as e:
            logger.exception("JSON dışa aktarılırken hata oluştu.")
            self.error_occurred.emit(f"Dışa aktarma hatası: {e}")
