from enum import Enum

class ResourceType(Enum):
    """Proje Kaynak (Resource) türleri"""
    DOCUMENT = "DOCUMENT"   # Doküman
    ARTICLE = "ARTICLE"     # Makale
    VIDEO = "VIDEO"         # Video
    GITHUB = "GITHUB"       # GitHub / Repo
    DESIGN = "DESIGN"       # Tasarım (Figma vs.)
    API = "API"             # API Referansı
    TOOL = "TOOL"           # Araç
    OTHER = "OTHER"         # Diğer
