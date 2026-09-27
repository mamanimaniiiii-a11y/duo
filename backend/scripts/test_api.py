"""
Test automatisé de tous les endpoints API Duo.

Prérequis : API lancée sur http://localhost:8000

Usage :
  python scripts/test_api.py

Configuration (variables d'environnement) :
  TEST_API_PASSWORD      — mot de passe client/mentor/apprenant (défaut : TestPass123!)
  TEST_CLIENT_EMAIL      — email compte client de test
  TEST_MENTOR_EMAIL      — email compte mentor de test
  TEST_APPRENANT_EMAIL   — email compte apprenant de test
  TEST_ADMIN_EMAIL       — email compte admin (aucun défaut : obligatoire pour /admin/*)
  TEST_ADMIN_PASSWORD    — mot de passe admin (défaut : TEST_API_PASSWORD si défini)
  API_BASE_URL           — défaut http://localhost:8000

Exemple PowerShell (admin réel) :
  $env:TEST_ADMIN_EMAIL="votre.email@example.com"
  $env:TEST_ADMIN_PASSWORD="votre-mot-de-passe"
  python scripts\\test_api.py
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

import requests

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _load_test_vars_from_dotenv() -> None:
    """Charge TEST_* depuis backend/.env si pas déjà dans l'environnement."""
    env_path = BACKEND_ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key.startswith("TEST_"):
            continue
        if key in os.environ:
            continue
        os.environ[key] = value.strip().strip('"').strip("'")


_load_test_vars_from_dotenv()

# --- Configuration (surchargeable via variables d'environnement) ---
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
API_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")
API_BASE = f"{BASE_URL}{API_PREFIX}"

TEST_PASSWORD = os.getenv("TEST_API_PASSWORD", "TestPass123!")
ADMIN_EMAIL = os.getenv("TEST_ADMIN_EMAIL", "").strip()
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD") or TEST_PASSWORD

ACCOUNTS = {
    "client": {
        "email": os.getenv("TEST_CLIENT_EMAIL", "client@test.duo.dz"),
        "display_name": "Client Test API",
        "role": "client",
    },
    "mentor": {
        "email": os.getenv("TEST_MENTOR_EMAIL", "mentor@test.duo.dz"),
        "display_name": "Mentor Test API",
        "role": "mentor",
    },
    "apprenant": {
        "email": os.getenv("TEST_APPRENANT_EMAIL", "apprenant@test.duo.dz"),
        "display_name": "Apprenant Test API",
        "role": "apprenant",
        "skills": ["Python", "React"],
        "career_goal": "Devenir développeur full-stack",
    },
    "admin": {
        "email": ADMIN_EMAIL,
        "display_name": "Admin API Test",
        "role": "admin",
    },
}


class ResultKind(str, Enum):
    OK = "OK"
    ERROR = "ERREUR"
    SKIP = "SKIP"


@dataclass
class TestResult:
    method: str
    path: str
    status: ResultKind
    status_code: int | None = None
    message: str = ""


@dataclass
class Context:
    tokens: dict[str, str] = field(default_factory=dict)
    refresh_tokens: dict[str, str] = field(default_factory=dict)
    user_ids: dict[str, str] = field(default_factory=dict)
    category_id: str | None = None
    project_id: str | None = None
    project_claimed: bool = False
    listing_id: str | None = None
    pack_id: str | None = None
    application_id: str | None = None
    boost_option_id: str | None = None
    premium_plan_id: str | None = None
    notification_id: str | None = None
    task_id: str | None = None
    admin_available: bool = False


def summarize_error(response: requests.Response) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            detail = data.get("detail")
            if isinstance(detail, list):
                return str(detail[0]) if detail else response.text[:120]
            if detail is not None:
                return str(detail)[:200]
        return response.text[:200]
    except (json.JSONDecodeError, ValueError):
        return (response.text or "")[:200]


def request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body: dict | None = None,
    params: dict | None = None,
    data: dict | None = None,
) -> requests.Response:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{API_BASE}{path}" if path.startswith("/") else f"{API_BASE}/{path}"
    return requests.request(
        method,
        url,
        headers=headers,
        json=json_body,
        params=params,
        data=data,
        timeout=30,
    )


def display_path(path: str) -> str:
    return f"{API_PREFIX}{path}" if path.startswith("/") else f"{API_PREFIX}/{path}"


