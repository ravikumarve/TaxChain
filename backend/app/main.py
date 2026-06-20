"""
TaxChain API — Main Entry Point
Production-grade FastAPI application with background jobs,
structured logging, rate limiting, and monitoring.
"""

import os
import logging
import uuid
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth, wallets, transactions, reports, payments, webhooks
from app.utils.error_handler import ErrorResponse, handle_general_error
from app.services.scheduler import start_scheduler, stop_scheduler

# Ensure logs directory exists before configuring logging
os.makedirs("logs", exist_ok=True)

# ---------------------------------------------------------------------------
# Structured JSON Logging
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("logs/taxchain.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# Suppress noisy libs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

# ---------------------------------------------------------------------------
# Request ID Middleware
# ---------------------------------------------------------------------------

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request for traceability."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4().hex[:16])
        request.state.request_id = request_id

        start_time = datetime.utcnow()
        response = await call_next(request)
        elapsed = (datetime.utcnow() - start_time).total_seconds()

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed:.3f}s"

        # Log slow requests (>2s) for performance monitoring
        if elapsed > 2.0:
            logger.warning(
                "Slow request: %s %s took %.3fs [rid=%s]",
                request.method, request.url.path, elapsed, request_id,
            )

        return response


# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TaxChain API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# ---------------------------------------------------------------------------
# Middleware (order matters: innermost first, outermost last)
# ---------------------------------------------------------------------------
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        settings.CORS_ORIGINS.split(",")
        if settings.CORS_ORIGINS
        else [settings.FRONTEND_URL]
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.TRUSTED_HOSTS.split(",")
    if settings.TRUSTED_HOSTS
    else ["*"],
)

# ---------------------------------------------------------------------------
# Sentry (error tracking) — optional, only if DSN is configured
# ---------------------------------------------------------------------------
if settings.SENTRY_DSN:
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=0.1,
            environment=os.getenv("APP_ENV", "dev"),
        )
        logger.info("Sentry error tracking initialized")
    except Exception as e:
        logger.warning("Failed to initialize Sentry: %s", e)

# ---------------------------------------------------------------------------
# Lifespan Events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    # Import all models to ensure they're registered with SQLAlchemy
    from app.models import (
        User,
        Wallet,
        Transaction,
        CostBasisLot,
        TaxEvent,
        Subscription,
    )

    # Start background scheduler
    start_scheduler()

    logger.info("TaxChain API started successfully [env=%s]", os.getenv("APP_ENV", "dev"))


@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown of background services."""
    stop_scheduler()
    logger.info("TaxChain API shut down gracefully")


# ---------------------------------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions globally with request ID tracing."""
    request_id = getattr(request.state, "request_id", "unknown")
    error_response = handle_general_error(exc, "global_exception_handler")
    return JSONResponse(
        status_code=error_response.status_code,
        content={
            **({"detail": error_response.detail} if isinstance(error_response.detail, str) else error_response.detail),
            "request_id": request_id,
        },
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(wallets.router, prefix="/api/wallets", tags=["wallets"])
app.include_router(
    transactions.router, prefix="/api/transactions", tags=["transactions"]
)
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])


# ---------------------------------------------------------------------------
# Health & Root
# ---------------------------------------------------------------------------

_startup_time = datetime.utcnow()


@app.get("/")
async def root():
    return {
        "message": "TaxChain API is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check with database connectivity."""
    from sqlalchemy import text
    from app.database import async_session

    checks = {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": (datetime.utcnow() - _startup_time).seconds,
        "environment": os.getenv("APP_ENV", "dev"),
    }

    # Database check
    try:
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"error: {e}"
        checks["status"] = "degraded"

    status_code = 200 if checks["status"] == "healthy" else 503
    return JSONResponse(content=checks, status_code=status_code)
