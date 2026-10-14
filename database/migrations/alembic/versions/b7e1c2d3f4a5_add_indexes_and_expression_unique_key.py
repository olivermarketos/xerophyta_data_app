"""add indexes and unique key on gene_expressions, link experiments to species

Revision ID: b7e1c2d3f4a5
Revises: aded5eaefd2d
Create Date: 2026-10-14 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e1c2d3f4a5'
down_revision: Union[str, None] = 'aded5eaefd2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # gene_expressions had no indexes, so every expression query scanned the whole table
    op.create_index('ix_gene_expressions_gene_id', 'gene_expressions', ['gene_id'])
    op.create_index('ix_gene_expressions_experiment_id', 'gene_expressions', ['experiment_id'])

    # One value per gene/sample within an experiment. A unique index enforces this in SQLite
    # without rebuilding the table. Stops a load from silently overwriting another experiment's rows.
    op.create_index(
        'uq_gene_expressions_experiment_gene_sample',
        'gene_expressions',
        ['experiment_id', 'gene_id', 'treatment', 'time', 'replicate'],
        unique=True,
    )

    # regulator_gene_id is already covered by uq_regulator_target_pair
    op.create_index('ix_regulatory_interactions_target_gene_id', 'regulatory_interactions', ['target_gene_id'])
    op.create_index('ix_regulatory_interactions_regulatory_cluster', 'regulatory_interactions', ['regulatory_cluster'])

    op.create_index('ix_genes_species_id', 'genes', ['species_id'])

    # experiments.species_id is now the link used by the app (was NULL for the X. elegans experiment)
    op.execute(
        """
        UPDATE experiments
        SET species_id = (SELECT id FROM species WHERE name = 'X. elegans')
        WHERE experiment_name = 'xe_seedlings_time_course' AND species_id IS NULL
        """
    )


def downgrade() -> None:
    op.drop_index('ix_genes_species_id', table_name='genes')
    op.drop_index('ix_regulatory_interactions_regulatory_cluster', table_name='regulatory_interactions')
    op.drop_index('ix_regulatory_interactions_target_gene_id', table_name='regulatory_interactions')
    op.drop_index('uq_gene_expressions_experiment_gene_sample', table_name='gene_expressions')
    op.drop_index('ix_gene_expressions_experiment_id', table_name='gene_expressions')
    op.drop_index('ix_gene_expressions_gene_id', table_name='gene_expressions')
