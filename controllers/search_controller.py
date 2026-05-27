"""
SearchController - UI ile SearchService arasındaki haberleşmeyi sağlar.
"""
import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from services.search_service import SearchService

logger = logging.getLogger(__name__)


class SearchController(QObject):
    # Dict dönecek {"projects": [...], "tasks": [...], "ideas": [...]}
    search_completed = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, service: SearchService) -> None:
        super().__init__()
        self._service = service

    def perform_search(self, query: str) -> None:
        try:
            results = self._service.search_all(query)
            self.search_completed.emit(results)
        except Exception as e:
            logger.exception("Arama sırasında hata: %s", e)
            self.error_occurred.emit(f"Arama başarısız: {e}")
