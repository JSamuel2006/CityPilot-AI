#!/bin/bash
###############################################################################
# CityPilot AI — Render Start Script
# Runs Alembic migrations then starts the FastAPI server.
# Render injects $PORT automatically.
###############################################################################

set -e  # Exit immediately on any error

echo "============================================"
echo "  CityPilot AI — Production Startup"
echo "============================================"

# ── 1. Run Alembic migrations ─────────────────────────────────────────────
echo "[1/2] Running Alembic migrations..."
alembic upgrade head
echo "      Migrations complete."

# ── 2. Start Uvicorn ──────────────────────────────────────────────────────
echo "[2/2] Starting Uvicorn on port ${PORT:-8000}..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers 1 \
    --log-level info
