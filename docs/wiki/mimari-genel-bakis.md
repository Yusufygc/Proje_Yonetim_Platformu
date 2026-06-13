# Mimari Genel Bakış

PySide6 masaüstü uygulaması; katı katmanlı mimari:

```
presentation/ (pages, dialogs, widgets, shell)   ← Qt UI
    ↓ sinyal/slot
controllers/  (QObject köprüleri)                ← hata→sinyal dönüşümü, EventBus yayını
    ↓
services/     (iş kuralları)                     ← validasyon, DTO işleme
    ↓
infrastructure/repositories/                     ← SQLAlchemy ORM, BaseRepository
    ↓
infrastructure/database/ (DatabaseManager)       ← engine, scoped_session, WAL
```

## Katman kuralları
- `presentation/` hiçbir yerde `infrastructure/` veya `sqlalchemy` import etmez (doğrulanmış, ihlal yok).
- `core/` Qt'ye bağımlıdır (manager'lar QObject) — bilinçli pragmatik karar.
- Ham SQL yasak; tüm erişim ORM üzerinden ([[veritabani-katmani]]).

## Ana bileşenler
- Bağımlılık kurulumu: [[di-container]] (`di_container.py` bootstrap).
- Modüller arası gevşek bağ: [[event-bus]] (`core/events/event_bus.py`).
- UI kilitlenmesini önleme: [[worker-altyapisi]] (`core/workers/`).
- Görsel katman: [[tema-sistemi]], [[ikon-yonetimi]], [[l10n-string-yonetimi]].
- Sayfa kaydı: `presentation/modules.py` + `core/module_registry.py` — sayfalar factory lambda'larıyla lazily kurulur.

## Boyut metrikleri (2026-06-12)
~142 .py dosyası, ~11.400 satır. RULES.md limitleri: dosya ≤400 satır, sınıf ≤15 metod ([[kurallar-ve-sozlesmeler]]). Bilinen istisna: `DIContainer` (factory yoğun, P3'te bölünecek — [[yol-haritasi]]).

İlgili: [[gorevler-modulu]], [[log]]
