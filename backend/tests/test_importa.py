from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient

from income_tracker_backend.app import build_app
from income_tracker_backend.importa import importa
from income_tracker_backend.stipendio import andamento
from suite_backend_core import get_settings
from suite_backend_core.flows import read_envelopes, write_envelope

FIELDS = ["voce", "tipo", "ore", "importo"]
SETTEMBRE = [
    {"voce": "Retribuzione ordinaria", "tipo": "competenza", "ore": 160, "importo": 2000},
    {"voce": "Straordinario", "tipo": "competenza", "ore": 8, "importo": 150.5},
    {"voce": "IRPEF", "tipo": "trattenuta", "ore": None, "importo": -450},
    {"voce": "Netto in busta", "tipo": "totale", "ore": None, "importo": 1700.5},
    {"voce": "Ferie godute gg", "tipo": "informativa", "ore": None, "importo": None},
]


def _envelopes(tmp_path, records=SETTEMBRE, period="2026-09"):
    write_envelope("cedolini", period, records, source="life-work:gestorePresenze",
                   allowed_fields=FIELDS, root=tmp_path)
    return read_envelopes("cedolini", root=tmp_path)


def test_andamento_nets_competenze_minus_trattenute() -> None:
    [mese] = andamento([{**r, "period": "2026-09"} for r in SETTEMBRE])
    assert mese["competenze"] == Decimal("2150.5")
    assert mese["trattenute"] == Decimal("450")
    assert mese["netto"] == Decimal("1700.5")
    assert mese["altro"] == Decimal("1700.5")  # the printed total is not summed in
    assert mese["ore"] == Decimal("168")


def test_andamento_orders_months() -> None:
    righe = [{"period": p, "voce": "x", "tipo": "competenza", "importo": 1} for p in ("2026-09", "2026-07")]
    assert [m["period"] for m in andamento(righe)] == ["2026-07", "2026-09"]


async def test_import_is_idempotent(tmp_path, store) -> None:
    envs = _envelopes(tmp_path)
    assert (await importa(envs, store)).importati == ["2026-09"]
    esito = await importa(envs, store)
    assert (esito.importati, esito.invariati) == ([], ["2026-09"])
    assert len(await store.righe("cedolini")) == len(SETTEMBRE)


async def test_correction_replaces_the_whole_month(tmp_path, store) -> None:
    await importa(_envelopes(tmp_path), store)
    corretto = [{**SETTEMBRE[0], "importo": 2100}, SETTEMBRE[2]]
    assert (await importa(_envelopes(tmp_path, corretto), store)).importati == ["2026-09"]
    righe = await store.righe("cedolini")
    assert [r["importo"] for r in righe] == [Decimal("2100.00"), Decimal("-450.00")]


async def test_api_stipendio(tmp_path, store) -> None:
    await importa(_envelopes(tmp_path), store)
    body = TestClient(build_app(store)).get("/api/stipendio").json()
    assert [(m["period"], m["netto"]) for m in body] == [("2026-09", "1700.50")]


def test_api_without_database_is_503(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)  # settings read backend/.env relative to the cwd
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()
    try:
        assert TestClient(build_app()).get("/api/stipendio").status_code == 503
    finally:
        get_settings.cache_clear()
