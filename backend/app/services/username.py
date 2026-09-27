import re
import unicodedata
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User

_USERNAME_RE = re.compile(r"^[a-z0-9_]{3,30}$")


def slugify_username_base(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_text.lower()).strip("_")
    slug = re.sub(r"_+", "_", slug)
    return (slug[:24] or "user")


def is_valid_username(value: str) -> bool:
    return bool(_USERNAME_RE.fullmatch(value))


def generate_unique_username(db: Session, display_name: str, email: str) -> str:
    base = slugify_username_base(display_name or email.split("@", 1)[0])
    candidate = base
    suffix = 1

    while db.scalar(select(User.id).where(User.username == candidate)) is not None:
        suffix += 1
        tail = f"_{suffix}"
        candidate = f"{base[: 30 - len(tail)]}{tail}"

    return candidate


def resolve_username(
    db: Session,
    *,
    requested: str | None,
    display_name: str,
    email: str,
    exclude_user_id: UUID | None = None,
) -> str:
    if requested:
        username = requested.strip().lower()
        if not is_valid_username(username):
            raise ValueError(
                "Le username doit contenir 3 à 30 caractères (lettres minuscules, chiffres, _)"
            )
        existing = db.scalar(select(User.id).where(User.username == username))
        if existing and existing != exclude_user_id:
            raise ValueError("Ce username est déjà pris")
        return username

    return generate_unique_username(db, display_name, email)
