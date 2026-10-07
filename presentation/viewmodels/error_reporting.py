"""Controller hata sinyallerini kullanıcıya toast olarak ileten ortak yardımcı."""
from __future__ import annotations

from typing import Any

from core.events.event_bus import EventBus


def forward_errors_to_toast(event_bus: EventBus, *controllers: Any) -> None:
    """Her controller'ın `error_occurred` sinyalini toast'a bağlar.

    Controller'lar istisnaları yakalayıp sinyalle bildirir; dinleyen olmazsa kullanıcı
    başarısız bir işlemin sessizce kaybolduğunu görür.
    """
    for controller in controllers:
        controller.error_occurred.connect(
            lambda message: event_bus.publish("toast.show", message=message, type_="danger")
        )
