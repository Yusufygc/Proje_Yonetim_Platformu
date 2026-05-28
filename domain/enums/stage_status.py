"""Proje aşaması durum enumları."""
from __future__ import annotations

import enum


class StageStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    ACTIVE = "ACTIVE"
    DONE = "DONE"
    SKIPPED = "SKIPPED"
