"""Add uniprot and At gene locus id

Revision ID: 3805dd78c874
Revises: 3315ec7abbf1
Create Date: 2024-09-15 15:52:00.010251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3805dd78c874'
down_revision: Union[str, None] = '3315ec7abbf1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('gene_info', sa.Column("uniprot_id", sa.Float))
    op.add_column('gene_info', sa.Column("At_locus_id", sa.Float))
    op.add_column('gene_info', sa.Column("Protein_name", sa.Float))


def downgrade() -> None:
    op.drop_column('gene_info', "uniprot_id")
    op.drop_column('gene_info', "At_locus_id")
    op.drop_column('gene_info', "Protein_name")