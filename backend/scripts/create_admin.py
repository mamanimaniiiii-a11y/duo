"""Crée un compte admin (à lancer une seule fois après migration)."""

import sys
from getpass import getpass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.enums import Locale, UserRole
from app.models.user import User


def main() -> None:
    email = input("Email admin: ").strip().lower()
    display_name = input("Nom affiché: ").strip()
    password = getpass("Mot de passe: ")

    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            print("Un utilisateur existe déjà avec cet email.")
            return

        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            display_name=display_name,
            locale=Locale.FR,
            onboarding_completed=True,
        )
        db.add(user)
        db.commit()
        print(f"Admin créé : {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
