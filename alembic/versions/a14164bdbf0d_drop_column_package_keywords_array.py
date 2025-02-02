"""drop column package.keywords_array

Revision ID: a14164bdbf0d
Revises: 76ed9efd00a8
Create Date: 2024-11-29 12:19:11.365714

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a14164bdbf0d"
down_revision: Union[str, None] = "76ed9efd00a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("package", "keywords_array")


def downgrade() -> None:
    op.add_column(
        "package",
        sa.Column("keywords_array", sa.ARRAY(sa.String()), nullable=True),
    )
