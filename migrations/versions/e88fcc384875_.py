"""empty message

Revision ID: e88fcc384875
Revises: 6e3e54bce19f
Create Date: 2023-08-26 14:53:47.443974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from src.core.database import Base


# revision identifiers, used by Alembic.
revision: str = 'e88fcc384875'
down_revision: Union[str, None] = '6e3e54bce19f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
