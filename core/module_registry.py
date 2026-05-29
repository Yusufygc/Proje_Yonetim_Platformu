"""
Tak-Çıkar modül altyapısı: FeaturePlugin tanımı ve ModuleRegistry singleton'ı.
Presentation katmanından bağımsızdır; yalnızca tip denetiminde QWidget kullanılır.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


@dataclass
class FeaturePlugin:
    """
    Tek bir uygulama modülünün tüm meta-verisini taşır.

    factory: parent QWidget alıp sayfa widget'ını döndüren fabrika fonksiyonu.
    """

    page_key: str
    nav_label_key: str
    nav_label_default: str
    nav_icon: str
    factory: Callable[[QWidget], QWidget]


class ModuleRegistry:
    """Uygulama modüllerinin singleton kaydı."""

    _instance: ModuleRegistry | None = None

    def __init__(self) -> None:
        self._plugins: list[FeaturePlugin] = []
        self._by_key: dict[str, FeaturePlugin] = {}

    @classmethod
    def instance(cls) -> ModuleRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, plugin: FeaturePlugin) -> None:
        if plugin.page_key in self._by_key:
            raise ValueError(f"Aynı page_key ile iki modül kaydedilemez: {plugin.page_key!r}")
        self._plugins.append(plugin)
        self._by_key[plugin.page_key] = plugin

    def plugins(self) -> list[FeaturePlugin]:
        return list(self._plugins)

    def get(self, page_key: str) -> FeaturePlugin | None:
        return self._by_key.get(page_key)
