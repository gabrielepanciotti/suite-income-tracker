"""IncomeTracker data model: one copy per imported period of the `cedolini` flow.

The node owns the schema `income_tracker` (``schema_for("income-tracker")``)
inside the instance database. The source of truth stays GestorePresenze on
life-work; these tables are the local copy the flow delivers (Life ADR 0001).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKeyConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from suite_backend_core import Base, schema_for

SCHEMA = schema_for("income-tracker")


class Periodo(Base):
    """One imported envelope: which month, from whom, which content (sha256)."""

    __tablename__ = "periodi"
    __table_args__ = {"schema": SCHEMA}

    flow: Mapped[str] = mapped_column(String(64), primary_key=True)
    period: Mapped[str] = mapped_column(String(7), primary_key=True)  # YYYY-MM
    source: Mapped[str] = mapped_column(String(128))
    sha256: Mapped[str] = mapped_column(String(64))
    produced_at: Mapped[str] = mapped_column(String(32))
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    voci: Mapped[list[Voce]] = relationship(
        back_populates="periodo", cascade="all, delete-orphan", order_by="Voce.id"
    )


class Voce(Base):
    """One payslip line: exactly the fields the flow contract lets out."""

    __tablename__ = "voci"
    __table_args__ = (
        # deleting a period drops its lines: a correction replaces the month
        ForeignKeyConstraint(
            ["flow", "period"],
            [f"{SCHEMA}.periodi.flow", f"{SCHEMA}.periodi.period"],
            ondelete="CASCADE",
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flow: Mapped[str] = mapped_column(String(64))
    period: Mapped[str] = mapped_column(String(7))
    voce: Mapped[str] = mapped_column(String(200))
    tipo: Mapped[str] = mapped_column(String(32))
    ore: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    importo: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    periodo: Mapped[Periodo] = relationship(back_populates="voci")
