"""add project_id to mentor_packs

Revision ID: 002_pack_project
Revises: 001_initial
Create Date: 2026-03-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_pack_project"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "mentor_packs",
        sa.Column("project_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_mentor_packs_project_id",
        "mentor_packs",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_mentor_packs_project_id"), "mentor_packs", ["project_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_mentor_packs_project_id"), table_name="mentor_packs")
    op.drop_constraint("fk_mentor_packs_project_id", "mentor_packs", type_="foreignkey")
    op.drop_column("mentor_packs", "project_id")
