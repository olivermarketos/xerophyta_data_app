"""Dropping unnecessary tables

Revision ID: 2be50a4486db
Revises: d06379be805e
Create Date: 2024-10-07 21:15:46.642199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2be50a4486db'
down_revision: Union[str, None] = 'd06379be805e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('At_gene_loci')
    op.drop_table('At_gene_names')




def downgrade() -> None:
    pass
