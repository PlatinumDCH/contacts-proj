"""degrade table contacta date bith

Revision ID: ff700fb09fa7
Revises: 925e491cb6dc
Create Date: 2024-12-22 22:31:26.375682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff700fb09fa7'
down_revision: Union[str, None] = '925e491cb6dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contacts', 'date_birthday')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('date_birthday', sa.DATE(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
