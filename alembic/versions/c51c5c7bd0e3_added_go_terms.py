"""Added GO terms

Revision ID: c51c5c7bd0e3
Revises: 
Create Date: 2024-09-23 18:18:01.237870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c51c5c7bd0e3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
# Create the go_terms table
    op.create_table(
        'go_terms',
        sa.Column('go_id', sa.String, primary_key=True),
        sa.Column('go_name', sa.String),
        sa.Column('go_category', sa.String),
    )

    # Create the gene_to_go table
    op.create_table(
        'gene_to_go',
        sa.Column('gene_name', sa.String, sa.ForeignKey('gene_info.gene_name')),
        sa.Column('go_id', sa.String, sa.ForeignKey('go_terms.go_id')),
    )

    # Create the enzymes table
    op.create_table(
        'enzymes',
        sa.Column('enzyme_code', sa.String, primary_key=True),
        sa.Column('enzyme_name', sa.String),
    )

    # Create the gene_to_enzyme table
    op.create_table(
        'gene_to_enzyme',
        sa.Column('gene_name', sa.String, sa.ForeignKey('gene_info.gene_name')),
        sa.Column('enzyme_code', sa.String, sa.ForeignKey('enzymes.enzyme_code')),
    )

    # Create the interpro table
    op.create_table(
        'interpro',
        sa.Column('interpro_id', sa.String, primary_key=True),
        sa.Column('interpro_name', sa.String),
    )

    # Create the gene_to_interpro table
    op.create_table(
        'gene_to_interpro',
        sa.Column('gene_name', sa.String, sa.ForeignKey('gene_info.gene_name')),
        sa.Column('interpro_id', sa.String, sa.ForeignKey('interpro.interpro_id')),
    )

def downgrade():
    # Drop tables in reverse order to avoid foreign key constraint issues
    op.drop_table('gene_to_interpro')
    op.drop_table('interpro')
    op.drop_table('gene_to_enzyme')
    op.drop_table('enzymes')
    op.drop_table('gene_to_go')
    op.drop_table('go_terms')        
