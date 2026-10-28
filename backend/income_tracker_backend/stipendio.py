"""Salary over time, from the imported payslip lines. Pure: no I/O.

``tipo`` is set by the producer (GestorePresenze#10): ``competenza`` adds to
the gross, ``trattenuta`` is withheld. The producer writes withholdings with the
sign printed on the slip (negative), so ``trattenute`` is reported as a positive
amount and a positive ``trattenuta`` line (a refund) lowers it. Net = competenze
- trattenute. Any other ``tipo`` (``totale``, ``informativa``) is kept aside in
``altro`` and never summed into the net, so a total printed on the slip is not
counted twice. A line without an amount (e.g. days of leave) counts as zero.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from decimal import Decimal
from typing import Any


def andamento(righe: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    mesi: dict[str, dict[str, Any]] = {}
    for r in righe:
        m = mesi.setdefault(r["period"], {
            "period": r["period"], "competenze": Decimal(0), "trattenute": Decimal(0),
            "altro": Decimal(0), "ore": Decimal(0),
        })
        importo = Decimal(str(r["importo"] if r["importo"] is not None else 0))
        if r["tipo"] == "competenza":
            m["competenze"] += importo
            m["ore"] += Decimal(str(r.get("ore") or 0))
        elif r["tipo"] == "trattenuta":
            m["trattenute"] -= importo
        else:
            m["altro"] += importo
    out = []
    for period in sorted(mesi):
        m = mesi[period]
        m["netto"] = m["competenze"] - m["trattenute"]
        out.append(m)
    return out
