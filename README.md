# IncomeTracker

IncomeTracker is a small FastAPI service that imports structured payslip records and presents monthly gross pay, deductions, net pay, and paid hours. It keeps a replaceable local copy of each reporting period, so corrected source data can be safely imported again.

## Features

- Imports structured records from a filesystem exchange directory.
- Replaces a reporting period atomically when its source checksum changes.
- Exposes monthly totals through `GET /api/stipendio`.
- Uses SQLite in-memory storage for the test suite and PostgreSQL-compatible URLs in production.

## Requirements

- Python 3.13
- A checkout of the Life framework beside this repository (for `suite_backend_core`)
- PostgreSQL or another supported database for runtime use

## Quickstart

```bash
git clone <repository-url> income-tracker
git clone <life-framework-url> Life
cd income-tracker
cp backend/.env.example backend/.env
cd backend
python3.13 -m venv .venv
.venv/bin/pip install ../../Life/packages/shared ../../Life/packages/backend-core -r requirements-dev.txt
.venv/bin/uvicorn income_tracker_backend.app:app --port 8000
```

Set `DATABASE_URL` in `backend/.env` before starting the service. The API is then available at `http://127.0.0.1:8000/api/stipendio`. A generic [Docker Compose example](deploy/docker-compose.example.yml) is provided for container deployments; after supplying an image that contains this service and its framework dependency, run `docker compose -f deploy/docker-compose.example.yml up`.

## Tests

The repository has no frontend. Run the Python test suite with:

```bash
cd backend
.venv/bin/python -m pytest
```

The GitHub workflow checks out the Life framework next to this repository. Configure the optional `LIFE_FRAMEWORK_REPO` repository variable when its location differs from the default `suite-life`.

## Configuration

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Database connection URL used by the API and importer. |
| `LIFE_EXCHANGE_DIR` | Directory containing incoming structured record envelopes. |
| `PORT` | HTTP port used by the module entry point. |

See [the user guide](docs/guida.md) for import behaviour and API details.

## License

MIT. See [LICENSE](LICENSE).
