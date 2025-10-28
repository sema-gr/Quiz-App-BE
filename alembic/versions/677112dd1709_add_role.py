"""add admin to role_type enum

Revision ID: 677112dd1709
Revises: 619e603f22c0
Create Date: 2025-10-27 17:41:09.619819
"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "677112dd1709"
down_revision: Union[str, Sequence[str], None] = "619e603f22c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    role_enum = postgresql.ENUM("owner", "admin", "member", name="role_type")
    role_enum.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    pass
