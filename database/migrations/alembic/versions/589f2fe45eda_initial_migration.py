"""Added RNA seq expression tables and experiment table

Revision ID: 589f2fe45eda
Revises: 
Create Date: 2025-01-01 20:43:30.596215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '589f2fe45eda'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'experiments',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('experiment_name', sa.String, nullable=True),
        sa.Column('description', sa.Text, nullable=True)
    )

    # Create the gene_expressions table
    op.create_table(
        'gene_expressions',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('treatment', sa.String, nullable=False),
        sa.Column('time', sa.Integer, nullable=False),
        sa.Column('replicate', sa.Integer, nullable=False),
        sa.Column('normalised_expression', sa.Float, nullable=False),
        sa.Column('log2_expression', sa.Float, nullable=False),
        sa.Column('meta_data', sa.Text, nullable=True),
        sa.Column('experiment_id', sa.Integer, sa.ForeignKey('experiments.id'), nullable=False),
        sa.Column('species_id', sa.Integer, sa.ForeignKey('species.id'), nullable=False),
        sa.Column('gene_id', sa.Integer, sa.ForeignKey('genes.id'), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('gene_expressions')
    op.drop_table('experiments')
