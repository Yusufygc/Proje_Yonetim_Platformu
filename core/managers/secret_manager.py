"""OS keychain backed secret storage."""
from __future__ import annotations

import logging
from typing import Any, cast

import config

logger = logging.getLogger(__name__)


class SecretManager:
    """Small wrapper around keyring to avoid plaintext secrets in settings or DB."""

    _instance: "SecretManager | None" = None

    def __init__(self, service_name: str | None = None) -> None:
        self._service_name = service_name or config.APP_NAME

    @classmethod
    def instance(cls) -> "SecretManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_secret(self, key: str, value: str) -> None:
        keyring = self._load_keyring()
        keyring.set_password(self._service_name, key, value)

    def get_secret(self, key: str) -> str | None:
        keyring = self._load_keyring()
        return cast(str | None, keyring.get_password(self._service_name, key))

    def delete_secret(self, key: str) -> None:
        keyring = self._load_keyring()
        try:
            keyring.delete_password(self._service_name, key)
        except Exception as exc:
            logger.debug("Secret delete ignored for key=%s: %s", key, exc)

    @staticmethod
    def _load_keyring() -> Any:
        try:
            import keyring
        except ImportError as exc:
            raise RuntimeError("keyring dependency is required for secret storage.") from exc
        return keyring
