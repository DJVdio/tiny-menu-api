"""remove_nickname_from_users

Revision ID: ac215c8b5b3c
Revises: 1e04f2532bb5
Create Date: 2025-11-07 11:41:56.187459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac215c8b5b3c'
down_revision: Union[str, None] = '1e04f2532bb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove nickname column from users table
    op.drop_column('users', 'nickname')


def downgrade() -> None:
    # Add nickname column back to users table
    op.add_column('users', sa.Column('nickname', sa.String(length=100), nullable=False))
