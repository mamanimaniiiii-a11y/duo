"""
Tests ciblés des endpoints IA (découpage tâches).

Prérequis :
  - API en cours d'exécution (uvicorn) OU utiliser --direct pour appeler le service sans HTTP
  - OPENAI_API_KEY dans backend/.env (fichier enregistré sur disque) + redémarrage uvicorn
  - Projet mentor en statut assigned/in_progress

Variables d'environnement (optionnelles) :
  API_BASE_URL          défaut http://127.0.0.1:8000/api/v1
  TEST_MENTOR_EMAIL     défaut mentor@test.5ibra.dz
  TEST_API_PASSWORD     défaut TestPass123!
  TEST_AI_PROJECT_ID    défaut 23c67abf-0730-4678-a360-9c20705a44e6
  TEST_AI_LOCALES       défaut ar,fr,en (séparées par des virgules)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from uuid import UUID

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

# Charger TEST_* depuis .env si présent
_env_path = BACKEND_ROOT / ".env"
if _env_path.exists():
    for line in _env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("TEST_") and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")
MENTOR_EMAIL = os.getenv("TEST_MENTOR_EMAIL", "mentor@test.5ibra.dz")
PASSWORD = os.getenv("TEST_API_PASSWORD", "TestPass123!")
PROJECT_ID = os.getenv(
    "TEST_AI_PROJECT_ID", "23c67abf-0730-4678-a360-9c20705a44e6"
)
LOCALES = [loc.strip() for loc in os.getenv("TEST_AI_LOCALES", "ar,fr,en").split(",") if loc.strip()]


def request_json(
    method: str,
    path: str,
    *,
    token: str | None = None,
    data: dict | None = None,
    form: dict | None = None,
    timeout: float = 180,
) -> tuple[int, dict | list | str]:
    url = f"{API_BASE}{path}"
    body = None
    headers: dict[str, str] = {}
    if form is not None:
        body = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode()
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = raw
        return exc.code, payload


def login() -> str:
    status, payload = request_json(
        "POST",
        "/auth/login",
        form={"username": MENTOR_EMAIL, "password": PASSWORD},
    )
    if status != 200:
        raise RuntimeError(f"Login échoué ({status}) : {payload}")
    return payload["access_token"]


def set_locale(token: str, locale: str) -> None:
    status, payload = request_json("PATCH", "/account", token=token, data={"locale": locale})
    if status != 200:
        raise RuntimeError(f"PATCH /account locale={locale} échoué ({status}) : {payload}")
    if payload.get("locale") != locale:
        raise RuntimeError(f"Locale attendue {locale}, obtenue {payload.get('locale')}")


def preview_breakdown(token: str, project_id: str) -> dict:
    status, payload = request_json(
        "POST",
        f"/ai/projects/{project_id}/task-breakdown",
        token=token,
    )
    if status != 200:
        raise RuntimeError(f"Preview échoué ({status}) : {payload}")
    return payload


def validate_breakdown(payload: dict, locale: str) -> list[str]:
    errors: list[str] = []
    tasks = payload.get("suggested_tasks")
    if not isinstance(tasks, list):
        errors.append("suggested_tasks manquant ou invalide")
        return errors
    if not (3 <= len(tasks) <= 8):
        errors.append(f"nombre de tâches hors plage 3-8 : {len(tasks)}")
    sort_orders = [t.get("sort_order") for t in tasks]
    if sorted(sort_orders) != list(range(len(tasks))):
        errors.append(f"sort_order non consécutifs : {sort_orders}")
    for i, task in enumerate(tasks):
        criteria = task.get("acceptance_criteria") or []
        if not (2 <= len(criteria) <= 5):
            errors.append(f"tâche {i} : {len(criteria)} critères (attendu 2-5)")
        for c in criteria:
            if len(c) < 10:
                errors.append(f"tâche {i} : critère trop court ({len(c)} chars)")
    # Heuristique légère : l'arabe contient souvent des caractères arabiques
    if locale == "ar":
        sample = " ".join(
            str(task.get("title", "")) + " " + str(task.get("description", ""))
            for task in tasks
        )
        if not any("\u0600" <= ch <= "\u06ff" for ch in sample):
            errors.append("locale=ar mais peu/pas de caractères arabiques détectés (relecture humaine requise)")
    return errors


def run_http_tests(locales: list[str], project_id: str, apply: bool) -> int:
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.openai_api_key:
        print("ERREUR : OPENAI_API_KEY absente du .env chargé par l'API.")
        print("→ Enregistrez backend/.env (Ctrl+S) puis redémarrez uvicorn.")
        return 1

    print(f"API        : {API_BASE}")
    print(f"Mentor     : {MENTOR_EMAIL}")
    print(f"Projet     : {project_id}")
    print(f"Locales    : {', '.join(locales)}")
    print(f"Modèle IA  : {settings.ai_model}")
    print()

    token = login()
    status, account = request_json("GET", "/account", token=token)
    print(f"Connecté   : {account.get('email')} (role={account.get('role')})")
    if account.get("role") != "mentor":
        print("ERREUR : le token ne correspond pas à un compte mentor.")
        return 1

    failures = 0
    last_preview: dict | None = None

    for locale in locales:
        print(f"\n--- locale={locale} ---")
        set_locale(token, locale)
        try:
            preview = preview_breakdown(token, project_id)
            last_preview = preview
            errors = validate_breakdown(preview, locale)
            task_count = len(preview.get("suggested_tasks", []))
            print(f"OK preview : {task_count} tâches")
            if errors:
                failures += 1
                for err in errors:
                    print(f"  WARN/ERR : {err}")
            else:
                print("  validation structurelle : OK")
        except RuntimeError as exc:
            failures += 1
            print(f"ERREUR : {exc}")

    if apply and last_preview and failures == 0:
        print("\n--- apply (dernière locale testée) ---")
        status, created = request_json(
            "POST",
            f"/ai/projects/{project_id}/task-breakdown/apply",
            token=token,
            data={"suggested_tasks": last_preview["suggested_tasks"]},
        )
        if status == 201:
            print(f"OK apply : {len(created)} tâches créées")
        else:
            failures += 1
            print(f"ERREUR apply ({status}) : {created}")

    print(f"\n=== Résumé : {failures} échec(s) ===")
    return 1 if failures else 0


def run_direct_preview(locale: str, project_id: str) -> int:
    """Appelle le service Python directement (bypass HTTP / uvicorn)."""
    from sqlalchemy import select

    from app.core.config import get_settings
    from app.core.database import SessionLocal
    from app.models.enums import Locale
    from app.models.user import User
    from app.services.ai.task_breakdown import generate_task_breakdown_preview

    get_settings.cache_clear()
    settings = get_settings()
    if not settings.openai_api_key:
        print("ERREUR : OPENAI_API_KEY absente du .env sur disque.")
        return 1

    db = SessionLocal()
    mentor = db.scalar(select(User).where(User.email == MENTOR_EMAIL))
    if not mentor:
        print(f"ERREUR : mentor introuvable ({MENTOR_EMAIL})")
        return 1
    mentor.locale = Locale(locale)
    db.commit()

    result = generate_task_breakdown_preview(db, UUID(project_id), mentor)
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))
    db.close()
    return 0


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Tests endpoints IA découpage tâches")
    parser.add_argument(
        "--locales",
        default=",".join(LOCALES),
        help="Locales à tester (ex. ar,fr,en)",
    )
    parser.add_argument("--project-id", default=PROJECT_ID)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Appliquer le dernier preview réussi (crée des tâches en base)",
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Appel service direct (1 locale via --locales), sans HTTP",
    )
    args = parser.parse_args()
    locales = [x.strip() for x in args.locales.split(",") if x.strip()]

    if args.direct:
        locale = locales[0] if locales else "ar"
        raise SystemExit(run_direct_preview(locale, args.project_id))

    raise SystemExit(run_http_tests(locales, args.project_id, args.apply))


if __name__ == "__main__":
    main()
