from enum import Enum

class IdeaStatus(Enum):
    """Fikir durumları (03_MODULLER_VE_ISLEVLER.md'ye göre)"""
    DRAFT = "DRAFT"             # Ham fikir
    REVIEWING = "REVIEWING"     # İnceleniyor
    VALIDATING = "VALIDATING"   # Doğrulanacak
    CONVERTED = "CONVERTED"     # Projeye dönüştü
    POSTPONED = "POSTPONED"     # Ertelendi
    REJECTED = "REJECTED"       # Reddedildi
