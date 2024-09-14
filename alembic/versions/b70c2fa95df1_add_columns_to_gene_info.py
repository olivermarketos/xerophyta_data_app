"""Add columns to gene_info

Revision ID: b70c2fa95df1
Revises: 
Create Date: 2024-09-14 12:30:49.769969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b70c2fa95df1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('gene_info', sa.Column("Similarity", sa.Float))
    op.add_column('gene_info', sa.Column("Bit_Score", sa.Float))
    op.add_column('gene_info', sa.Column("Alignment_length", sa.Integer))
    op.add_column('gene_info', sa.Column("Positives", sa.Integer))


def downgrade() -> None:
    op.drop_column('gene_info', "Similarity")
    op.drop_column('gene_info', "Bit_Score")
    op.drop_column('gene_info', "Alignment_length")
    op.drop_column('gene_info', "Positives")