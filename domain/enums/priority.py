"""Öncelik enum'u — proje, görev ve fikir için ortak kullanılır."""
import enum


class Priority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