def print_result(result: TestResult) -> None:
    code = result.status_code if result.status_code is not None else "—"
    line = f"{result.method:6} {display_path(result.path):58} -> {code:>3}  [{result.status.value}]"
    if result.message:
        line += f"  {result.message}"
    print(line)


def run_test(
    ctx: Context,
    method: str,
    path: str,
    *,
    role: str | None = None,
    token: str | None = None,
    json_body: dict | None = None,
    params: dict | None = None,
    data: dict | None = None,
    skip_if: Callable[[Context], str | None] | None = None,
    ok_codes: set[int] | None = None,
) -> TestResult:
    if skip_if:
        reason = skip_if(ctx)
        if reason:
            result = TestResult(method, path, ResultKind.SKIP, message=reason)
            print_result(result)
            return result

    auth_token = token
    if auth_token is None and role:
        auth_token = ctx.tokens.get(role)
        if not auth_token:
            result = TestResult(
                method,
                path,
                ResultKind.SKIP,
                message=f"pas de token pour le rôle {role}",
            )
            print_result(result)
            return result

    try:
        response = request(
            method,
            path,
            token=auth_token,
            json_body=json_body,
            params=params,
            data=data,
        )
    except requests.RequestException as exc:
        result = TestResult(method, path, ResultKind.ERROR, message=str(exc))
        print_result(result)
        return result

    allowed = ok_codes or {200, 201}
    if response.status_code in allowed:
        result = TestResult(method, path, ResultKind.OK, response.status_code)
    else:
        result = TestResult(
            method,
            path,
            ResultKind.ERROR,
            response.status_code,
            summarize_error(response),
        )
    print_result(result)
    return result


def register_or_reuse(ctx: Context, role: str) -> None:
    account = ACCOUNTS[role]
    if role == "admin":
        return

    payload = {
        "email": account["email"],
        "password": TEST_PASSWORD,
        "display_name": account["display_name"],
        "role": account["role"],
        "locale": "fr",
    }
    if role == "apprenant":
        payload["skills"] = account.get("skills", [])
        payload["career_goal"] = account.get("career_goal", "")

    response = request("POST", "/auth/register", json_body=payload)
    if response.status_code == 201:
        print(f"[setup] Compte {role} créé : {account['email']}")
    elif response.status_code == 409:
        print(f"[setup] Compte {role} existant : {account['email']}")
    else:
        print(f"[setup] Inscription {role} : {response.status_code} — {summarize_error(response)}")


def login_role(ctx: Context, role: str) -> bool:
    if role == "admin":
        email = ACCOUNTS["admin"]["email"]
        if not email:
            print("[setup] TEST_ADMIN_EMAIL non défini — endpoints /admin/* seront skippés")
            return False
        password = ADMIN_PASSWORD
    else:
        email = ACCOUNTS[role]["email"]
        password = TEST_PASSWORD

    response = request(
        "POST",
        "/auth/login",
        data={"username": email, "password": password},
    )
    if response.status_code != 200:
        print(f"[setup] Connexion {role} échouée : {summarize_error(response)}")
        return False

    data = response.json()
    ctx.tokens[role] = data["access_token"]
    ctx.refresh_tokens[role] = data["refresh_token"]

    me = request("GET", "/auth/me", token=ctx.tokens[role])
    if me.status_code == 200:
        ctx.user_ids[role] = me.json()["id"]
    print(f"[setup] Connecté en tant que {role} ({email})")
    return True


