"""
EventBus yaşam döngüsü testleri.

Bound method aboneleri WeakMethod ile tutulduğundan, sahibi yok edilen
abonelikler yayında otomatik düşmelidir; aksi halde silinmiş Qt nesnelerine
çağrı yapılarak uygulama çöker (RuntimeError).
"""
import gc

import pytest

from core.events.event_bus import EventBus


@pytest.fixture()
def bus() -> EventBus:
    # Singleton yerine izole örnek: testler birbirinin aboneliğini görmemeli.
    return EventBus()


class _Owner:
    def __init__(self) -> None:
        self.received: list[dict] = []

    def handler(self, **kwargs: object) -> None:
        self.received.append(dict(kwargs))


def test_publish_calls_bound_and_free_handlers(bus: EventBus) -> None:
    owner = _Owner()
    free_calls: list[dict] = []
    bus.subscribe("ev", owner.handler)
    bus.subscribe("ev", lambda **kw: free_calls.append(dict(kw)))

    bus.publish("ev", x=1)

    assert owner.received == [{"x": 1}]
    assert free_calls == [{"x": 1}]


def test_dead_owner_is_pruned_without_crash(bus: EventBus) -> None:
    owner = _Owner()
    bus.subscribe("ev", owner.handler)

    del owner
    gc.collect()

    bus.publish("ev", x=2)  # Çökme olmamalı
    assert bus._subscribers["ev"] == []


def test_unsubscribe_bound_method(bus: EventBus) -> None:
    owner = _Owner()
    bus.subscribe("ev", owner.handler)
    bus.unsubscribe("ev", owner.handler)

    bus.publish("ev", x=3)

    assert owner.received == []


def test_runtime_error_handler_auto_removed(bus: EventBus) -> None:
    # Silinmiş C++ nesnesine çağrı PySide6'da RuntimeError üretir;
    # bus bu aboneliği düşürmeli ve diğer aboneleri etkilememelidir.
    survivor_calls: list[dict] = []

    def dead_handler(**kwargs: object) -> None:
        raise RuntimeError("Internal C++ object already deleted.")

    bus.subscribe("ev", dead_handler)
    bus.subscribe("ev", lambda **kw: survivor_calls.append(dict(kw)))

    bus.publish("ev", x=4)
    bus.publish("ev", x=5)

    assert survivor_calls == [{"x": 4}, {"x": 5}]
    assert all(entry is not dead_handler for entry in bus._subscribers["ev"])


def test_generic_exception_does_not_unsubscribe(bus: EventBus) -> None:
    calls: list[int] = []

    def flaky(**kwargs: object) -> None:
        calls.append(1)
        raise ValueError("iş hatası")

    bus.subscribe("ev", flaky)
    bus.publish("ev")
    bus.publish("ev")

    # ValueError abonelik düşürme sebebi değildir; handler her yayında çağrılır.
    assert len(calls) == 2
