"""
Modüller arası sıkı bağımlılığı (tight coupling) önlemek için merkezi Pub/Sub olay mekanizması.
Bir modül olayı yayınlar, ilgili diğer modüller abone olarak kendi iç durumlarını günceller.
"""
from __future__ import annotations

import inspect
import logging
import weakref
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)


class EventBus:
    """
    Uygulama genelinde tek örnek (Singleton) olay otobüsü.

    Bound method aboneleri WeakMethod ile tutulur: sahibi (örn. silinen bir
    widget) garbage collect edildiğinde abonelik kendiliğinden düşer. Böylece
    unsubscribe çağrılmasa bile ölü Qt nesnelerine yayın yapılmaz.
    Serbest fonksiyon ve lambda'lar güçlü referansla tutulur; zayıf tutulsalar
    başka referansları olmadığı için anında yok olurlardı.

    Kullanım:
        bus = EventBus.instance()
        bus.subscribe("TaskCompleted", my_handler)
        bus.publish("TaskCompleted", task_id=42)
    """

    _instance: EventBus | None = None

    def __init__(self) -> None:
        # Liste elemanı: WeakMethod (bound method) veya doğrudan Callable.
        self._subscribers: dict[str, list[Any]] = defaultdict(list)

    @classmethod
    def instance(cls) -> "EventBus":
        """Tek örneği döndürür; yoksa oluşturur."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def subscribe(self, event_name: str, handler: Callable[..., None]) -> None:
        """
        Belirtilen olaya bir dinleyici (handler) ekler.

        Args:
            event_name: Dinlenecek olayın adı.
            handler: Olay tetiklendiğinde çağrılacak fonksiyon.
        """
        entry: Any
        if inspect.ismethod(handler):
            entry = weakref.WeakMethod(handler)
        else:
            entry = handler
        self._subscribers[event_name].append(entry)
        logger.debug("EventBus: '%s' olayına abone olundu.", event_name)

    def unsubscribe(self, event_name: str, handler: Callable[..., None]) -> None:
        """Belirtilen olaydan bir dinleyiciyi kaldırır."""
        subscribers = self._subscribers.get(event_name, [])
        self._subscribers[event_name] = [
            entry for entry in subscribers if self._resolve(entry) != handler
        ]

    def publish(self, event_name: str, **kwargs: Any) -> None:
        """
        Bir olayı tüm abonelerine yayınlar.

        Args:
            event_name: Yayınlanacak olayın adı.
            **kwargs: Olay verisi olarak iletilecek anahtar-değer çiftleri.
        """
        entries = self._subscribers.get(event_name, [])
        if not entries:
            logger.debug("EventBus: '%s' olayı için abone bulunamadı.", event_name)
            return

        dead: list[Any] = []
        # Yayın sırasında subscribe/unsubscribe olabilir; kopya üzerinde gezilir.
        for entry in list(entries):
            handler = self._resolve(entry)
            if handler is None:
                dead.append(entry)
                continue
            try:
                handler(**kwargs)
            except RuntimeError as exc:
                # PySide6: C++ tarafı silinmiş nesneye çağrı. Abonelik düşürülür,
                # uygulama çökmesi engellenir.
                logger.warning(
                    "EventBus: '%s' aboneliği ölü Qt nesnesine işaret ediyor, kaldırıldı (%s).",
                    event_name,
                    exc,
                )
                dead.append(entry)
            except Exception:
                logger.exception(
                    "EventBus: '%s' olayı işlenirken hata oluştu (handler=%s).",
                    event_name,
                    getattr(handler, "__qualname__", repr(handler)),
                )

        if dead:
            self._subscribers[event_name] = [e for e in entries if e not in dead]

    @staticmethod
    def _resolve(entry: Any) -> Callable[..., None] | None:
        """WeakMethod girdisini çözer; referans öldüyse None döner."""
        if isinstance(entry, weakref.WeakMethod):
            return entry()
        return entry
