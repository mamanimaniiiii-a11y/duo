"""
Supprime un utilisateur de la base Supabase et les données liées (CASCADE).

Usage :
  cd backend
  .\\.venv\\Scripts\\Activate.ps1
  python scripts/delete_user.py --email admin@test.5ibra.dz

  # Sans confirmation interactive :
  python scripts/delete_user.py --email admin@test.5ibra.dz --yes

Puis recréer l'admin :
  python scripts/create_admin.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, or_, select

from app.core.database import SessionLocal
from app.models.application import Application
from app.models.boost import BoostSubscription, PremiumSubscription
from app.models.listing import Listing
from app.models.pack import MentorPack, PackPurchase
from app.models.profile import ApprenantProfile, ClientProfile, MentorProfile
from app.models.project import Project, Task
from app.models.review import Review
from app.models.support import Dispute, Message, Notification
from app.models.user import User


def _count(db, model, *conditions) -> int:
    return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0


def summarize_related_data(db, user_id: UUID) -> dict[str, int]:
    """Compte les enregistrements liés (informatif avant suppression)."""
    uid = user_id
    return {
        "client_profile": _count(db, ClientProfile, ClientProfile.user_id == uid),
        "mentor_profile": _count(db, MentorProfile, MentorProfile.user_id == uid),
        "apprenant_profile": _count(db, ApprenantProfile, ApprenantProfile.user_id == uid),
        "projects_as_client": _count(db, Project, Project.client_id == uid),
        "projects_as_mentor": _count(db, Project, Project.mentor_id == uid),
        "tasks_assigned": _count(db, Task, Task.assigned_apprenant_id == uid),
        "listings": _count(db, Listing, Listing.mentor_id == uid),
        "applications": _count(db, Application, Application.apprenant_id == uid),
        "reviews_sent": _count(db, Review, Review.from_user_id == uid),
        "reviews_received": _count(db, Review, Review.to_user_id == uid),
        "mentor_packs": _count(db, MentorPack, MentorPack.mentor_id == uid),
        "pack_purchases_as_apprenant": _count(db, PackPurchase, PackPurchase.apprenant_id == uid),
        "pack_purchases_as_mentor": _count(db, PackPurchase, PackPurchase.mentor_id == uid),
        "boost_subscriptions": _count(db, BoostSubscription, BoostSubscription.mentor_id == uid),
        "premium_subscriptions": _count(db, PremiumSubscription, PremiumSubscription.mentor_id == uid),
        "notifications": _count(db, Notification, Notification.user_id == uid),
        "messages_sent": _count(db, Message, Message.sender_id == uid),
        "messages_received": _count(db, Message, Message.recipient_id == uid),
        "disputes_opened": _count(db, Dispute, Dispute.opened_by_id == uid),
        "disputes_against": _count(db, Dispute, Dispute.against_user_id == uid),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Supprime un utilisateur et ses données liées.")
    parser.add_argument(
        "--email",
        default="admin@test.5ibra.dz",
        help="Email de l'utilisateur à supprimer (défaut : admin@test.5ibra.dz)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirmer la suppression sans demander oui/non",
    )
    args = parser.parse_args()

    email = args.email.strip().lower()
    db = SessionLocal()

    try:
        user = db.scalar(select(User).where(User.email == email))
        if not user:
            print(f"Aucun utilisateur trouvé pour l'email : {email}")
            return 0

        print("Utilisateur trouvé :")
        print(f"  id           : {user.id}")
        print(f"  email        : {user.email}")
        print(f"  role         : {user.role.value}")
        print(f"  display_name : {user.display_name}")
        print(f"  is_active    : {user.is_active}")
        print(f"  created_at   : {user.created_at}")

        related = summarize_related_data(db, user.id)
        total_related = sum(related.values())
        print("\nDonnées liées (seront supprimées ou détachées par CASCADE / SET NULL) :")
        for key, count in related.items():
            if count:
                print(f"  - {key}: {count}")
        if total_related == 0:
            print("  (aucune donnée liée)")

        if not args.yes:
            answer = input(f"\nSupprimer définitivement {email} ? (oui/non) : ").strip().lower()
            if answer not in {"oui", "o", "yes", "y"}:
                print("Annulé.")
                return 1

        user_id = user.id
        db.delete(user)
        db.commit()

        still_there = db.scalar(select(User).where(User.email == email))
        if still_there:
            print("ERREUR : l'utilisateur est encore présent après suppression.")
            return 1

        print(f"\nOK — utilisateur supprimé : {email} (id={user_id})")
        print("Recréez le compte avec : python scripts/create_admin.py")
        return 0

    except Exception as exc:
        db.rollback()
        print(f"ERREUR lors de la suppression : {exc}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
