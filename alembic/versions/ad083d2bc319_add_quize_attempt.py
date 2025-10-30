"""add quize_attempt

Revision ID: ad083d2bc319
Revises: 9ee4f563fde1
Create Date: 2025-10-30 19:19:21.568592

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ad083d2bc319"
down_revision: Union[str, Sequence[str], None] = "9ee4f563fde1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quiz_attempts",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("quiz_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quiz_attempts_id"), "quiz_attempts", ["id"], unique=False)
    op.create_table(
        "user_answers",
        sa.Column("attempt_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["attempt_id"], ["quiz_attempts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_answers_id"), "user_answers", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_answers_id"), table_name="user_answers")
    op.drop_table("user_answers")
    op.drop_index(op.f("ix_quiz_attempts_id"), table_name="quiz_attempts")
    op.drop_table("quiz_attempts")
