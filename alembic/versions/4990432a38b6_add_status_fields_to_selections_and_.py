"""add_status_fields_to_selections_and_bindings

Revision ID: 4990432a38b6
Revises: 93568cae3e57
Create Date: 2025-11-07 14:31:39.978823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4990432a38b6'
down_revision: Union[str, None] = '93568cae3e57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 为 customer_selections 表添加 status 和 updated_at 字段
    op.add_column('customer_selections', sa.Column('status', sa.Enum('active', 'cancelled', name='selectionstatus'), nullable=False, server_default='active'))
    op.add_column('customer_selections', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    # 2. 为 chef_selections 表添加 status 和 updated_at 字段
    op.add_column('chef_selections', sa.Column('status', sa.Enum('active', 'cancelled', name='chefselectionstatus'), nullable=False, server_default='active'))
    op.add_column('chef_selections', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    # 3. 为 chef_customer_bindings 添加新的 unbound 状态值（MySQL 需要修改 ENUM 类型）
    # 注意：MySQL 修改 ENUM 需要使用 ALTER TABLE MODIFY COLUMN
    op.execute("ALTER TABLE chef_customer_bindings MODIFY COLUMN status ENUM('pending', 'approved', 'rejected', 'unbound') NOT NULL DEFAULT 'pending'")

    # 4. 更新索引：删除旧索引
    op.drop_index('idx_user_dish_date', table_name='customer_selections')
    op.drop_index('idx_chef_customer_selection', table_name='chef_selections')

    # 5. 创建包含 status 的新索引
    op.create_index('idx_user_dish_date_status', 'customer_selections', ['user_id', 'dish_id', 'date', 'status'])
    op.create_index('idx_chef_customer_selection_status', 'chef_selections', ['chef_id', 'customer_selection_id', 'date', 'status'])


def downgrade() -> None:
    # 删除新索引
    op.drop_index('idx_user_dish_date_status', table_name='customer_selections')
    op.drop_index('idx_chef_customer_selection_status', table_name='chef_selections')

    # 恢复旧索引
    op.create_index('idx_user_dish_date', 'customer_selections', ['user_id', 'dish_id', 'date'])
    op.create_index('idx_chef_customer_selection', 'chef_selections', ['chef_id', 'customer_selection_id', 'date'])

    # 恢复 chef_customer_bindings 的 ENUM 类型
    op.execute("ALTER TABLE chef_customer_bindings MODIFY COLUMN status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending'")

    # 删除 status 和 updated_at 字段
    op.drop_column('chef_selections', 'updated_at')
    op.drop_column('chef_selections', 'status')
    op.drop_column('customer_selections', 'updated_at')
    op.drop_column('customer_selections', 'status')
