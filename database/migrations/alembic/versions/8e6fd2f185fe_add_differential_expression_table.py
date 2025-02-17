"""Add differential_expression table

Revision ID: 8e6fd2f185fe
Revises: a4be4a33d690
Create Date: 2025-01-05 14:21:29.149955

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e6fd2f185fe'
down_revision: Union[str, None] = 'a4be4a33d690'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'differential_expression',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('gene_id', sa.Integer, sa.ForeignKey('genes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('experiment_id', sa.Integer, sa.ForeignKey('experiments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('re_set', sa.String, nullable=True),
        sa.Column('re_direction', sa.String, nullable=True),
        sa.Column('de_set', sa.String, nullable=True),
        sa.Column('de_direction', sa.String, nullable=True)
    )

    # Optional: Add indexes for faster querying
    op.create_index('ix_differential_expression_gene_id', 'differential_expression', ['gene_id'])
    op.create_index('ix_differential_expression_experiment_id', 'differential_expression', ['experiment_id'])



def downgrade() -> None:
    op.drop_index('ix_differential_expression_gene_id', table_name='differential_expression')
    op.drop_index('ix_differential_expression_experiment_id', table_name='differential_expression')
    op.drop_table('differential_expression')