def seed_test_data(ctx: Context) -> None:
    print("\n[setup] Préparation des données de test…\n")

    categories = request("GET", "/public/categories")
    if categories.status_code == 200 and categories.json():
        ctx.category_id = categories.json()[0]["id"]

    if ctx.category_id and ctx.tokens.get("client"):
        project = request(
            "POST",
            "/client/projects",
            token=ctx.tokens["client"],
            json_body={
                "title": "Projet test API automatisé",
                "description": "Description suffisamment longue pour la validation du projet test.",
                "category_id": ctx.category_id,
                "budget_dzd": 50000,
            },
        )
        if project.status_code == 201:
            ctx.project_id = project.json()["id"]

    if ctx.tokens.get("mentor"):
        listing = request(
            "POST",
            "/mentor/recrutement/listings",
            token=ctx.tokens["mentor"],
            json_body={
                "title": "Annonce test API",
                "description": "Annonce de recrutement créée par le script de test automatisé.",
                "required_skills": ["Python"],
            },
        )
        if listing.status_code == 201:
            ctx.listing_id = listing.json()["id"]
            request(
                "PATCH",
                f"/mentor/recrutement/listings/{ctx.listing_id}",
                token=ctx.tokens["mentor"],
                json_body={"status": "open"},
            )

        pack = request(
            "POST",
            "/mentor/packs",
            token=ctx.tokens["mentor"],
            json_body={
                "title": "Pack test API",
                "description": "Pack d'accompagnement créé par le script de test automatisé.",
                "price_dzd": 15000,
                "duration_days": 30,
                "max_projects": 2,
                "features": ["Suivi hebdomadaire", "Revue de code"],
            },
        )
        if pack.status_code == 201:
            ctx.pack_id = pack.json()["id"]

        boost_options = request("GET", "/mentor/boost/options", token=ctx.tokens["mentor"])
        if boost_options.status_code == 200 and boost_options.json():
            ctx.boost_option_id = boost_options.json()[0]["id"]

    if ctx.listing_id and ctx.tokens.get("apprenant"):
        application = request(
            "POST",
            "/apprenant/applications",
            token=ctx.tokens["apprenant"],
            params={"listing_id": ctx.listing_id},
            json_body={
                "cover_letter": "Je souhaite rejoindre cette mission pour progresser sur des projets réels.",
            },
        )
        if application.status_code == 201:
            ctx.application_id = application.json()["id"]
        elif application.status_code == 409:
            apps = request(
                "GET",
                "/apprenant/activite/applications",
                token=ctx.tokens["apprenant"],
            )
            if apps.status_code == 200 and apps.json():
                ctx.application_id = apps.json()[0]["id"]

    missions = request("GET", "/apprenant/missions", token=ctx.tokens.get("apprenant"))
    if missions.status_code == 200 and missions.json():
        ctx.task_id = missions.json()[0]["id"]

    if ctx.admin_available:
        boost_admin = request(
            "GET",
            "/admin/boost-premium/boost-options",
            token=ctx.tokens["admin"],
        )
        if boost_admin.status_code == 200 and boost_admin.json():
            ctx.boost_option_id = boost_admin.json()[0]["id"]

        plans = request(
            "GET",
            "/admin/boost-premium/premium-plans",
            token=ctx.tokens["admin"],
        )
        if plans.status_code == 200 and plans.json():
            ctx.premium_plan_id = plans.json()[0]["id"]

        if not ctx.boost_option_id:
            created = request(
                "POST",
                "/admin/boost-premium/boost-options",
                token=ctx.tokens["admin"],
                json_body={
                    "label": {"fr": "Boost 7 jours", "en": "7-day boost", "ar": "تعزيز 7 أيام"},
                    "duration_days": 7,
                    "price_dzd": 5000,
                    "is_active": True,
                },
            )
            if created.status_code == 201:
                ctx.boost_option_id = created.json()["id"]


