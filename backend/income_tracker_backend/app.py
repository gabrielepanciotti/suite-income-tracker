from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request

from income_tracker_backend.importa import FLOW
from income_tracker_backend.stipendio import andamento
from income_tracker_backend.store import SqlStore, Store
from suite_backend_core import create_app, get_settings, make_engine, make_session_factory


def build_app(store: Store | None = None) -> FastAPI:
    app = create_app()
    if store is None:
        url = get_settings().database_url
        store = SqlStore(make_session_factory(make_engine(url))) if url else None
    app.state.store = store

    @app.get("/api/stipendio")
    async def stipendio(request: Request) -> list[dict]:
        """Month by month: gross, withheld, net and paid hours."""
        current: Store | None = request.app.state.store
        if current is None:
            raise HTTPException(503, "DATABASE_URL not configured")
        return andamento(await current.righe(FLOW))

    return app


app = build_app()
