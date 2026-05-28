from enum import Enum


class IdeaStatus(Enum):
    """Fikir durumları."""
    RAW = "RAW"                 # Ham fikir
    REVIEWING = "REVIEWING"     # İnceleniyor
    VALIDATING = "VALIDATING"   # Doğrulanacak
    CONVERTED = "CONVERTED"     # Projeye dönüştü
    DEFERRED = "DEFERRED"       # Ertelendi
    REJECTED = "REJECTED"       # Reddedildi
