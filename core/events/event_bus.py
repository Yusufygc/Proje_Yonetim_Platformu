"""
Modüller arası sıkı bağımlılığı (tight coupling) önlemek için merkezi Pub/Sub olay mekanizması.
Bir modül olayı yayınlar, ilgili diğer modüller abone olarak kendi iç durumlarını günceller.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)


class EventBus:
    """
    Uygulama genelinde tek örnek (Singleton) olay otobüsü.

    Kullanım:
        bus = EventBus.instance()
        bus.subscribe("TaskCompleted", my_handler)
        bus.publish("TaskCompleted", task_id=42)
    """

    _instance: EventBus | None = None

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[..., None]]] = defaultdict(list)

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
        self._subscribers[event_name].append(handler)
        logger.debug("EventBus: '%s' olayına abone olundu.", event_name)

    def unsubscribe(self, event_name: str, handler: Callable[..., None]) -> None:
        """Belirtilen olaydan bir dinleyiciyi kaldırır."""
        subscribers = self._subscribers.get(event_name, [])
        if handler in subscribers:
            subscribers.remove(handler)

    def publish(self, event_name: str, **kwargs: Any) -> None:
        """
        Bir olayı tüm abonelerine yayınlar.

        Args:
            event_name: Yayınlanacak olayın adı.
            **kwargs: Olay verisi olarak ilerilecek anahtar-değer çiftleri.
        """
        handlers = self._subscribers.get(event_name, [])
        if not handlers:
            logger.debug("EventBus: '%s' olayı için abone bulunamadı.", event_name)
            return

        for handler in handlers:
            try:
                handler(**kwargs)
            except Exception:
                logger.exception(
                    "EventBus: '%s' olayı işlenirken hata oluştu (handler=%s).",
                    event_name,
                    handler.__qualname__,
                )
