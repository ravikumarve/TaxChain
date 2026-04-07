from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


# Create database tables
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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
