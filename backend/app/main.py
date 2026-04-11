import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from alembic.config import Config
from alembic import command
from app.config import settings
from app.database import engine, Base
from app.routers import auth, wallets, transactions, reports
from app.utils.error_handler import ErrorResponse, handle_general_error
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/taxchain.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

app = FastAPI(title="TaxChain API", version="1.0.0")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event - tables are already created
@app.on_event("startup")
async def startup_event():
    # Import all models to ensure they're loaded
    from app.models import (
        User,
        Wallet,
        Transaction,
        CostBasisLot,
        TaxEvent,
        Subscription,
    )

    logger.info("TaxChain API started successfully")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions globally."""
    error_response = handle_general_error(exc, "global_exception_handler")
    return JSONResponse(
        status_code=error_response.status_code, content=error_response.detail
    )


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(wallets.router, prefix="/api/wallets", tags=["wallets"])
app.include_router(
    transactions.router, prefix="/api/transactions", tags=["transactions"]
)
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])


@app.get("/")
async def root():
    return {"message": "TaxChain API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
