# Kurallar ve Sözleşmeler

## RULES.md / CLAUDE.md özü
- Dosya ≤400 satır, sınıf ≤15 metod; aşılıyorsa böl (god object yasağı).
- Ham SQL yasak; SQLAlchemy + Alembic ([[veritabani-katmani]]).
- Her PySide6 widget'ına `parent` parametresi (bellek sızıntısı önlemi).
- Commit: Türkçe, AI referansı yasak, değişikliği spesifik anlatır.
- Yorumlar "neden"i anlatır, "ne"yi değil.
- Graphify zorunluluğu 2026-06-12'de kaldırıldı; mimari bilgi bu wiki'de tutulur ([[log]]).

## Tema sözleşmesi
Renk yalnızca iki yerden gelir: QSS `@token` veya `ThemeManager.color(key)`. `color()` kullanan widget `theme_changed`'e abone olmak ZORUNDA. Python'da `setStyleSheet` yasak (istisna: main_window global QSS). Detay: [[tema-sistemi]].

## L10N sözleşmesi
UI metni `presentation.utils.i18n.tr(key, default)` ile. Hardcoded Türkçe literal ratchet testiyle engellenir; bilinçli veri sabiti `# l10n: data`. Detay: [[l10n-string-yonetimi]].

## EventBus sözleşmesi
Abonelik bound method ile (WeakMethod otomatik temizlik); yayın controller katmanından. Detay: [[event-bus]].

## Repository sözleşmesi
Yeni repo `BaseRepository[T]` veya `ProjectScopedRepository[T]`'den türer; `model` atar; dönen entity'ler detached. Detay: [[veritabani-katmani]].

## Boyut sabitleri
Margin/spacing/sabit boyut magic number yazılmaz; `presentation/dimensions.py` (Spacing/Size/Shadow) kullanılır.

İlgili: [[mimari-genel-bakis]], [[yol-haritasi]]
