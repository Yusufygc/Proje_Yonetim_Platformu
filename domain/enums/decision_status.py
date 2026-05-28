from enum import Enum

class DecisionStatus(Enum):
    """Proje Karar (Decision Record) durumları"""
    DRAFT = "DRAFT"         # Taslak
    ACCEPTED = "ACCEPTED"   # Kabul edildi
    SUPERSEDED = "SUPERSEDED"  # Değiştirildi
    CANCELLED = "CANCELLED"    # İptal edildi
