"""добавил полле date_birthday в модель контакты

Revision ID: f4ce4315d87e
Revises: 7e7ac79cf9c8
Create Date: 2024-12-24 13:08:37.957431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4ce4315d87e'
down_revision: Union[str, None] = '7e7ac79cf9c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('date_birthday', sa.Date(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contacts', 'date_birthday')
    # ### end Alembic commands ###
