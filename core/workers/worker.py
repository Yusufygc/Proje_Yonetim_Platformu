"""
Asenkron işlemler için Worker altyapısı.
Main Thread'i (UI Thread) kilitlememek için ağır işlemler burada çalıştırılır.
"""
import logging
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """Worker nesnesinden UI thread'e veri iletmek için kullanılan sinyaller."""
    finished = Signal()
    error = Signal(str)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    """
    QThreadPool içinde çalıştırılacak jenerik iş parçacığı sınıfı.

    Örnek kullanım:
        worker = Worker(my_heavy_function, arg1, arg2)
        worker.signals.result.connect(self.on_success)
        worker.signals.error.connect(self.on_error)
        worker.start()
    """

    _active_workers: set["Worker"] = set()

    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.setAutoDelete(False)

    @Slot()
    def run(self) -> None:
        """İşlemi arka planda çalıştırır."""
        try:
            if "progress_callback" in self.fn.__code__.co_varnames:
                self.kwargs["progress_callback"] = self.signals.progress.emit

            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            logger.exception("Worker failed while running %s", getattr(self.fn, "__name__", self.fn))
            self.signals.error.emit(str(e))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

    def start(self) -> None:
        """Worker'i başlat ve GC'ye karşı referansı koru."""
        Worker._active_workers.add(self)
        self.signals.finished.connect(self._cleanup)
        QThreadPool.globalInstance().start(self)

    @Slot()
    def _cleanup(self) -> None:
        """Tüm sinyaller işlendikten sonra referansı serbest bırak."""
        Worker._active_workers.discard(self)
