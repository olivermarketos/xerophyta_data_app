"""Move At genes to own table

Revision ID: c51aa94055dd
Revises: c51c5c7bd0e3
Create Date: 2024-09-30 21:03:54.819361

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c51aa94055dd'
down_revision: Union[str, None] = 'c51c5c7bd0e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("gene_info","At_gene_name")
    op.drop_column("gene_info","At_locus_id")
   
   # Create the arabidopsis_gene_names table
    op.create_table(
        'At_gene_names',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('gene_name', sa.String, sa.ForeignKey('gene_info.gene_name')),
        sa.Column('at_gene_name', sa.String, nullable=False),
    )

    # Create the arabidopsis_gene_loci table
    op.create_table(
        'At_gene_loci',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('gene_name', sa.String, sa.ForeignKey('gene_info.gene_name')),
        sa.Column('at_gene_loci', sa.String),
    )


def downgrade() -> None:
    # Add the columns back to gene_info
    op.add_column('gene_info', sa.Column('At_gene_name', sa.String))
    op.add_column('gene_info', sa.Column('At_loci_id', sa.String))

    # Drop the arabidopsis_gene_names and arabidopsis_gene_loci tables
    op.drop_table('At_gene_names')
    op.drop_table('At_gene_loci')
