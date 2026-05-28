"""
Tüm DTO'ların türetileceği temel veri transfer nesneleri.
"""
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class BaseDTO:
    """Temel DTO sınıfı."""
    
    def to_dict(self) -> dict[str, Any]:
        """Nesneyi sözlüğe dönüştürür."""
        return asdict(self)