def run_all_tests(ctx: Context) -> list[TestResult]:
    results: list[TestResult] = []

    def add(method: str, path: str, **kwargs: Any) -> None:
        results.append(run_test(ctx, method, path, **kwargs))

    print("\n=== Tests des endpoints ===\n")

    # Santé
    health = requests.get(f"{BASE_URL}/health", timeout=10)
    hr = TestResult(
        "GET",
        "/health",
        ResultKind.OK if health.status_code == 200 else ResultKind.ERROR,
        health.status_code,
        "" if health.status_code == 200 else summarize_error(health),
    )
    print_result(hr)
    results.append(hr)

    # Auth (hors register/login déjà faits en setup)
    add("POST", "/auth/refresh", json_body={"refresh_token": ctx.refresh_tokens.get("client", "")})
    add("GET", "/auth/me", role="client")

    # Public
    add("GET", "/public/categories")
    add("GET", "/public/mentors")
    add(
        "GET",
        f"/public/mentors/{ctx.user_ids['mentor']}" if ctx.user_ids.get("mentor") else "/public/mentors/{id}",
        skip_if=lambda c: None if c.user_ids.get("mentor") else "pas de données",
    )
    add(
        "GET",
        f"/public/apprenants/{ctx.user_ids['apprenant']}" if ctx.user_ids.get("apprenant") else "/public/apprenants/{id}",
        skip_if=lambda c: None if c.user_ids.get("apprenant") else "pas de données",
    )
    add("GET", "/public/listings")
    add(
        "GET",
        f"/public/listings/{ctx.listing_id}" if ctx.listing_id else "/public/listings/{id}",
        skip_if=lambda c: None if c.listing_id else "pas de données",
    )

    # Account
    add("GET", "/account", role="client")
    add("PATCH", "/account", role="client", json_body={"display_name": "Client Test API"})
    add("PATCH", "/account/client-profile", role="client", json_body={"company_name": "Test SARL"})
    add("PATCH", "/account/mentor-profile", role="mentor", json_body={"bio": "Mentor de test API"})
    add("PATCH", "/account/apprenant-profile", role="apprenant", json_body={"skills": ["Python"]})
    add("POST", "/account/onboarding/complete", role="client", json_body={})

    # Client
    add("GET", "/client/dashboard", role="client")
    add("GET", "/client/projects", role="client")
    add(
        "POST",
        "/client/projects",
        role="client",
        json_body={
            "title": "Second projet test API",
            "description": "Autre projet créé pendant le test automatisé des endpoints.",
            "category_id": ctx.category_id or "",
            "budget_dzd": 25000,
        },
        skip_if=lambda c: None if c.category_id else "pas de données",
        ok_codes={200, 201},
    )
    add(
        "GET",
        f"/client/projects/{ctx.project_id}" if ctx.project_id else "/client/projects/{id}",
        role="client",
        skip_if=lambda c: None if c.project_id else "pas de données",
    )
    add(
        "PATCH",
        f"/client/projects/{ctx.project_id}" if ctx.project_id else "/client/projects/{id}",
        role="client",
        json_body={"title": "Projet test API mis à jour"},
        skip_if=lambda c: None if c.project_id else "pas de données",
    )
    add(
        "POST",
        f"/client/projects/{ctx.project_id}/publish" if ctx.project_id else "/client/projects/{id}/publish",
        role="client",
        skip_if=lambda c: None if c.project_id else "pas de données",
    )

    # Mentor — flux prise en charge (après publication client ci-dessus)
    add("GET", "/mentor/dashboard", role="mentor")
    add("GET", "/mentor/projects/disponibles", role="mentor")
    if ctx.project_id and ctx.tokens.get("mentor"):
        claim_resp = request(
            "POST",
            f"/mentor/projects/{ctx.project_id}/prendre-en-charge",
            token=ctx.tokens["mentor"],
        )
        claim_result = TestResult(
            "POST",
            f"/mentor/projects/{ctx.project_id}/prendre-en-charge",
            ResultKind.OK if claim_resp.status_code == 200 else ResultKind.ERROR,
            claim_resp.status_code,
            "" if claim_resp.status_code == 200 else summarize_error(claim_resp),
        )
        print_result(claim_result)
        results.append(claim_result)
        if claim_resp.status_code == 200:
            ctx.project_claimed = True
        elif claim_resp.status_code == 409:
            ctx.project_claimed = True
    else:
        skip = TestResult(
            "POST",
            "/mentor/projects/{id}/prendre-en-charge",
            ResultKind.SKIP,
            message="pas de données",
        )
        print_result(skip)
        results.append(skip)

    add("GET", "/mentor/projects", role="mentor")
    add(
        "GET",
        f"/mentor/projects/{ctx.project_id}" if ctx.project_id else "/mentor/projects/{id}",
        role="mentor",
        skip_if=lambda c: None if c.project_id and c.project_claimed else "projet non pris en charge",
    )
    add("GET", "/mentor/recrutement/listings", role="mentor")
    add(
        "POST",
        "/mentor/recrutement/listings",
        role="mentor",
        json_body={
            "title": "Annonce test API #2",
            "description": "Deuxième annonce créée par le script de test automatisé.",
            "required_skills": ["JavaScript"],
        },
        ok_codes={200, 201},
    )
    add(
        "PATCH",
        f"/mentor/recrutement/listings/{ctx.listing_id}" if ctx.listing_id else "/mentor/recrutement/listings/{id}",
        role="mentor",
        json_body={"title": "Annonce test API mise à jour"},
        skip_if=lambda c: None if c.listing_id else "pas de données",
    )
    add(
        "GET",
        f"/mentor/recrutement/listings/{ctx.listing_id}/applications" if ctx.listing_id else "/mentor/recrutement/listings/{id}/applications",
        role="mentor",
        skip_if=lambda c: None if c.listing_id else "pas de données",
    )
    add(
        "PATCH",
        f"/mentor/recrutement/applications/{ctx.application_id}" if ctx.application_id else "/mentor/recrutement/applications/{id}",
        role="mentor",
        json_body={"status": "pending"},
        skip_if=lambda c: None if c.application_id else "pas de données",
    )
    add("GET", "/mentor/apprenants", role="mentor")
    add("GET", "/mentor/packs", role="mentor")
    add(
        "POST",
        "/mentor/packs",
        role="mentor",
        json_body={
            "title": "Pack test API #2",
            "description": "Deuxième pack créé par le script de test automatisé.",
            "price_dzd": 20000,
            "duration_days": 60,
            "max_projects": 3,
            "features": ["Mentorat personnalisé"],
        },
        ok_codes={200, 201},
    )
    add(
        "PATCH",
        f"/mentor/packs/{ctx.pack_id}" if ctx.pack_id else "/mentor/packs/{id}",
        role="mentor",
        json_body={"title": "Pack test API mis à jour"},
        skip_if=lambda c: None if c.pack_id else "pas de données",
    )
    add("GET", "/mentor/boost/options", role="mentor")
    add(
        "POST",
        "/mentor/boost/subscribe",
        role="mentor",
        json_body={"boost_option_id": ctx.boost_option_id or ""},
        skip_if=lambda c: None if c.boost_option_id else "pas de données",
    )
    add(
        "POST",
        "/mentor/premium/subscribe",
        role="mentor",
        json_body={"plan_id": ctx.premium_plan_id or ""},
        skip_if=lambda c: None if c.premium_plan_id else "pas de données",
    )
    add("GET", "/mentor/progression", role="mentor")

    # Apprenant
    add("GET", "/apprenant/dashboard", role="apprenant")
    add("GET", "/apprenant/decouvrir/listings", role="apprenant")
    add(
        "POST",
        "/apprenant/applications",
        role="apprenant",
        params={"listing_id": ctx.listing_id or ""},
        json_body={
            "cover_letter": "Candidature de test automatisé pour vérifier l'endpoint applications.",
        },
        skip_if=lambda c: None if c.listing_id else "pas de données",
        ok_codes={200, 201, 409},
    )
    add("GET", "/apprenant/activite/applications", role="apprenant")
    add("GET", "/apprenant/missions", role="apprenant")
    add(
        "GET",
        f"/apprenant/missions/{ctx.task_id}" if ctx.task_id else "/apprenant/missions/{id}",
        role="apprenant",
        skip_if=lambda c: None if c.task_id else "pas de données",
    )
    add("GET", "/apprenant/packs", role="apprenant")
    add(
        "GET",
        f"/apprenant/packs/{ctx.pack_id}" if ctx.pack_id else "/apprenant/packs/{id}",
        role="apprenant",
        skip_if=lambda c: None if c.pack_id else "pas de données",
    )
    add(
        "POST",
        "/apprenant/packs/purchase",
        role="apprenant",
        json_body={"pack_id": ctx.pack_id or ""},
        skip_if=lambda c: None if c.pack_id else "pas de données",
        ok_codes={200, 201, 409},
    )
    add("GET", "/apprenant/packs/purchases", role="apprenant")
    add("GET", "/apprenant/progression", role="apprenant")

    # Reviews
    add(
        "GET",
        f"/reviews/user/{ctx.user_ids['mentor']}" if ctx.user_ids.get("mentor") else "/reviews/user/{id}",
        skip_if=lambda c: None if c.user_ids.get("mentor") else "pas de données",
    )
    add(
        "POST",
        "/reviews",
        role="client",
        json_body={
            "to_user_id": ctx.user_ids.get("mentor", ""),
            "project_id": ctx.project_id,
            "rating": 5,
            "comment": "Excellent travail de test.",
            "type": "client_to_mentor",
        },
        skip_if=lambda c: None if c.user_ids.get("mentor") else "pas de données",
        ok_codes={200, 201, 409},
    )

    # Common
    add("GET", "/messages", role="client")
    add(
        "POST",
        "/messages",
        role="client",
        params={
            "recipient_id": ctx.user_ids.get("mentor", ""),
            "content": "Message de test automatisé",
        },
        skip_if=lambda c: None if c.user_ids.get("mentor") else "pas de données",
    )
    add("GET", "/notifications", role="client")
    add("GET", "/notifications/unread-count", role="client")
    add(
        "PATCH",
        "/notifications/{notification_id}/read",
        role="client",
        skip_if=lambda c: "pas de données",
    )

    # Admin
    if ctx.admin_available:
        add("GET", "/admin/dashboard", role="admin")
        add("GET", "/admin/utilisateurs", role="admin")
        add(
            "PATCH",
            f"/admin/utilisateurs/{ctx.user_ids['apprenant']}/toggle-active" if ctx.user_ids.get("apprenant") else "/admin/utilisateurs/{id}/toggle-active",
            role="admin",
            skip_if=lambda c: None if c.user_ids.get("apprenant") else "pas de données",
        )
        add("GET", "/admin/litiges", role="admin")
        add("GET", "/admin/configuration/categories", role="admin")
        add(
            "POST",
            "/admin/configuration/categories",
            role="admin",
            json_body={
                "slug": f"test-api-{os.getpid()}",
                "name": {"fr": "Catégorie test", "en": "Test category", "ar": "فئة اختبار"},
                "sort_order": 99,
                "is_active": True,
            },
            ok_codes={200, 201, 409},
        )
        add(
            "PATCH",
            f"/admin/configuration/categories/{ctx.category_id}",
            role="admin",
            json_body={"sort_order": 1},
            skip_if=lambda c: None if c.category_id else "pas de données",
        )
        add("GET", "/admin/boost-premium/boost-options", role="admin")
        add("GET", "/admin/boost-premium/premium-plans", role="admin")
        add(
            "POST",
            "/admin/boost-premium/premium-plans",
            role="admin",
            json_body={
                "label": {"fr": "Premium test", "en": "Premium test", "ar": "بريميوم اختبار"},
                "price_dzd": 10000,
                "duration_days": 30,
                "benefits": ["Visibilité accrue"],
                "is_active": True,
            },
            ok_codes={200, 201},
        )
    else:
        for method, path in [
            ("GET", "/admin/dashboard"),
            ("GET", "/admin/utilisateurs"),
            ("GET", "/admin/litiges"),
            ("GET", "/admin/configuration/categories"),
            ("GET", "/admin/boost-premium/boost-options"),
            ("GET", "/admin/boost-premium/premium-plans"),
        ]:
            skip = TestResult(method, path, ResultKind.SKIP, message="admin non connecté")
            print_result(skip)
            results.append(skip)

    return results


