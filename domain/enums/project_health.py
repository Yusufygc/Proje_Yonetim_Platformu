"""Proje sağlığı enum'u."""
import enum


class ProjectHealth(str, enum.Enum):
    GOOD = "GOOD"
    AT_RISK = "AT_RISK"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"
