"""Move annotation columns from ArabidopsisHomologue table to Annotation table

Revision ID: 2f011382f81f
Revises: 8e6fd2f185fe
Create Date: 2025-02-18 23:52:43.615742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f011382f81f'
down_revision: Union[str, None] = '8e6fd2f185fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.drop_column('arabidopsis_homologues', 'description')
    op.drop_column('arabidopsis_homologues', 'bit_score')
    op.drop_column('arabidopsis_homologues', 'similarity')
    op.drop_column('arabidopsis_homologues', 'e_value')
    op.drop_column('arabidopsis_homologues', 'alignment_length')
    op.drop_column('arabidopsis_homologues', 'positives')

    op.add_column('annotations', sa.Column("similarity",sa.Float(), nullable=True))
    op.add_column('annotations', sa.Column("bit_score",sa.Float(), nullable=True))
    op.add_column('annotations', sa.Column("alignment_length",sa.Integer(), nullable=True))
    op.add_column('annotations', sa.Column("positives",sa.Integer(), nullable=True))

def downgrade() -> None:
    op.add_column('arabidopsis_homologues', sa.Column('alignment_length', sa.INTEGER(), nullable=True))
    op.add_column('arabidopsis_homologues', sa.Column('e_value', sa.FLOAT(), nullable=True))
    op.add_column('arabidopsis_homologues', sa.Column('similarity', sa.FLOAT(), nullable=True))
    op.add_column('arabidopsis_homologues', sa.Column('bit_score', sa.FLOAT(), nullable=True))
    op.add_column('arabidopsis_homologues', sa.Column('description', sa.TEXT(), nullable=True))
    op.add_column('arabidopsis_homologues', sa.Column('positives', sa.INTEGER(), nullable=True))

    op.drop_column('annotations', 'similarity')
    op.drop_column('annotations', 'bit_score')
    op.drop_column('annotations', 'alignment_length')
    op.drop_column('annotations', 'positives')
    
    
    