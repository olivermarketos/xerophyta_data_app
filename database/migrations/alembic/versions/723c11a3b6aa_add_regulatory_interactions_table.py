"""add_regulatory_interactions_table

Revision ID: 723c11a3b6aa
Revises: 2f011382f81f
Create Date: 2025-06-02 18:12:48.921480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '723c11a3b6aa'
down_revision: Union[str, None] = '2f011382f81f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('regulatory_interactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('regulator_gene_id', sa.Integer(), nullable=False),
    sa.Column('target_gene_id', sa.Integer(), nullable=False),
    sa.Column('regulatory_cluster', sa.String(), nullable=True),
    sa.Column('target_cluster', sa.String(), nullable=True),
    # For SQLite, Enum translates to String with a CHECK constraint usually
    sa.Column('direction', sa.Enum('Activation', 'Repression', 'Unknown', name='regulation_direction_enum'), nullable=False),
    sa.ForeignKeyConstraint(['regulator_gene_id'], ['genes.id'], name=op.f('fk_regulatory_interactions_regulator_gene_id_genes')), # Name might differ
    sa.ForeignKeyConstraint(['target_gene_id'], ['genes.id'], name=op.f('fk_regulatory_interactions_target_gene_id_genes')),     # Name might differ
    sa.PrimaryKeyConstraint('id', name=op.f('pk_regulatory_interactions')),
    sa.UniqueConstraint('regulator_gene_id', 'target_gene_id', name='uq_regulator_target_pair') # Should pick up your __table_args__
    )
    # Note: The changes to the Gene model (the relationships) don't directly translate to
    # op commands for the 'genes' table itself, as they are ORM constructs that
    # rely on the 'regulatory_interactions' table's foreign keys.
    # Autogenerate focuses on schema: tables, columns, indexes, constraints.
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('regulatory_interactions')
    # If the Enum created a TYPE (common in PostgreSQL, not directly in SQLite),
    # you might need to drop it, but for SQLite, sa.Enum usually just makes a VARCHAR + CHECK.
    # Autogenerate for sa.Enum on SQLite usually handles this correctly by not needing a separate type drop.
    # e.g. for PostgreSQL you might see: op.execute("DROP TYPE regulation_direction_enum")
    # ### end Alembic commands ###

