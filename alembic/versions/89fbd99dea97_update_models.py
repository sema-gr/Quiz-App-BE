"""update models

Revision ID: 89fbd99dea97
Revises: 619e603f22c0
Create Date: 2025-10-23 15:21:12.146330

"""

from typing import Sequence, Union
from alembic import op

revision: str = "89fbd99dea97"
down_revision: Union[str, Sequence[str], None] = "619e603f22c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE membership_status_new AS ENUM ('active', 'pending')")
    op.execute(
        "ALTER TABLE company_associations ALTER COLUMN status TYPE membership_status_new USING status::text::membership_status_new"
    )
    op.execute("DROP TYPE membership_status CASCADE")
    op.execute("ALTER TYPE membership_status_new RENAME TO membership_status")
    op.execute("CREATE TYPE action_type_new AS ENUM ('invite', 'accept', 'remove')")
    op.execute(
        "ALTER TABLE company_actions ALTER COLUMN action_type TYPE action_type_new USING action_type::text::action_type_new"
    )
    op.execute("DROP TYPE action_type CASCADE")
    op.execute("ALTER TYPE action_type_new RENAME TO action_type")

    op.drop_table("company_members")


def downgrade() -> None:
    op.execute(
        "CREATE TYPE membership_status_old AS ENUM ('MEMBER', 'INVITED', 'REQUESTED')"
    )
    op.execute(
        "ALTER TABLE company_associations ALTER COLUMN status TYPE membership_status_old USING status::text::membership_status_old"
    )
    op.execute("DROP TYPE membership_status CASCADE")
    op.execute("ALTER TYPE membership_status_old RENAME TO membership_status")
    op.alter_column("company_associations", "status", server_default="REQUESTED")

    op.execute("CREATE TYPE action_type_old AS ENUM ('CREATE', 'UPDATE', 'DELETE')")
    op.execute(
        "ALTER TABLE company_actions ALTER COLUMN action_type TYPE action_type_old USING action_type::text::action_type_old"
    )
    op.execute("DROP TYPE action_type CASCADE")
    op.execute("ALTER TYPE action_type_old RENAME TO action_type")
