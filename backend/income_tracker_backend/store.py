"""Where imported periods live. ``SqlStore`` is the real one; tests use it on SQLite."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Protocol

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from income_tracker_backend.db import Periodo, Voce
from suite_backend_core.flows import Envelope


class Store(Protocol):
    async def sha_importato(self, flow: str, period: str) -> str | None: ...
    async def sostituisci(self, envelope: Envelope) -> None: ...
    async def righe(self, flow: str) -> list[dict[str, Any]]: ...


def _decimal(value: Any) -> Decimal | None:
    return None if value is None else Decimal(str(value))


class SqlStore:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    async def sha_importato(self, flow: str, period: str) -> str | None:
        async with self._sessions() as s:
            return await s.scalar(
                select(Periodo.sha256).where(Periodo.flow == flow, Periodo.period == period)
            )

    async def sostituisci(self, envelope: Envelope) -> None:
        """Replace the whole period in one transaction: never a half month."""
        async with self._sessions() as s, s.begin():
            key = (Periodo.flow == envelope.flow, Periodo.period == envelope.period)
            await s.execute(delete(Voce).where(Voce.flow == envelope.flow, Voce.period == envelope.period))
            await s.execute(delete(Periodo).where(*key))
            s.add(Periodo(
                flow=envelope.flow, period=envelope.period, source=envelope.source,
                sha256=envelope.sha256, produced_at=envelope.produced_at,
                imported_at=datetime.now(UTC),
                voci=[
                    Voce(flow=envelope.flow, period=envelope.period, voce=r["voce"], tipo=r["tipo"],
                         ore=_decimal(r.get("ore")), importo=_decimal(r.get("importo")))
                    for r in envelope.records
                ],
            ))

    async def righe(self, flow: str) -> list[dict[str, Any]]:
        async with self._sessions() as s:
            rows = await s.scalars(select(Voce).where(Voce.flow == flow).order_by(Voce.period, Voce.id))
            return [
                {"period": v.period, "voce": v.voce, "tipo": v.tipo, "ore": v.ore, "importo": v.importo}
                for v in rows
            ]
