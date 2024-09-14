"""Remove unused columns

Revision ID: 3315ec7abbf1
Revises: b70c2fa95df1
Create Date: 2024-09-14 16:28:34.167710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3315ec7abbf1'
down_revision: Union[str, None] = 'b70c2fa95df1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("gene_info","protein")
    op.drop_column("gene_info","blast_taxonomy")
    op.drop_column("gene_info","annotation_GO_ID")
    op.drop_column("gene_info","enzyme_code")
    op.drop_column("gene_info","enzyme_name")
    op.drop_column("gene_info","annotation_GO_term")
    op.drop_column("gene_info","interPro_accession")
    op.drop_column("gene_info","interPro_name")
    op.drop_column("gene_info","aa_sequence")
    op.drop_column("gene_info","arabidopsis_homolog")
    op.drop_column("gene_info","Sequence_length")
    


def downgrade() -> None:
    pass
