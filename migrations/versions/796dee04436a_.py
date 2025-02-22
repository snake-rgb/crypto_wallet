"""empty message

Revision ID: 796dee04436a
Revises: 568a0cbd9e2a
Create Date: 2023-08-15 13:50:00.837537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from src.core.database import Base


# revision identifiers, used by Alembic.
revision: str = '796dee04436a'
down_revision: Union[str, None] = '568a0cbd9e2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'orders', ['id'])
    op.drop_constraint('orders_return_transaction_id_fkey', 'orders', type_='foreignkey')
    op.drop_column('orders', 'return_transaction_id')
    op.create_unique_constraint(None, 'products', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'products', type_='unique')
    op.add_column('orders', sa.Column('return_transaction_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('orders_return_transaction_id_fkey', 'orders', 'transactions', ['return_transaction_id'], ['id'])
    op.drop_constraint(None, 'orders', type_='unique')
    # ### end Alembic commands ###
