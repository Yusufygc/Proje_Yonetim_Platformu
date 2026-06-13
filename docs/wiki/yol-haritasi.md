# Yol Haritası

Kaynak analiz: `Project_docs/SENIOR_ANALIZ_RAPORU_2026-06-12.md` (durum tablosu §9).

## Tamamlandı (2026-06-12)
- **P0**: [[event-bus]] WeakMethod + RuntimeError prune; WBS render fix (döngü içi import, `setUpdatesEnabled`).
- **P1**: [[gorevler-modulu]] paket bölünmesi; `project_dialog` + `form_utils` refactor; tema sözleşmesi bağlantıları ([[tema-sistemi]]); QSS modülerleştirme (base/ 8 modül).
- **P2**: `BaseRepository[T]` ([[veritabani-katmani]]); StringManager `language_changed` + ratchet testi + `project_dialog` migrasyonu ([[l10n-string-yonetimi]]); yazmalar senkron kararı ([[worker-altyapisi]]).

## P3 — Tamamlandı (2026-06-12)
1. ✅ **DIContainer bölünmesi**: `di_registries.py` (Repository/Service/Controller registry) + facade `__getattr__` delegasyonu ([[di-container]]).
2. ✅ **IconManager**: `QSvgRenderer`, `Icons` sabitleri, DRY, `try_instance()` ([[ikon-yonetimi]]).
3. ✅ **Script taşıma**: `commit_all.py`, `download_assets.py` → `scripts/`.

## Sürekli kuyruk
- L10N migrasyonu: 21 dosya allowlist'te ([[l10n-string-yonetimi]]).
- Dil seçici UI + `language_changed` dinleyicileri (L10N tamamlanınca).
- ✅ Tamamlandı (2026-06-13): UI'daki Service Locator çağrıları (Theme/Icon/String/Pref/EventBus) constructor injection'a çevrildi; factory'ler `di.<manager>` ile besler ([[di-container]]).

İlgili: [[kurallar-ve-sozlesmeler]], [[log]]
