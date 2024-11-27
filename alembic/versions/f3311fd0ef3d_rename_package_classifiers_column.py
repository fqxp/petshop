"""rename package.classifiers column

Revision ID: f3311fd0ef3d
Revises: f1ed49b3bdc5
Create Date: 2024-11-27 12:52:03.595082

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3311fd0ef3d"
down_revision: Union[str, None] = "f1ed49b3bdc5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name="package",
        column_name="classifiers",
        new_column_name="classifiers_array",
    )


def downgrade() -> None:
    op.alter_column(
        table_name="package",
        column_name="classifiers_array",
        new_column_name="classifiers",
    )
