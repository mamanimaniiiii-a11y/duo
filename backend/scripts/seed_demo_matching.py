"""
Crée les comptes démo matching + projet ML pour Nouara Haifi.

Prérequis : API sur http://127.0.0.1:8000

Usage :
  python scripts/seed_demo_matching.py
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000/api/v1"
PASSWORD = "TestPass123!"

MENTORS = [
    {
        "email": "rania.boughella@duo.dz",
        "display_name": "Rania Boughella",
        "username": "rania_boughella",
        "skills": ["Python", "Machine Learning", "TensorFlow", "Data Science", "Pandas"],
        "bio": "Mentor data science et machine learning.",
        "score": 88,
    },
    {
        "email": "djalil.boughella@duo.dz",
        "display_name": "Djalil Boughella",
        "username": "djalil_boughella",
        "skills": ["React", "Node.js", "DevOps", "Docker", "TypeScript"],
        "bio": "Mentor développement web et DevOps.",
        "score": 62,
    },
]

CLIENT = {
    "email": "nouara.haifi@duo.dz",
    "display_name": "Nouara Haifi",
    "username": "nouara_haifi",
}

PROJECT = {
    "title": "Plateforme de prédiction et Machine Learning",
    "description": (
        "Contexte : une startup souhaite prédire la demande clients à partir de données historiques.\n\n"
        "Objectif : construire un pipeline ML (nettoyage, entraînement, évaluation, déploiement).\n\n"
        "Livrables : modèle de prédiction, API Python, dashboard de métriques, documentation.\n\n"
        "Compétences mentor : Python, Machine Learning, TensorFlow, Scikit-learn, Data Science.\n\n"
        "Niveau apprenants : intermédiaire. Délai : 8 semaines."
    ),
    "required_skills": [
        "Python",
        "Machine Learning",
        "TensorFlow",
        "Scikit-learn",
        "Data Science",
    ],
    "budget_dzd": 120000,
}


def request(method: str, path: str, data: dict | None = None, form: dict | None = None, token: str | None = None):
    body = None
    headers = {}
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    elif form is not None:
        body = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(f"{BASE}{path}", data=body, method=method, headers=headers)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read().decode()
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"detail": raw}
        return exc.code, payload


def login(email: str) -> str:
    status, payload = request("POST", "/auth/login", form={"username": email, "password": PASSWORD})
    if status != 200:
        raise RuntimeError(f"Login {email} failed ({status}): {payload}")
    return payload["access_token"]


def register_or_skip(email: str, display_name: str, role: str, username: str) -> None:
    status, payload = request(
        "POST",
        "/auth/register",
        data={
            "email": email,
            "password": PASSWORD,
            "display_name": display_name,
            "role": role,
            "username": username,
        },
    )
    if status == 201:
        print(f"  créé : {email}")
    elif status == 409:
        print(f"  existe déjà : {email}")
    else:
        raise RuntimeError(f"Register {email} failed ({status}): {payload}")


def recalculate_mentor_score(email: str) -> None:
    try:
        from sqlalchemy import select

        from app.core.database import SessionLocal
        from app.models.user import User
        from app.services.score_service import recalculate_mentor_score as compute_score

        db = SessionLocal()
        user = db.scalar(select(User).where(User.email == email.lower()))
        if not user:
            print(f"  score {email}: utilisateur introuvable")
            return
        breakdown = compute_score(db, user)
        print(f"  score {email}: {breakdown.total} (formule §5bis.2)")
        db.close()
    except Exception as exc:
        print(f"  score {email}: non recalculé ({exc})")


def setup_mentor(mentor: dict) -> None:
    register_or_skip(mentor["email"], mentor["display_name"], "mentor", mentor["username"])
    token = login(mentor["email"])
    request("POST", "/account/onboarding/complete", token=token, data={})
    status, payload = request(
        "PATCH",
        "/account/mentor-profile",
        token=token,
        data={"bio": mentor["bio"], "skills": mentor["skills"]},
    )
    if status != 200:
        raise RuntimeError(f"Mentor profile {mentor['email']} failed: {payload}")
    print(f"  skills {mentor['email']}: {', '.join(mentor['skills'])}")
    recalculate_mentor_score(mentor["email"])


def main() -> None:
    print("=== Mentors démo ===")
    for mentor in MENTORS:
        setup_mentor(mentor)

    print("\n=== Client Nouara Haifi ===")
    register_or_skip(CLIENT["email"], CLIENT["display_name"], "client", CLIENT["username"])
    client_token = login(CLIENT["email"])
    request("POST", "/account/onboarding/complete", token=client_token, data={})

    status, categories = request("GET", "/public/categories")
    if status != 200 or not categories:
        raise RuntimeError("Impossible de charger les catégories")
    category_id = categories[0]["id"]

    status, project = request(
        "POST",
        "/client/projects",
        token=client_token,
        data={
            "title": PROJECT["title"],
            "description": PROJECT["description"],
            "description_format": "standard",
            "learner_complexity_level": "intermediate",
            "category_id": category_id,
            "budget_dzd": PROJECT["budget_dzd"],
            "required_skills": PROJECT["required_skills"],
        },
    )
    if status != 201:
        raise RuntimeError(f"Création projet échouée: {project}")

    project_id = project["id"]
    status, published = request("POST", f"/client/projects/{project_id}/publish", token=client_token)
    if status != 200:
        raise RuntimeError(f"Publication échouée: {published}")

    status, matches = request("GET", f"/client/projects/{project_id}/mentor-matches", token=client_token)
    print(f"\n=== Projet publié : {PROJECT['title']} ===")
    print(f"ID projet : {project_id}")
    print(f"Statut : {published.get('status')}")
    print("\nClassement mentors :")
    if status == 200:
        for row in matches:
            mentor = row["mentor"]
            print(
                f"  - {mentor['display_name']} (@{mentor['username']}) "
                f": matching {row['match_score']}% "
                f"(skills {row.get('skills_match_percent', '?')}%, score mentor {row.get('mentor_score', mentor.get('score', 0))})"
            )

    print("\n=== Comptes ===")
    print(f"Client  : {CLIENT['email']} / {PASSWORD}")
    for mentor in MENTORS:
        print(f"Mentor  : {mentor['email']} / {PASSWORD}")
    print(f"\nURL client : http://localhost:3000/fr/client/projets/{project_id}")


if __name__ == "__main__":
    main()
