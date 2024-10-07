"""Upgrade to At homologues

Revision ID: d06379be805e
Revises: c51aa94055dd
Create Date: 2024-10-02 18:21:14.114396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd06379be805e'
down_revision: Union[str, None] = 'c51aa94055dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    

    # Create the arabidopsis_homologues table
    op.create_table(
        'arabidopsis_homologues',
        sa.Column('arabidopsis_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('accession_number', sa.String(), nullable=True, unique=True),
        sa.Column('at_locus', sa.String(), nullable=True),
    )

    # Create the common_names table
    op.create_table(
        'At_common_names',
        sa.Column('common_name_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('arabidopsis_id', sa.Integer(), sa.ForeignKey('arabidopsis_homologues.arabidopsis_id')),
    )

    # Create the many-to-many association table between xe_genes and arabidopsis_homologues
    op.create_table(
        'xe_gene_homologue_link',
        sa.Column('gene_name', sa.Integer(), sa.ForeignKey('gene_info.gene_names')),
        sa.Column('arabidopsis_id', sa.Integer(), sa.ForeignKey('arabidopsis_homologues.arabidopsis_id')),
        sa.PrimaryKeyConstraint('gene_name', 'arabidopsis_id')
    )



def downgrade() -> None:
    # Drop the new tables (in reverse order)
    op.drop_table('xe_gene_homologue_link')
    op.drop_table('At_common_names')
    op.drop_table('arabidopsis_homologues')
