# Kurallar ve Sözleşmeler

## RULES.md / CLAUDE.md özü
- Dosya ≤400 satır, sınıf ≤15 metod; aşılıyorsa böl (god object yasağı).
- Ham SQL yasak; SQLAlchemy + Alembic ([[veritabani-katmani]]).
- Python tarafında oluşturulan her `QObject`'e `parent` parametresi (bellek sızıntısı önlemi).
- Commit: Türkçe, AI referansı yasak, değişikliği spesifik anlatır.
- Yorumlar "neden"i anlatır, "ne"yi değil.
- Graphify zorunluluğu 2026-06-12'de kaldırıldı; mimari bilgi bu wiki'de tutulur ([[log]]).

## Sürüm yayınlama sözleşmesi
Sürüm tek kaynaktan (`APP_VERSION`) `scripts/set_version.py` ile değişir; yayın yalnızca `vX.Y.Z` etiketiyle olur ve etiket sürümle birebir aynı olmalıdır. Yayınlanmış etiket taşınmaz; asistanlar açık istek olmadan etiket oluşturmaz/push etmez. RULES.md §8. Detay: [[surum-yayinlama]].

## Tema sözleşmesi
Renk yalnızca `ThemeManager`/`ThemeBridge` paletinden gelir (`themeBridge.color("key")`); QML dosyalarına sabit renk yazılmaz. Detay: [[tema-sistemi]].

## L10N sözleşmesi
UI metni `presentation.utils.i18n.tr(key, default)` ile. Hardcoded Türkçe literal ratchet testiyle engellenir; bilinçli veri sabiti `# l10n: data`. Detay: [[l10n-string-yonetimi]].

## EventBus sözleşmesi
Abonelik bound method ile (WeakMethod otomatik temizlik); yayın controller katmanından. Detay: [[event-bus]].

## Repository sözleşmesi
Yeni repo `BaseRepository[T]` veya `ProjectScopedRepository[T]`'den türer; `model` atar; dönen entity'ler detached. Detay: [[veritabani-katmani]].

## Boyut sabitleri
QML boyut/aralık/süre değerleri `presentation/qml/theme/Theme.qml` sabitlerinden alınır (`Theme.spacing`, `Theme.radius`, `Theme.animation`); `presentation/dimensions.py` yalnızca font ailesi sabitlerini taşır.

İlgili: [[mimari-genel-bakis]], [[yol-haritasi]], [[surum-yayinlama]]
