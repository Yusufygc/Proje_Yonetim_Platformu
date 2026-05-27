"""
GUI thread'ini kilitlemeden uzun süren işlemleri arka planda çalıştıran Worker altyapısı.
16_SENIOR_MIMARI_STANDARTLAR.md gereği 50ms+ işlemler bu sınıf üzerinden yürütülür.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """Worker'ın sonuç ve hata bilgilerini UI thread'ine iletmek için sinyal seti."""

    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class AsyncWorker(QRunnable):
    """
    Verilen callable'ı QThreadPool aracılığıyla arka planda çalıştırır.

    Args:
        fn: Arka planda çalıştırılacak fonksiyon.
        *args: Fonksiyona iletilecek konumsal argümanlar.
        **kwargs: Fonksiyona iletilecek anahtar argümanlar.
    """

    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @Slot()
    def run(self) -> None:
        """QThreadPool tarafından çağrılır; sonucu sinyal ile UI'ya iletir."""
        try:
            result = self._fn(*self._args, **self._kwargs)
            self.signals.result.emit(result)
        except Exception as exc:
            logger.exception("AsyncWorker hata: %s", exc)
            self.signals.error.emit(str(exc))
        finally:
            self.signals.finished.emit()
