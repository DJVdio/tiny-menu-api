"""optimize_indexes_and_remove_redundant_indexes

Revision ID: 93568cae3e57
Revises: ac215c8b5b3c
Create Date: 2025-11-07 14:22:21.934749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93568cae3e57'
down_revision: Union[str, None] = 'ac215c8b5b3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 删除旧的冗余索引
    # users表 - 保留username索引，移除id上的index=True（主键自带索引）
    op.drop_index('ix_users_id', table_name='users')

    # dishes表 - 移除旧索引
    op.drop_index('ix_dishes_id', table_name='dishes')
    op.drop_index('ix_dishes_name', table_name='dishes')

    # customer_selections表 - 移除旧索引
    op.drop_index('ix_customer_selections_id', table_name='customer_selections')
    op.drop_index('ix_customer_selections_date', table_name='customer_selections')

    # chef_selections表 - 移除旧索引
    op.drop_index('ix_chef_selections_id', table_name='chef_selections')
    op.drop_index('ix_chef_selections_date', table_name='chef_selections')

    # chef_customer_bindings表 - 移除旧索引
    op.drop_index('ix_chef_customer_bindings_id', table_name='chef_customer_bindings')

    # daily_recommendations表 - 移除旧索引
    op.drop_index('ix_daily_recommendations_id', table_name='daily_recommendations')
    op.drop_index('ix_daily_recommendations_date', table_name='daily_recommendations')

    # 创建新的优化索引
    # users表
    op.create_index('idx_username', 'users', ['username'])

    # dishes表
    op.create_index('idx_name', 'dishes', ['name'])
    op.create_index('idx_category', 'dishes', ['category'])

    # chef_customer_bindings表 - 复合索引
    op.create_index('idx_chef_status', 'chef_customer_bindings', ['chef_id', 'status'])
    op.create_index('idx_customer_chef', 'chef_customer_bindings', ['customer_id', 'chef_id'])
    op.create_index('idx_chef_customer_status', 'chef_customer_bindings', ['chef_id', 'customer_id', 'status'])

    # customer_selections表 - 复合索引
    op.create_index('idx_user_date', 'customer_selections', ['user_id', 'date'])
    op.create_index('idx_date_user', 'customer_selections', ['date', 'user_id'])
    op.create_index('idx_user_dish_date', 'customer_selections', ['user_id', 'dish_id', 'date'])

    # chef_selections表 - 复合索引
    op.create_index('idx_chef_date', 'chef_selections', ['chef_id', 'date'])
    op.create_index('idx_chef_customer_selection', 'chef_selections', ['chef_id', 'customer_selection_id', 'date'])

    # daily_recommendations表 - 复合索引
    op.create_index('idx_date', 'daily_recommendations', ['date'])
    op.create_index('idx_date_dish', 'daily_recommendations', ['date', 'dish_id'])


def downgrade() -> None:
    # 删除新索引
    op.drop_index('idx_username', table_name='users')
    op.drop_index('idx_name', table_name='dishes')
    op.drop_index('idx_category', table_name='dishes')
    op.drop_index('idx_chef_status', table_name='chef_customer_bindings')
    op.drop_index('idx_customer_chef', table_name='chef_customer_bindings')
    op.drop_index('idx_chef_customer_status', table_name='chef_customer_bindings')
    op.drop_index('idx_user_date', table_name='customer_selections')
    op.drop_index('idx_date_user', table_name='customer_selections')
    op.drop_index('idx_user_dish_date', table_name='customer_selections')
    op.drop_index('idx_chef_date', table_name='chef_selections')
    op.drop_index('idx_chef_customer_selection', table_name='chef_selections')
    op.drop_index('idx_date', table_name='daily_recommendations')
    op.drop_index('idx_date_dish', table_name='daily_recommendations')

    # 恢复旧索引
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_dishes_id', 'dishes', ['id'])
    op.create_index('ix_dishes_name', 'dishes', ['name'])
    op.create_index('ix_customer_selections_id', 'customer_selections', ['id'])
    op.create_index('ix_customer_selections_date', 'customer_selections', ['date'])
    op.create_index('ix_chef_selections_id', 'chef_selections', ['id'])
    op.create_index('ix_chef_selections_date', 'chef_selections', ['date'])
    op.create_index('ix_chef_customer_bindings_id', 'chef_customer_bindings', ['id'])
    op.create_index('ix_daily_recommendations_id', 'daily_recommendations', ['id'])
    op.create_index('ix_daily_recommendations_date', 'daily_recommendations', ['date'])
