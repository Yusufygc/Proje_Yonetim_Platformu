from enum import Enum

class DecisionStatus(Enum):
    """Proje Karar (Decision Record) durumları"""
    DRAFT = "DRAFT"         # Taslak
    ACCEPTED = "ACCEPTED"   # Kabul edildi
    CHANGED = "CHANGED"     # Değiştirildi
    CANCELED = "CANCELED"   # İptal edildi
