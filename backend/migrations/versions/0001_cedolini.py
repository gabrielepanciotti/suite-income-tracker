"""cedolini: periods and payslip lines imported from the life-work flow

Revision ID: 0001
Revises:
Create Date: 2026-10-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "income_tracker"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    op.create_table(
        "periodi",
        sa.Column("flow", sa.String(64), primary_key=True),
        sa.Column("period", sa.String(7), primary_key=True),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("produced_at", sa.String(32), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
        schema=SCHEMA,
    )
    op.create_table(
        "voci",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("flow", sa.String(64), nullable=False),
        sa.Column("period", sa.String(7), nullable=False),
        sa.Column("voce", sa.String(200), nullable=False),
        sa.Column("tipo", sa.String(32), nullable=False),
        sa.Column("ore", sa.Numeric(10, 2)),
        sa.Column("importo", sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(
            ["flow", "period"], [f"{SCHEMA}.periodi.flow", f"{SCHEMA}.periodi.period"],
            ondelete="CASCADE",
        ),
        schema=SCHEMA,
    )
    # the runtime role reads and replaces periods, never alters the schema
    op.execute(f"""
        DO $$ BEGIN
          IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'life_app') THEN
            GRANT USAGE ON SCHEMA {SCHEMA} TO life_app;
            GRANT SELECT, INSERT, DELETE ON ALL TABLES IN SCHEMA {SCHEMA} TO life_app;
            GRANT USAGE ON ALL SEQUENCES IN SCHEMA {SCHEMA} TO life_app;
          END IF;
        END $$;
    """)


def downgrade() -> None:
    op.drop_table("voci", schema=SCHEMA)
    op.drop_table("periodi", schema=SCHEMA)
