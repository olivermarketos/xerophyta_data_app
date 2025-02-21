"""Add species_id to experiments

Revision ID: a4be4a33d690
Revises: aeea982a9429
Create Date: 2025-01-03 22:29:35.416814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4be4a33d690'
down_revision: Union[str, None] = 'aeea982a9429'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table('experiments', schema=None) as batch_op:
        # First, add the new column (no FK yet)
        batch_op.add_column(sa.Column('species_id', sa.Integer(), nullable=True))
        
        # Now create a separate FK constraint
        batch_op.create_foreign_key(
            'fk_experiments_species_id',    # Constraint name
            'species',                      # Referenced table
            ['species_id'],                 # Local columns
            ['id']                          # Referenced columns
        )

def downgrade():
    with op.batch_alter_table('experiments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_experiments_species_id', type_='foreignkey')
        batch_op.drop_column('species_id')