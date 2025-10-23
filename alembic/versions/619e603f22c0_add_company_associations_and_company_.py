"""add company_associations and company_actions

Revision ID: 619e603f22c0
Revises: 000_initial_full
Create Date: 2025-10-22 21:15:46.757092

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "619e603f22c0"
down_revision: Union[str, Sequence[str], None] = "000_initial_full"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    action_type = sa.Enum(
        "CREATE", "UPDATE", "DELETE", "INVITE", "REMOVE", name="action_type"
    )
    action_type.create(op.get_bind(), checkfirst=True)
    membership_status = sa.Enum(
        "MEMBER", "INVITED", "REQUESTED", name="membership_status"
    )
    membership_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "company_associations",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "status", membership_status, nullable=False, server_default="REQUESTED"
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "company_actions",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("association_id", sa.UUID(), nullable=False),
        sa.Column("action_type", action_type, nullable=False),
        sa.Column("performed_by_id", sa.UUID(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["association_id"], ["company_associations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["performed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS action_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS membership_status CASCADE;")
