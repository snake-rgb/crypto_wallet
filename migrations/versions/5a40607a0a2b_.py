"""empty message

Revision ID: 5a40607a0a2b
Revises: abb0cfa6a0b4
Create Date: 2023-10-03 09:16:10.656611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from src.core.database import Base


# revision identifiers, used by Alembic.
revision: str = '5a40607a0a2b'
down_revision: Union[str, None] = 'abb0cfa6a0b4'
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
