"""Add chef customer binding table

Revision ID: add_binding_table
Revises: 89efe187623a
Create Date: 2025-11-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_binding_table'
down_revision: Union[str, None] = '89efe187623a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create chef_customer_bindings table
    op.create_table('chef_customer_bindings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chef_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='bindingstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['chef_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chef_customer_bindings_id'), 'chef_customer_bindings', ['id'], unique=False)


def downgrade() -> None:
    # Drop chef_customer_bindings table
    op.drop_index(op.f('ix_chef_customer_bindings_id'), table_name='chef_customer_bindings')
    op.drop_table('chef_customer_bindings')
