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
    conn = op.get_bind()

    action_type_exists = conn.execute(
        "SELECT 1 FROM pg_type WHERE typname = 'action_type'"
    ).scalar()
    membership_status_exists = conn.execute(
        "SELECT 1 FROM pg_type WHERE typname = 'membership_status'"
    ).scalar()

    if not action_type_exists:
        action_type = sa.Enum("INVITE", "REQUEST", name="action_type")
        action_type.create(op.get_bind())

    if not membership_status_exists:
        membership_status = sa.Enum(
            "ACCEPTED", "PENDING", "CANCELLED", "REJECTED", name="membership_status"
        )
        membership_status.create(op.get_bind())
    else:
        membership_status = sa.Enum(name="membership_status")

    inspector = sa.inspect(conn)

    if not inspector.has_table("company_associations"):
        op.create_table(
            "company_associations",
            sa.Column(
                "id",
                sa.UUID(),
                server_default=sa.text("gen_random_uuid()"),
                nullable=False,
            ),
            sa.Column("company_id", sa.UUID(), nullable=False),
            sa.Column("user_id", sa.UUID(), nullable=False),
            sa.Column("role", sa.String(), nullable=False, server_default="user"),
            sa.Column(
                "status", membership_status, nullable=False, server_default="PENDING"
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
            sa.ForeignKeyConstraint(
                ["company_id"], ["companies.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("company_id", "user_id", name="uq_company_user"),
        )
    else:
        if not inspector.has_column("company_associations", "role"):
            op.add_column(
                "company_associations",
                sa.Column("role", sa.String(), nullable=False, server_default="user"),
            )

    if not inspector.has_table("company_actions"):
        op.create_table(
            "company_actions",
            sa.Column(
                "id",
                sa.UUID(),
                server_default=sa.text("gen_random_uuid()"),
                nullable=False,
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
            sa.ForeignKeyConstraint(
                ["performed_by_id"], ["users.id"], ondelete="SET NULL"
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    index_definitions = [
        ("ix_company_associations_company_id", "company_associations", ["company_id"]),
        ("ix_company_associations_user_id", "company_associations", ["user_id"]),
        ("ix_company_associations_status", "company_associations", ["status"]),
        ("ix_company_actions_association_id", "company_actions", ["association_id"]),
    ]

    for index_name, table_name, columns in index_definitions:
        if inspector.has_table(table_name) and not inspector.has_index(
            table_name, index_name
        ):
            op.create_index(index_name, table_name, columns)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if inspector.has_table("company_actions"):
        op.drop_table("company_actions")

    if inspector.has_table("company_associations"):
        op.drop_table("company_associations")

    action_type_exists = conn.execute(
        "SELECT 1 FROM pg_type WHERE typname = 'action_type'"
    ).scalar()
    membership_status_exists = conn.execute(
        "SELECT 1 FROM pg_type WHERE typname = 'membership_status'"
    ).scalar()

    if action_type_exists:
        op.execute("DROP TYPE IF EXISTS action_type CASCADE;")

    if membership_status_exists:
        op.execute("DROP TYPE IF EXISTS membership_status CASCADE;")
