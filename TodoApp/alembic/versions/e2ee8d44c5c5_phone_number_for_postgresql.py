"""Phone Number for Postgresql

Revision ID: e2ee8d44c5c5
Revises: 4a9a09c2dafc
Create Date: 2025-07-29 14:49:31.307341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2ee8d44c5c5'
down_revision: Union[str, Sequence[str], None] = '4a9a09c2dafc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(length=11), nullable=True))



def downgrade() -> None:
    """Downgrade schema."""
    pass
