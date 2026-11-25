# Veritabanı Katmanı

## DatabaseManager (`infrastructure/database/db_manager.py`)
- Singleton; SQLAlchemy 2.0 style, ham SQL yasak (RULES.md).
- `create_engine(..., check_same_thread=False)` + `scoped_session(sessionmaker(expire_on_commit=False))`.
- `PRAGMA journal_mode=WAL` açılışta bir kez çalıştırılır (dosyada kalıcıdır).
- `PRAGMA foreign_keys=ON` SQLite'ta bağlantı bazındadır; `connect` olayında havuzdaki her bağlantıya uygulanır (`_enable_foreign_keys`). Testi: `tests/test_foreign_keys.py` (geçici dosya veritabanı; bellek-içi veritabanı bu hatayı göstermez).
- **Alembic motorunda `foreign_keys` kapalı kalmalıdır:** `env.py` ayrı bir `NullPool` motoru kurar. Ayar açık olsaydı `batch_alter_table`'ın tabloyu yeniden kurarken yaptığı `DROP TABLE`, alt kayıtları `CASCADE` ile silerdi.
- **Eski yetim kayıtlar:** Ayarın kapalı olduğu bağlantılarda silinen kayıtlara işaret eden referanslar eski veritabanlarında kalmış olabilir; otomatik temizlenmez. SQLite yalnızca yazılan referans kolonunu denetlediği için bu satırlar güncellenebilir ve silinebilir. `PRAGMA foreign_key_check` ile listelenir.
- Her bağlantıya Türkçe uyumlu arama katlama fonksiyonu eklenir (`_register_sql_functions`).
- `session()` context manager: commit/rollback otomatik, `finally`'de `scoped_session.remove()` → worker thread'leriyle güvenli ([[worker-altyapisi]]).
- Migration: Alembic (`run_migrations`), [[di-container]] bootstrap'inde çağrılır.

## BaseRepository deseni (2026-06-12, `infrastructure/repositories/base_repository.py`)
- `BaseRepository[T]`: `create / create_many / get_by_id / update / update_many / delete`. Entity'ler **flush + refresh + expunge** ile detached döndürülür (session kapandıktan sonra UI'da güvenle taşınır).
- `_query_options()` override → `selectinload` ekleme noktası (Project: stages/tasks/tags; Task: checklist_items — N+1 önlenir).
- `ProjectScopedRepository[T]`: `get_by_project(project_id)` + `_project_order()` ile sıralama.
- Yeni repo yazarken kural: bu tabanlardan türet; `model = X` ata; özel imza gerekirse `# type: ignore[override]` ile sar (örn. `ActivityLogRepository.create` alanlardan kurar).

## Repo envanteri
13 repo; çoğu kısadır. Özel davranışlar: `ProjectRepository.get_all` (arşiv filtresi + sayfalama), `TaskRepository.calculate_progress_percent` (tek SQL ile yaprak görev ilerlemesi), `ProjectTagRepository.replace_for_project` (tam değiştirme).

İlgili: [[mimari-genel-bakis]], [[kurallar-ve-sozlesmeler]]
