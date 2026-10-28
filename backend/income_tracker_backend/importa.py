"""Import the `cedolini` envelopes from the exchange directory into the store.

    python -m income_tracker_backend.importa

Idempotent: a period whose sha256 is already imported is skipped; a period whose
sha256 changed is a correction at the source and replaces the whole month.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from dataclasses import dataclass, field

from income_tracker_backend.store import SqlStore, Store
from suite_backend_core import get_settings, make_engine, make_session_factory
from suite_backend_core.flows import Envelope, read_envelopes

FLOW = "cedolini"
logger = logging.getLogger(__name__)


@dataclass
class Esito:
    importati: list[str] = field(default_factory=list)
    invariati: list[str] = field(default_factory=list)


async def importa(envelopes: Sequence[Envelope], store: Store) -> Esito:
    esito = Esito()
    for env in envelopes:
        if await store.sha_importato(env.flow, env.period) == env.sha256:
            esito.invariati.append(env.period)
            continue
        await store.sostituisci(env)
        esito.importati.append(env.period)
    return esito


async def _main() -> int:
    url = get_settings().database_url
    if not url:
        logger.error("DATABASE_URL not set (backend/.env)")
        return 2
    engine = make_engine(url)
    try:
        esito = await importa(read_envelopes(FLOW), SqlStore(make_session_factory(engine)))
    finally:
        await engine.dispose()
    logger.info("imported %s, unchanged %s", esito.importati or "-", esito.invariati or "-")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(asyncio.run(_main()))
