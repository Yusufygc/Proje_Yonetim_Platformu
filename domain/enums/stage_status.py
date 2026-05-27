"""Proje aşaması durum enumları."""
from __future__ import annotations

import enum


class StageStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
