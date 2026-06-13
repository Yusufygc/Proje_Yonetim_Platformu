# Veritabanı Katmanı

## DatabaseManager (`infrastructure/database/db_manager.py`)
- Singleton; SQLAlchemy 2.0 style, ham SQL yasak (RULES.md).
- `create_engine(..., check_same_thread=False)` + `scoped_session(sessionmaker(expire_on_commit=False))`.
- `PRAGMA journal_mode=WAL` + `foreign_keys=ON` açılışta.
- `session()` context manager: commit/rollback otomatik, `finally`'de `scoped_session.remove()` → worker thread'leriyle güvenli ([[worker-altyapisi]]).
- Migration: Alembic (`run_migrations`), [[di-container]] bootstrap'inde çağrılır.

## BaseRepository deseni (2026-06-12, `infrastructure/repositories/base_repository.py`)
- `BaseRepository[T]`: `create / create_many / get_by_id / update / update_many / delete`. Entity'ler **flush + refresh + expunge** ile detached döndürülür (session kapandıktan sonra UI'da güvenle taşınır).
- `_query_options()` override → `selectinload` ekleme noktası (Project: stages/tasks/tags; Task: checklist_items — N+1 önlenir).
- `ProjectScopedRepository[T]`: `get_by_project(project_id)` + `_project_order()` ile sıralama.
- Yeni repo yazarken kural: bu tabanlardan türet; `model = X` ata; özel imza gerekirse `# type: ignore[override]` ile sar (örn. `ActivityLogRepository.create` alanlardan kurar).

## Repo envanteri
12 repo; çoğu ~11 satır. Özel davranışlar: `ProjectRepository.get_all` (arşiv filtresi + sayfalama), `TaskRepository.calculate_progress_percent` (tek SQL ile yaprak görev ilerlemesi), `ProjectTagRepository.replace_for_project` (tam değiştirme).

İlgili: [[mimari-genel-bakis]], [[kurallar-ve-sozlesmeler]]
