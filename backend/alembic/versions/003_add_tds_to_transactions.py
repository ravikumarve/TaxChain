from alembic import op
import sqlalchemy as sa

revision = '003_add_tds_to_transactions'
down_revision = '002_add_cost_basis_method'


def upgrade():
    op.add_column('transactions', sa.Column('tds_usd', sa.DECIMAL(20, 8), server_default='0'))


def downgrade():
    op.drop_column('transactions', 'tds_usd')
