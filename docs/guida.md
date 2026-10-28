# Using IncomeTracker

## Overview

IncomeTracker summarizes structured payslip records by month: earnings, deductions, net pay, and paid hours. The source system sends only `voce`, `tipo`, `ore`, and `importo`; documents and other personal identifiers are not imported.

## API

IncomeTracker exposes JSON endpoints only. Start the application from `backend/`:

```bash
.venv/bin/python -m uvicorn income_tracker_backend.app:app --port 8000
```

Open `http://127.0.0.1:8000/api/stipendio`. Interactive API documentation is available at `/docs` and the health endpoint is `/api/health`.

`GET /api/stipendio` returns an array ordered by reporting period:

```json
{"period": "2026-09", "competenze": "2985.63", "trattenute": "876.67", "altro": "65639.09", "ore": "11.08", "netto": "2108.96"}
```

- `period`: month in `YYYY-MM` format.
- `competenze`: total earning rows.
- `trattenute`: deductions represented as a positive amount.
- `altro`: other row types, such as a printed total; this does not affect net pay.
- `ore`: hours associated with earning rows.
- `netto`: `competenze - trattenute`.

Amounts and hours are decimal strings in the JSON response.

## Importing new records

Run the importer manually from `backend/`:

```bash
cd backend
.venv/bin/python -m income_tracker_backend.importa
```

It reads envelopes from `~/.life/exchange/cedolini/`, or from `LIFE_EXCHANGE_DIR` when set. The operation is idempotent: an unchanged `sha256` is skipped, while a changed checksum replaces the whole month.

## Correcting a month

Correct the data in the source system, then run the importer again. The local copy is replaced on the next import when the source checksum changes.

## Troubleshooting

- `503 "DATABASE_URL not configured"`: set `DATABASE_URL` in `backend/.env`.
- The importer exits with code 2: `DATABASE_URL` is missing.
- An empty response means no records have been imported into the configured database.
- A missing month may not have arrived in the configured exchange directory yet.
