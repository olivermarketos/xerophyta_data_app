"""View current schema

Revision ID: aeea982a9429
Revises: 589f2fe45eda
Create Date: 2025-01-01 21:02:54.479232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'aeea982a9429'
down_revision: Union[str, None] = '589f2fe45eda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Check if the column already exists
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("experiments")]

    if "species_id" not in columns:
        op.add_column(
            "experiments",
            sa.Column("species_id", sa.Integer(), nullable=False, server_default="1")
        )
        op.alter_column("experiments", "species_id", server_default=None)

def downgrade():
    op.drop_column("experiments", "species_id")

