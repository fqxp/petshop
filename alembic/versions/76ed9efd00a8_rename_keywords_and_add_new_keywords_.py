"""rename keywords and add new keywords with string type

Revision ID: 76ed9efd00a8
Revises: 27019706082b
Create Date: 2024-11-29 10:26:50.413608

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "76ed9efd00a8"
down_revision: Union[str, None] = "27019706082b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name="package",
        column_name="keywords",
        new_column_name="keywords_array",
    )
    op.add_column(
        "package",
        sa.Column("keywords", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade() -> None:
    op.alter_column(
        table_name="package",
        column_name="keywords_array",
        new_column_name="keywords",
    )
    op.drop_column("package", "keywords")