def main() -> int:
    print(f"API cible : {BASE_URL}")
    print(f"Préfixe    : {API_PREFIX}\n")

    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
    except requests.RequestException:
        print(f"ERREUR : impossible de joindre {BASE_URL}/health")
        print("Lancez d'abord : uvicorn app.main:app --reload --port 8000")
        return 1

    ctx = Context()

    print("=== Setup comptes ===\n")
    for role in ("client", "mentor", "apprenant"):
        register_or_reuse(ctx, role)
        login_role(ctx, role)

    if login_role(ctx, "admin"):
        ctx.admin_available = True
    else:
        print("[setup] Admin non disponible — endpoints /admin/* seront skippés")
        print("         Définissez TEST_ADMIN_EMAIL et TEST_ADMIN_PASSWORD, puis relancez.")
        print("         Ou créez un admin : python scripts/create_admin.py\n")

    seed_test_data(ctx)
    results = run_all_tests(ctx)

    ok = sum(1 for r in results if r.status == ResultKind.OK)
    errors = sum(1 for r in results if r.status == ResultKind.ERROR)
    skipped = sum(1 for r in results if r.status == ResultKind.SKIP)

    print("\n=== Résumé ===")
    print(f"  OK      : {ok}")
    print(f"  ERREUR  : {errors}")
    print(f"  SKIP    : {skipped}")
    print(f"  TOTAL   : {len(results)}")

    if errors:
        print("\nEndpoints en erreur :")
        for r in results:
            if r.status == ResultKind.ERROR:
                print(f"  - {r.method} {r.path} ({r.status_code}) : {r.message}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
