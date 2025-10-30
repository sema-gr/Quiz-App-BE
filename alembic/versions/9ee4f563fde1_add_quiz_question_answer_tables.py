"""Add quiz, question, answer tables

Revision ID: 9ee4f563fde1
Revises: 677112dd1709
Create Date: 2025-10-29 20:54:27.283205

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9ee4f563fde1"
down_revision: Union[str, Sequence[str], None] = "677112dd1709"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "quizzes",
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("max_attempts_per_user", sa.Integer(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quizzes_id"), "quizzes", ["id"], unique=False)
    op.create_table(
        "questions",
        sa.Column("quiz_id", sa.UUID(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_questions_id"), "questions", ["id"], unique=False)
    op.create_table(
        "answers",
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_answers_id"), "answers", ["id"], unique=False)
    op.create_index(op.f("ix_companies_id"), "companies", ["id"], unique=False)
    op.create_index(
        op.f("ix_company_actions_id"), "company_actions", ["id"], unique=False
    )
    op.drop_constraint(
        op.f("company_associations_company_id_user_id_key"),
        "company_associations",
        type_="unique",
    )
    op.create_index(
        op.f("ix_company_associations_id"), "company_associations", ["id"], unique=False
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_company_associations_id"), table_name="company_associations")
    op.create_unique_constraint(
        op.f("company_associations_company_id_user_id_key"),
        "company_associations",
        ["company_id", "user_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.drop_index(op.f("ix_company_actions_id"), table_name="company_actions")
    op.drop_index(op.f("ix_companies_id"), table_name="companies")
    op.drop_index(op.f("ix_answers_id"), table_name="answers")
    op.drop_table("answers")
    op.drop_index(op.f("ix_questions_id"), table_name="questions")
    op.drop_table("questions")
    op.drop_index(op.f("ix_quizzes_id"), table_name="quizzes")
    op.drop_table("quizzes")
