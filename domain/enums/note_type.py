from enum import Enum

class NoteType(Enum):
    """Proje Not (Note) türleri"""
    GENERAL = "GENERAL"                 # Genel not
    MEETING = "MEETING"                 # Toplantı notu
    RESEARCH = "RESEARCH"               # Araştırma notu
    DEBUG = "DEBUG"                     # Hata ayıklama notu
    LESSON_LEARNED = "LESSON_LEARNED"   # Öğrenilen ders
    RELEASE = "RELEASE"                 # Yayın notu
