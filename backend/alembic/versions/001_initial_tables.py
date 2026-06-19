"""Initial tables

Revision ID: 001_initial_tables
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("plan", sa.String(20), server_default="free"),
        sa.Column("country", sa.String(10), server_default="IN"),
        sa.Column("financial_year_start", sa.String(5), server_default="04-01"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("NOW()")),
    )

    # Wallets table
    op.create_table(
        "wallets",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("chain", sa.String(20), nullable=False),
        sa.Column("label", sa.String(100)),
        sa.Column("last_synced_at", sa.TIMESTAMP()),
        sa.Column("tx_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()")),
    )

    # Transactions table
    op.create_table(
        "transactions",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "wallet_id", sa.UUID(), sa.ForeignKey("wallets.id", ondelete="CASCADE")
        ),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("tx_hash", sa.String(255), nullable=False),
        sa.Column("chain", sa.String(20), nullable=False),
        sa.Column("tx_type", sa.String(30), nullable=False),
        sa.Column("token_symbol", sa.String(50)),
        sa.Column("token_address", sa.String(255)),
        sa.Column("quantity", sa.Numeric(36, 18), nullable=False),
        sa.Column("price_usd", sa.Numeric(20, 8)),
        sa.Column("value_usd", sa.Numeric(20, 8)),
        sa.Column("fee_usd", sa.Numeric(20, 8)),
        sa.Column("timestamp", sa.TIMESTAMP(), nullable=False),
        sa.Column("raw_data", sa.JSONB()),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("tx_hash", "chain"),
    )

    # Cost basis lots table
    op.create_table(
        "cost_basis_lots",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("token_symbol", sa.String(50), nullable=False),
        sa.Column("chain", sa.String(20), nullable=False),
        sa.Column("quantity_remaining", sa.Numeric(36, 18), nullable=False),
        sa.Column("cost_per_unit_usd", sa.Numeric(20, 8), nullable=False),
        sa.Column("acquired_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("source_tx_id", sa.UUID(), sa.ForeignKey("transactions.id")),
    )

    # Tax events table
    op.create_table(
        "tax_events",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("token_symbol", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Numeric(36, 18), nullable=False),
        sa.Column("proceeds_usd", sa.Numeric(20, 8), nullable=False),
        sa.Column("cost_basis_usd", sa.Numeric(20, 8), nullable=False),
        sa.Column("gain_loss_usd", sa.Numeric(20, 8), nullable=False),
        sa.Column("is_short_term", sa.Boolean()),
        sa.Column("sale_tx_id", sa.UUID(), sa.ForeignKey("transactions.id")),
        sa.Column("acquired_at", sa.TIMESTAMP()),
        sa.Column("disposed_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("financial_year", sa.String(10)),
    )

    # Subscriptions table
    op.create_table(
        "subscriptions",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("provider_sub_id", sa.String(255)),
        sa.Column("plan", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("current_period_end", sa.TIMESTAMP()),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()")),
    )


def downgrade() -> None:
    op.drop_table("subscriptions")
    op.drop_table("tax_events")
    op.drop_table("cost_basis_lots")
    op.drop_table("transactions")
    op.drop_table("wallets")
    op.drop_table("users")
