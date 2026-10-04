"""add user role

Revision ID: 4c675ae641b0
Revises: 975fd6ca7f0b
Create Date: 2026-09-29 16:10:59.748324

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "4c675ae641b0"
down_revision: Union[str, Sequence[str], None] = "975fd6ca7f0b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role_enum = postgresql.ENUM(
        "CUSTOMER",
        "SELLER",
        "ADMIN",
        name="userrole",
    )

    user_role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            nullable=False,
            server_default="CUSTOMER",
        ),
    )

    op.alter_column(
        "users",
        "role",
        server_default=None,
    )


def downgrade() -> None:
    user_role_enum = postgresql.ENUM(
        "CUSTOMER",
        "SELLER",
        "ADMIN",
        name="userrole",
    )

    op.drop_column("users", "role")

    user_role_enum.drop(op.get_bind(), checkfirst=True)