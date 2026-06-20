"""add cost_basis_method to users

Revision ID: 002_add_cost_basis_method
Revises: 001_initial_tables
Create Date: 2026-06-20 14:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_add_cost_basis_method"
down_revision: Union[str, None] = "001_initial_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("cost_basis_method", sa.String(10), server_default="fifo"),
    )


def downgrade() -> None:
    op.drop_column("users", "cost_basis_method")
