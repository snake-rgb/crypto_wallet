"""empty message

Revision ID: 3b0430396f8d
Revises: 8e97cee3063a
Create Date: 2023-08-26 11:22:41.232904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from src.core.database import Base


# revision identifiers, used by Alembic.
revision: str = '3b0430396f8d'
down_revision: Union[str, None] = '8e97cee3063a'
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
