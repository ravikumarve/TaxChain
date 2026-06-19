"""
Background Job Scheduler
Manages periodic tasks: wallet sync, price cache warming, subscription expiry.
Uses APScheduler (async) — installed but was never wired up.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.wallet import Wallet
from app.models.user import User
from app.models.subscription import Subscription
from app.services.chain_sync import fetch_transactions_with_retry, transform_transaction
from app.services.price_engine import clear_price_cache
from app.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def sync_wallet_job(wallet_id: str, user_id: str, address: str, chain: str) -> None:
    """
    Sync a single wallet's transactions.
    Called by the scheduler for periodic auto-sync.
    """
    try:
        from app.database import async_session
        from app.models.transaction import Transaction

        logger.info(
            "Auto-syncing wallet %s (%s) on %s for user %s",
            wallet_id, address, chain, user_id,
        )

        txs = await fetch_transactions_with_retry(address, chain)

        async with async_session() as db:
            # Deduplicate by tx_hash
            existing = await db.execute(
                select(Transaction.tx_hash).where(
                    Transaction.wallet_id == wallet_id
                )
            )
            existing_hashes = {row[0] for row in existing.fetchall()}

            new_count = 0
            for raw_tx in txs:
                tx_hash = raw_tx.get("tx_hash", "")
                if tx_hash and tx_hash not in existing_hashes:
                    tx = Transaction(
                        wallet_id=wallet_id,
                        user_id=user_id,
                        chain=chain,
                        **raw_tx,
                    )
                    db.add(tx)
                    new_count += 1

            await db.commit()
            logger.info(
                "Synced wallet %s: %d new transactions", wallet_id, new_count
            )

    except Exception as e:
        logger.error("Failed to auto-sync wallet %s: %s", wallet_id, str(e))


async def sync_all_wallets() -> None:
    """
    Periodic job: sync all wallets that haven't been synced in 6+ hours.
    Runs every 6 hours via scheduler.
    """
    logger.info("Starting scheduled sync of all wallets...")
    cutoff = datetime.utcnow() - timedelta(hours=6)

    try:
        async with async_session() as db:
            result = await db.execute(
                select(Wallet).where(
                    (Wallet.last_synced_at == None) | (Wallet.last_synced_at < cutoff)
                )
            )
            wallets = result.scalars().all()

        if not wallets:
            logger.info("No wallets need syncing")
            return

        logger.info("Found %d wallets to sync", len(wallets))

        for wallet in wallets:
            await sync_wallet_job(
                wallet_id=str(wallet.id),
                user_id=str(wallet.user_id),
                address=wallet.address,
                chain=wallet.chain,
            )

        logger.info("Scheduled wallet sync complete")

    except Exception as e:
        logger.error("Scheduled wallet sync failed: %s", str(e))


async def expire_subscriptions() -> None:
    """
    Periodic job: check for expired subscriptions and downgrade users.
    Runs every hour via scheduler.
    """
    logger.info("Checking for expired subscriptions...")

    try:
        async with async_session() as db:
            # Find active subscriptions past their period end
            result = await db.execute(
                select(Subscription).where(
                    Subscription.status == "active",
                    Subscription.current_period_end < datetime.utcnow(),
                )
            )
            expired = result.scalars().all()

            if not expired:
                logger.info("No expired subscriptions found")
                return

            logger.info("Found %d expired subscriptions", len(expired))

            for sub in expired:
                sub.status = "expired"
                # Downgrade user to free plan
                await db.execute(
                    update(User)
                    .where(User.id == sub.user_id)
                    .values(plan="free")
                )
                logger.info(
                    "Expired subscription %s for user %s, downgraded to free",
                    sub.id, sub.user_id,
                )

            await db.commit()
            logger.info("Subscription expiry check complete")

    except Exception as e:
        logger.error("Subscription expiry check failed: %s", str(e))


async def warm_price_cache() -> None:
    """
    Periodic job: clear stale price cache so frequently-requested
    tokens stay fresh in memory. Runs every 24 hours.
    """
    logger.info("Warming price cache...")
    clear_price_cache()
    logger.info("Price cache cleared (will re-populate on next request)")


def start_scheduler() -> None:
    """Register and start all background jobs."""
    if scheduler.running:
        logger.warning("Scheduler already running")
        return

    # Wallet auto-sync every 6 hours
    scheduler.add_job(
        sync_all_wallets,
        IntervalTrigger(hours=6),
        id="wallet_auto_sync",
        name="Auto-sync all stale wallets",
        replace_existing=True,
        max_instances=1,
    )

    # Subscription expiry check every hour
    scheduler.add_job(
        expire_subscriptions,
        IntervalTrigger(hours=1),
        id="subscription_expiry",
        name="Check for expired subscriptions",
        replace_existing=True,
        max_instances=1,
    )

    # Price cache warming every 24 hours
    scheduler.add_job(
        warm_price_cache,
        IntervalTrigger(hours=24),
        id="price_cache_warm",
        name="Clear stale price cache",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    logger.info(
        "Background scheduler started with 3 jobs: wallet_sync (6h), "
        "subscription_expiry (1h), price_cache (24h)"
    )


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Background scheduler shut down")
