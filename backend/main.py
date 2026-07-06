"""
CityPilot AI — FastAPI Application Entry Point.
PostgreSQL-only backend with structured JSON responses.
"""

import time
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()

from config import get_settings  # noqa: E402
from routers import dashboard, analyze, map, analytics, report, upload, settings as settings_router  # noqa: E402

settings = get_settings()

# ── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
)
logger = logging.getLogger("citypilot")


# ── Lifespan ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CityPilot AI starting — PostgreSQL backend")
    yield
    logger.info("CityPilot AI shutting down")


# ── Application ─────────────────────────────────────────────────────
app = FastAPI(
    title="CityPilot AI API",
    version="1.0.0-beta",
    lifespan=lifespan,
)

# CORS — reads from CORS_ORIGINS env var
# Set CORS_ORIGINS=https://your-frontend.vercel.app in Render dashboard
_raw_origins = settings.CORS_ORIGINS.strip()
if _raw_origins == "*":
    _allow_origins = ["*"]
    _allow_credentials = False   # Can't combine "*" with credentials per CORS spec
else:
    _allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
    _allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Timing Middleware ───────────────────────────────────────
@app.middleware("http")
async def add_request_timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Execution-Time-Ms"] = str(elapsed)
    return response


# ── Global Exception Handler ───────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_time_ms": 0,
        },
    )


# ── Routers ─────────────────────────────────────────────────────────
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(analyze.router, tags=["AI Command Center"])
app.include_router(map.router, tags=["City Map"])
app.include_router(analytics.router, tags=["Analytics"])
app.include_router(report.router, tags=["Reports"])
app.include_router(upload.router, tags=["Knowledge Base"])
app.include_router(settings_router.router, tags=["Settings"])


@app.get("/")
def read_root():
    return {
        "success": True,
        "message": "Welcome to CityPilot AI API",
        "data": {"version": "1.0.0-beta", "database": "PostgreSQL"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
