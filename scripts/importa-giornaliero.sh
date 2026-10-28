#!/usr/bin/env bash
# Daily import of the payslip envelopes (cron on dev-linux).
#
# GestorePresenze drops a monthly envelope around the 10th; this picks it up the
# same day it appears. Idempotent: a month whose sha256 is already imported is
# skipped, so running every day costs a few lines of log and nothing else.
set -uo pipefail

RADICE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Settings read backend/.env relative to the cwd.
cd "$RADICE/backend" || exit 1

echo "=== $(date -Is) ==="
# Exit 2 = DATABASE_URL missing in backend/.env.
exec "$RADICE/backend/.venv/bin/python" -m income_tracker_backend.importa
