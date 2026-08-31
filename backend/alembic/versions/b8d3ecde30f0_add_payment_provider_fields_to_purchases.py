"""add_payment_provider_fields_to_purchases

Revision ID: b8d3ecde30f0
Revises: 71614ead67f4
Create Date: 2026-08-31 14:10:13.258608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8d3ecde30f0'
down_revision: Union[str, None] = '71614ead67f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add payment provider fields to purchases table
    op.add_column('purchases', sa.Column('payment_provider_tx_id', sa.String(length=255), nullable=True))
    op.add_column('purchases', sa.Column('payment_method', sa.String(length=50), nullable=True))
    op.add_column('purchases', sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Create index on payment_provider_tx_id for webhook lookup performance
    op.create_index(op.f('ix_purchases_payment_provider_tx_id'), 'purchases', ['payment_provider_tx_id'], unique=False)


def downgrade() -> None:
    # Remove index first
    op.drop_index(op.f('ix_purchases_payment_provider_tx_id'), table_name='purchases')

    # Remove columns
    op.drop_column('purchases', 'updated_at')
    op.drop_column('purchases', 'payment_method')
    op.drop_column('purchases', 'payment_provider_tx_id')
