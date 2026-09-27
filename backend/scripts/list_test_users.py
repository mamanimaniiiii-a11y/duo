"""Liste les comptes *@test.duo.dz avec email, rôle et locale."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.user import User


def main() -> None:
    db = SessionLocal()
    users = db.scalars(
        select(User).where(User.email.like("%@test.duo.dz")).order_by(User.email)
    ).all()

    if not users:
        print("Aucun compte *@test.duo.dz trouvé.")
        return

    print(f"{'email':<30} {'role':<12} {'locale':<6} {'active':<6} id")
    print("-" * 90)
    for user in users:
        print(
            f"{user.email:<30} {user.role.value:<12} {user.locale.value:<6} "
            f"{str(user.is_active):<6} {user.id}"
        )
    db.close()


if __name__ == "__main__":
    main()
