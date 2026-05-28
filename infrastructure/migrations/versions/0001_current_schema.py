"""Current application schema baseline.

Revision ID: 0001_current_schema
Revises:
Create Date: 2026-05-27
"""
from __future__ import annotations

from alembic import op

revision = "0001_current_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    import domain.models  # noqa: F401
    from infrastructure.database.base_model import Base

    Base.metadata.create_all(bind)


def downgrade() -> None:
    bind = op.get_bind()
    import domain.models  # noqa: F401
    from infrastructure.database.base_model import Base

    Base.metadata.drop_all(bind)
