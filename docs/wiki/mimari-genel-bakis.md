# Mimari Genel Bakış

PySide6 + QML masaüstü uygulaması; katı katmanlı mimari (eski Qt Widgets arayüzü 2026-10-07'de kaldırıldı):

```
presentation/qml/ + presentation/viewmodels/      ← QML arayüzü + ViewModel/köprüler
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
- Navigasyon kaydı: `presentation/modules.py` + `core/module_registry.py` yalnızca sayfa anahtarı, etiket ve ikon meta-verisini tutar (`FeaturePlugin`); `NavigationBridge.modules` bunu QML kenar çubuğuna açar. Sayfaların kendisi `presentation/qml/main.qml` içinde yüklenir.

## Boyut metrikleri (2026-06-12)
~142 .py dosyası, ~11.400 satır. RULES.md limitleri: dosya ≤400 satır, sınıf ≤15 metod ([[kurallar-ve-sozlesmeler]]). Bilinen istisna: `DIContainer` (factory yoğun, P3'te bölünecek — [[yol-haritasi]]).

İlgili: [[gorevler-modulu]], [[log]]
