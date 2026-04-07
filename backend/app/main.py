from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alembic.config import Config
from alembic import command
from app.config import settings
from app.database import engine, Base
from app.routers import auth, wallets, transactions, reports

app = FastAPI(title="TaxChain API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Run Alembic database migrations
@app.on_event("startup")
async def startup_event():
    # Import all models so Alembic can discover them
    from app.models import (
        User,
        Wallet,
        Transaction,
        CostBasisLot,
        TaxEvent,
        Subscription,
    )

    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    # Run migrations using async engine
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: command.upgrade(
                alembic_cfg, "head", sqlalchemy_connection=sync_conn
            )
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
