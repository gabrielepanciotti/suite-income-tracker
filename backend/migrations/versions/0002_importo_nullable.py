"""importo nullable: informational payslip lines (e.g. days of leave) carry no amount

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

SCHEMA = "income_tracker"


def upgrade() -> None:
    op.alter_column("voci", "importo", existing_type=sa.Numeric(12, 2), nullable=True, schema=SCHEMA)


def downgrade() -> None:
    op.alter_column("voci", "importo", existing_type=sa.Numeric(12, 2), nullable=False, schema=SCHEMA)
