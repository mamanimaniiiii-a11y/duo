"""project description meta and user username

Revision ID: 004_project_meta_username
Revises: 003_mentor_skills
Create Date: 2026-03-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.services.username import slugify_username_base

revision: str = "004_project_meta_username"
down_revision: Union[str, None] = "003_mentor_skills"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    description_format = postgresql.ENUM(
        "short",
        "standard",
        "detailed",
        "custom",
        name="project_description_format",
        create_type=False,
    )
    learner_complexity = postgresql.ENUM(
        "beginner",
        "intermediate",
        "advanced",
        name="learner_complexity_level",
        create_type=False,
    )
    description_format.create(bind, checkfirst=True)
    learner_complexity.create(bind, checkfirst=True)

    op.add_column(
        "projects",
        sa.Column(
            "description_format",
            description_format,
            nullable=False,
            server_default="standard",
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "learner_complexity_level",
            learner_complexity,
            nullable=False,
            server_default="beginner",
        ),
    )

    op.add_column("users", sa.Column("username", sa.String(length=30), nullable=True))

    session = sa.orm.Session(bind=bind)
    users = session.execute(sa.text("SELECT id, display_name, email FROM users")).fetchall()
    taken: set[str] = set()
    for user_id, display_name, email in users:
        base = slugify_username_base(display_name or email.split("@", 1)[0])
        candidate = base
        suffix = 1
        while candidate in taken:
            suffix += 1
            tail = f"_{suffix}"
            candidate = f"{base[: 30 - len(tail)]}{tail}"
        taken.add(candidate)
        session.execute(
            sa.text("UPDATE users SET username = :username WHERE id = :id"),
            {"username": candidate, "id": user_id},
        )
    session.commit()

    op.alter_column("users", "username", nullable=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "username")
    op.drop_column("projects", "learner_complexity_level")
    op.drop_column("projects", "description_format")
    bind = op.get_bind()
    postgresql.ENUM(name="learner_complexity_level").drop(bind, checkfirst=True)
    postgresql.ENUM(name="project_description_format").drop(bind, checkfirst=True)
