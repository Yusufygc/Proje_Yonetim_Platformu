# Alembic Migrations

Runtime database migrations are managed by Alembic.

Existing SQLite databases created by the old `schema_migrations` runner are
validated and stamped once by `infrastructure.database.alembic_runner`.
