"""
Matrice de tests reproductible pour l'analyse de lacunes (gap analysis §5.4).

Usage :
  python scripts/test_gap_analysis_matrix.py --prepare
  python scripts/test_gap_analysis_matrix.py --locales fr,ar,en
  python scripts/test_gap_analysis_matrix.py --dry-run   # affiche la matrice sans appeler l'IA
  python scripts/test_ai.py --gap-matrix --prepare       # raccourci via test_ai.py

Prérequis :
  - PostgreSQL accessible (DATABASE_URL dans backend/.env)
  - Clé IA configurée (GROQ_API_KEY ou OPENAI_API_KEY selon AI_PROVIDER)
  - Comptes apprenant@test.duo.dz (historique vide) et apprenant2@test.duo.dz (sparse)

Scénarios :
  a. Historique vide × catalogue vide × 3 locales
  b. Historique sparse × catalogue vide × 3 locales
  c. Catalogue pertinent (non vide) × 3 locales → IDs recommandés + idées vides
  d. Catalogue non pertinent × 3 locales → IDs vides + idées vides (garde-fou serveur)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

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

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.application import Application
from app.models.category import Category
from app.models.enums import (
    LearnerComplexityLevel,
    ListingStatus,
    Locale,
    ProjectStatus,
    UserRole,
)
from app.models.listing import Listing
from app.models.project import Project, Task
from app.models.user import User
from app.schemas.ai import AiGapRecommendation
from app.services.ai.ai_provider import resolve_ai_provider_config
from app.services.ai.gap_analysis import build_learner_gap_context, generate_gap_analysis

APPRENANT_EMPTY_EMAIL = os.getenv("TEST_GAP_EMPTY_EMAIL", "apprenant@test.duo.dz")
APPRENANT_SPARSE_EMAIL = os.getenv("TEST_GAP_SPARSE_EMAIL", "apprenant2@test.duo.dz")
DEFAULT_LOCALES = ["fr", "ar", "en"]
GAP_MATRIX_MARKER = "__GAP_MATRIX__"
RELEVANT_LISTING_TITLE = f"{GAP_MATRIX_MARKER} RELEVANT Python full-stack"
IRRELEVANT_LISTING_TITLE = f"{GAP_MATRIX_MARKER} IRRELEVANT Comptabilité Sage"


class CatalogMode(str, Enum):
    EMPTY = "empty"
    RELEVANT = "relevant"
    IRRELEVANT = "irrelevant"


class CaseStatus(str, Enum):
    OK = "OK"
    ERROR = "ERROR"
    SKIP = "SKIP"


@dataclass
class MatrixCase:
    scenario_id: str
    label: str
    apprenant_email: str
    expected_history: str | None
    catalog_mode: CatalogMode
    locale: str
    expect_ideas: bool
    expect_recommended_ids: bool  # True = must be non-empty, False = must be empty, None = either


@dataclass
class CaseResult:
    case: MatrixCase
    status: CaseStatus
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    history_richness: str | None = None
    catalog_count: int = 0
    recommended_count: int = 0
    ideas_count: int = 0


@dataclass
class DbSnapshot:
    task_count: int
    application_count: int
    project_count: int
    listing_count: int
    task_updated_max: datetime | None
    project_updated_max: datetime | None
    listing_updated_max: datetime | None


ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
FRENCH_MARKERS_RE = re.compile(
    r"\b("
    r"vous|Vous|les|des|une|pour|avec|dans|qui|est|sont|"
    r"compétences|développeur|Maîtrise|apprenant|"
    r"élargir|proposer|débutez|objectif|lacunes|renforcer"
    r")\b",
    re.IGNORECASE,
)
STRONG_FRENCH_FOR_EN_RE = re.compile(
    r"\b("
    r"vous|Vous|débutez|compétences|développeur|Maîtrise|proposons|"
    r"élargir|aucune mission|Le catalogue|Nous vous|pour vous"
    r")\b",
    re.IGNORECASE,
)
ENGLISH_MARKERS_RE = re.compile(
    r"\b(Your profile|Because the|you need to|Next steps|To become a|skills to acquire)\b",
    re.IGNORECASE,
)


def _load_apprenant(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def verify_prerequisites(db: Session) -> list[str]:
    """Vérifie que les comptes de test ont le bon history_richness."""
    issues: list[str] = []
    for email, expected in (
        (APPRENANT_EMPTY_EMAIL, "empty"),
        (APPRENANT_SPARSE_EMAIL, "sparse"),
    ):
        apprenant = _load_apprenant(db, email)
        if not apprenant:
            issues.append(f"Compte introuvable : {email}")
            continue
        context = build_learner_gap_context(db, apprenant)
        if context.history_richness != expected:
            task_count = len(context.missions)
            issues.append(
                f"{email} : history_richness={context.history_richness} "
                f"(attendu {expected}, {task_count} mission(s))"
            )
    return issues


def prepare_prerequisites(db: Session) -> list[str]:
    """Restaure apprenant@test en historique vide (désassigne les tâches de test)."""
    actions: list[str] = []
    apprenant = _load_apprenant(db, APPRENANT_EMPTY_EMAIL)
    if not apprenant:
        raise RuntimeError(f"Compte introuvable : {APPRENANT_EMPTY_EMAIL}")

    tasks = db.scalars(
        select(Task).where(Task.assigned_apprenant_id == apprenant.id)
    ).all()
    if tasks:
        for task in tasks:
            task.assigned_apprenant_id = None
        db.commit()
        actions.append(
            f"Désassigné {len(tasks)} tâche(s) de {APPRENANT_EMPTY_EMAIL} pour restaurer history_richness=empty"
        )

    remaining = verify_prerequisites(db)
    if remaining:
        raise RuntimeError("Prérequis toujours non satisfaits après préparation :\n  " + "\n  ".join(remaining))
    return actions


def build_matrix(locales: list[str]) -> list[MatrixCase]:
    cases: list[MatrixCase] = []
    for locale in locales:
        cases.append(
            MatrixCase(
                scenario_id="a",
                label="historique vide × catalogue vide",
                apprenant_email=APPRENANT_EMPTY_EMAIL,
                expected_history="empty",
                catalog_mode=CatalogMode.EMPTY,
                locale=locale,
                expect_ideas=True,
                expect_recommended_ids=False,
            )
        )
        cases.append(
            MatrixCase(
                scenario_id="b",
                label="historique sparse × catalogue vide",
                apprenant_email=APPRENANT_SPARSE_EMAIL,
                expected_history="sparse",
                catalog_mode=CatalogMode.EMPTY,
                locale=locale,
                expect_ideas=True,
                expect_recommended_ids=False,
            )
        )
        cases.append(
            MatrixCase(
                scenario_id="c",
                label="catalogue pertinent (non vide)",
                apprenant_email=APPRENANT_EMPTY_EMAIL,
                expected_history=None,
                catalog_mode=CatalogMode.RELEVANT,
                locale=locale,
                expect_ideas=False,
                expect_recommended_ids=True,
            )
        )
        cases.append(
            MatrixCase(
                scenario_id="d",
                label="catalogue non pertinent (IDs vides attendus)",
                apprenant_email=APPRENANT_EMPTY_EMAIL,
                expected_history=None,
                catalog_mode=CatalogMode.IRRELEVANT,
                locale=locale,
                expect_ideas=False,
                expect_recommended_ids=False,
            )
        )
    return cases


def _collect_prose(payload: dict) -> str:
    parts = [payload.get("skill_gap", ""), payload.get("explanation", "")]
    for idea in payload.get("suggested_project_ideas") or []:
        parts.append(idea.get("title", ""))
        parts.append(idea.get("description", ""))
    return "\n".join(str(part) for part in parts if part)


def validate_output_language(locale: str, payload: dict) -> list[str]:
    errors: list[str] = []
    prose = _collect_prose(payload)
    skill_gap = str(payload.get("skill_gap", ""))
    explanation = str(payload.get("explanation", ""))

    if locale == "ar":
        if not ARABIC_RE.search(skill_gap):
            errors.append("locale=ar : skill_gap sans caractères arabes")
        if not ARABIC_RE.search(explanation):
            errors.append("locale=ar : explanation sans caractères arabes")
        for i, idea in enumerate(payload.get("suggested_project_ideas") or []):
            idea_text = f"{idea.get('title', '')} {idea.get('description', '')}"
            if idea_text.strip() and not ARABIC_RE.search(idea_text):
                errors.append(f"locale=ar : idée {i + 1} sans caractères arabes")

    elif locale == "fr":
        combined = f"{skill_gap} {explanation}"
        if not FRENCH_MARKERS_RE.search(combined) and not re.search(r"[àâäéèêëïîôùûüç]", combined, re.I):
            errors.append("locale=fr : peu d'indices français dans skill_gap/explanation")
        if ENGLISH_MARKERS_RE.search(combined):
            errors.append("locale=fr : phrases anglaises détectées dans skill_gap/explanation")

    elif locale == "en":
        combined = f"{skill_gap} {explanation}"
        strong_hits = STRONG_FRENCH_FOR_EN_RE.findall(combined)
        if strong_hits:
            errors.append(
                f"locale=en : indices français forts ({', '.join(sorted(set(strong_hits))[:5])})"
            )
        if re.search(r"\b(Vous débutez|Nous vous proposons|Maîtrise du)\b", combined):
            errors.append("locale=en : phrase française entière détectée")

    return errors


def validate_gap_payload(
    payload: dict,
    *,
    locale: str,
    allowed_project_ids: frozenset[UUID],
    expect_ideas: bool,
    expect_recommended_ids: bool | None,
) -> list[str]:
    errors: list[str] = []

    try:
        AiGapRecommendation.model_validate(payload)
    except Exception as exc:
        errors.append(f"Validation Pydantic échouée : {exc}")
        return errors

    ids = [str(x) for x in (payload.get("recommended_project_ids") or [])]
    ideas = payload.get("suggested_project_ideas") or []

    if ids and ideas:
        errors.append("Exclusion mutuelle violée : recommended_project_ids et suggested_project_ideas non vides")

    allowed_str = {str(pid) for pid in allowed_project_ids}
    for pid in ids:
        if pid not in allowed_str:
            errors.append(f"UUID hors catalogue : {pid}")

    if expect_ideas and not ids and not ideas:
        errors.append("Catalogue vide : aucune suggested_project_ideas générée")
    if not expect_ideas and ideas:
        errors.append("suggested_project_ideas non vide alors que le catalogue contient des opportunités")

    if expect_recommended_ids is True and not ids:
        errors.append("recommended_project_ids vide alors qu'un projet pertinent est attendu")
    if expect_recommended_ids is False and ids:
        errors.append("recommended_project_ids non vide alors qu'aucun projet pertinent n'est attendu")

    if ideas:
        for i, idea in enumerate(ideas):
            if not idea.get("title") or not idea.get("description"):
                errors.append(f"Idée {i + 1} incomplète")
            if not idea.get("target_skills"):
                errors.append(f"Idée {i + 1} sans target_skills")

    errors.extend(validate_output_language(locale, payload))
    return errors


def take_db_snapshot(db: Session, apprenant_ids: list[UUID]) -> DbSnapshot:
    task_q = select(func.count()).select_from(Task).where(Task.assigned_apprenant_id.in_(apprenant_ids))
    app_q = select(func.count()).select_from(Application).where(Application.apprenant_id.in_(apprenant_ids))
    project_q = select(func.count()).select_from(Project)
    listing_q = select(func.count()).select_from(Listing)

    task_updated = db.scalar(
        select(func.max(Task.updated_at)).where(Task.assigned_apprenant_id.in_(apprenant_ids))
    )
    project_updated = db.scalar(select(func.max(Project.updated_at)))
    listing_updated = db.scalar(select(func.max(Listing.updated_at)))

    return DbSnapshot(
        task_count=db.scalar(task_q) or 0,
        application_count=db.scalar(app_q) or 0,
        project_count=db.scalar(project_q) or 0,
        listing_count=db.scalar(listing_q) or 0,
        task_updated_max=task_updated,
        project_updated_max=project_updated,
        listing_updated_max=listing_updated,
    )


def compare_db_snapshots(before: DbSnapshot, after: DbSnapshot) -> list[str]:
    errors: list[str] = []
    if before.task_count != after.task_count:
        errors.append(f"Tâches modifiées : {before.task_count} → {after.task_count}")
    if before.application_count != after.application_count:
        errors.append(f"Applications modifiées : {before.application_count} → {after.application_count}")
    if before.project_count != after.project_count:
        errors.append(f"Projets modifiés : {before.project_count} → {after.project_count}")
    if before.listing_count != after.listing_count:
        errors.append(f"Annonces modifiées : {before.listing_count} → {after.listing_count}")
    if before.task_updated_max != after.task_updated_max:
        errors.append("Horodatage tâches modifié après l'appel")
    if before.project_updated_max != after.project_updated_max:
        errors.append("Horodatage projets modifié après l'appel")
    if before.listing_updated_max != after.listing_updated_max:
        errors.append("Horodatage annonces modifié après l'appel")
    return errors


class CatalogFixture:
    """Prépare le catalogue pour chaque scénario ; restaure l'état initial à la fin."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self._listing_status_backup: dict[UUID, ListingStatus] = {}
        self.relevant_project_id: UUID | None = None
        self.irrelevant_project_id: UUID | None = None

    def setup(self) -> None:
        listings = self.db.scalars(select(Listing)).all()
        for listing in listings:
            self._listing_status_backup[listing.id] = listing.status

        self._ensure_fixture_listings()
        self.set_mode(CatalogMode.EMPTY)

    def restore(self) -> None:
        for listing_id, status in self._listing_status_backup.items():
            listing = self.db.get(Listing, listing_id)
            if listing and listing.status != status:
                listing.status = status
        self.db.commit()

    def set_mode(self, mode: CatalogMode) -> None:
        for listing in self.db.scalars(select(Listing)).all():
            if listing.title.startswith(GAP_MATRIX_MARKER):
                listing.status = ListingStatus.CLOSED
            elif listing.status == ListingStatus.OPEN and listing.project_id is not None:
                listing.status = ListingStatus.CLOSED

        if mode == CatalogMode.RELEVANT:
            relevant = self.db.scalar(
                select(Listing).where(Listing.title == RELEVANT_LISTING_TITLE)
            )
            if relevant:
                relevant.status = ListingStatus.OPEN
        elif mode == CatalogMode.IRRELEVANT:
            irrelevant = self.db.scalar(
                select(Listing).where(Listing.title == IRRELEVANT_LISTING_TITLE)
            )
            if irrelevant:
                irrelevant.status = ListingStatus.OPEN

        self.db.commit()

    def _ensure_fixture_listings(self) -> None:
        relevant = self.db.scalar(select(Listing).where(Listing.title == RELEVANT_LISTING_TITLE))
        irrelevant = self.db.scalar(select(Listing).where(Listing.title == IRRELEVANT_LISTING_TITLE))

        if relevant and irrelevant:
            self.relevant_project_id = relevant.project_id
            self.irrelevant_project_id = irrelevant.project_id
            return

        mentor = self.db.scalar(select(User).where(User.email == os.getenv("TEST_MENTOR_EMAIL", "mentor@test.duo.dz")))
        if not mentor:
            mentor = self.db.scalar(
                select(User).where(User.role == UserRole.MENTOR).limit(1)
            )
        client = self.db.scalar(select(User).where(User.role == UserRole.CLIENT).limit(1))
        category = self.db.scalar(select(Category).limit(1))
        if not mentor or not client or not category:
            raise RuntimeError("Impossible de créer les annonces de test : mentor/client/catégorie manquant")

        if not relevant:
            project = Project(
                client_id=client.id,
                mentor_id=mentor.id,
                category_id=category.id,
                title=f"{GAP_MATRIX_MARKER} Projet Python full-stack",
                description="Projet de test gap matrix : développement web Python/React pour apprenant débutant.",
                status=ProjectStatus.IN_PROGRESS,
                required_skills=["Python", "React", "JavaScript", "HTML", "CSS"],
                learner_complexity_level=LearnerComplexityLevel.BEGINNER,
            )
            self.db.add(project)
            self.db.flush()
            relevant = Listing(
                mentor_id=mentor.id,
                title=RELEVANT_LISTING_TITLE,
                description="Annonce test gap matrix : mission full-stack Python/React alignée sur un profil débutant.",
                required_skills=["Python", "React", "JavaScript"],
                project_id=project.id,
                status=ListingStatus.CLOSED,
            )
            self.db.add(relevant)
            self.relevant_project_id = project.id

        if not irrelevant:
            project = Project(
                client_id=client.id,
                mentor_id=mentor.id,
                category_id=category.id,
                title=f"{GAP_MATRIX_MARKER} Projet Comptabilité Sage",
                description="Projet de test gap matrix : mission comptable sans lien avec le développement logiciel.",
                status=ProjectStatus.IN_PROGRESS,
                required_skills=["Comptabilité", "Sage 100", "Paie", "Fiscalité"],
                learner_complexity_level=LearnerComplexityLevel.ADVANCED,
            )
            self.db.add(project)
            self.db.flush()
            irrelevant = Listing(
                mentor_id=mentor.id,
                title=IRRELEVANT_LISTING_TITLE,
                description="Annonce test gap matrix : expert comptable Sage — hors profil développeur.",
                required_skills=["Comptabilité", "Sage 100", "Paie"],
                project_id=project.id,
                status=ListingStatus.CLOSED,
            )
            self.db.add(irrelevant)
            self.irrelevant_project_id = project.id

        self.db.commit()


def run_case(
    db: Session,
    fixture: CatalogFixture,
    case: MatrixCase,
    apprenant_ids: list[UUID],
    *,
    verbose: bool,
) -> CaseResult:
    result = CaseResult(case=case, status=CaseStatus.OK)

    apprenant = db.scalar(select(User).where(User.email == case.apprenant_email))
    if not apprenant:
        result.status = CaseStatus.ERROR
        result.errors.append(f"Apprenant introuvable : {case.apprenant_email}")
        return result

    fixture.set_mode(case.catalog_mode)
    apprenant.locale = Locale(case.locale)
    db.commit()

    context = build_learner_gap_context(db, apprenant)
    result.history_richness = context.history_richness
    result.catalog_count = len(context.opportunities)

    if case.expected_history and context.history_richness != case.expected_history:
        result.status = CaseStatus.ERROR
        result.errors.append(
            f"history_richness attendu={case.expected_history}, obtenu={context.history_richness}"
        )
        return result

    if case.catalog_mode == CatalogMode.EMPTY and result.catalog_count != 0:
        result.status = CaseStatus.ERROR
        result.errors.append(f"Catalogue attendu vide, obtenu {result.catalog_count} opportunité(s)")
        return result
    if case.catalog_mode != CatalogMode.EMPTY and result.catalog_count == 0:
        result.status = CaseStatus.ERROR
        result.errors.append("Catalogue attendu non vide, obtenu 0 opportunité(s)")
        return result

    before = take_db_snapshot(db, apprenant_ids)
    try:
        recommendation = generate_gap_analysis(db, apprenant)
    except Exception as exc:
        result.status = CaseStatus.ERROR
        result.errors.append(f"Appel gap_analysis échoué : {exc}")
        return result
    after = take_db_snapshot(db, apprenant_ids)

    db_errors = compare_db_snapshots(before, after)
    if db_errors:
        result.status = CaseStatus.ERROR
        result.errors.extend(db_errors)

    payload = recommendation.model_dump(mode="json")
    result.recommended_count = len(payload.get("recommended_project_ids") or [])
    result.ideas_count = len(payload.get("suggested_project_ideas") or [])

    validation_errors = validate_gap_payload(
        payload,
        locale=case.locale,
        allowed_project_ids=context.allowed_project_ids,
        expect_ideas=case.expect_ideas,
        expect_recommended_ids=case.expect_recommended_ids,
    )
    if validation_errors:
        result.status = CaseStatus.ERROR
        result.errors.extend(validation_errors)

    if verbose:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    return result


def print_case_line(result: CaseResult) -> None:
    case = result.case
    tag = f"[{case.scenario_id}] {case.locale} | {case.label}"
    if result.status == CaseStatus.OK:
        print(f"  OK   {tag}")
        print(
            f"       history={result.history_richness} catalogue={result.catalog_count} "
            f"ids={result.recommended_count} ideas={result.ideas_count}"
        )
    else:
        print(f"  ERR  {tag}")
        for err in result.errors:
            print(f"       → {err}")


MANUAL_CHECKLIST = """
=== Checklist manuelle (non automatisée) ===

Pour chaque locale (fr, ar, en), relire au moins un cas « catalogue vide » (a ou b) :
  □ Le ton est naturel et pédagogique (pas robotique ni trop générique).
  □ L'arabe (locale=ar) est fluide pour un public algérien (pas dialecte étranger ni MSA trop formel).
  □ Les skill_gap listent des lacunes cohérentes avec career_goal et declared_skills.
  □ Les idées fictives (scénarios a/b) sont réalistes pour le marché algérien (PME, freelances, étudiants).
  □ Les idées ont une complexité raisonnable pour un apprenant encadré (quelques semaines).

Pour le scénario c (catalogue pertinent) :
  □ Les projets recommandés sont réellement alignés avec le profil (pas seulement présents dans le catalogue).
  □ L'explanation justifie clairement pourquoi ces projets sont pertinents.

Pour le scénario d (catalogue non pertinent) :
  □ L'explanation explique pourquoi aucun projet du catalogue n'est recommandé (sans inventer d'idées fictives).
"""


def run_matrix(locales: list[str], *, dry_run: bool, verbose: bool, prepare: bool) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    cases = build_matrix(locales)
    print("=== Gap analysis matrix (§5.4) ===")
    print(f"Locales    : {', '.join(locales)}")
    print(f"Cas total  : {len(cases)}")
    print(f"Empty user : {APPRENANT_EMPTY_EMAIL}")
    print(f"Sparse user: {APPRENANT_SPARSE_EMAIL}")
    print()

    if dry_run:
        print("--- Matrice (dry-run, pas d'appel IA) ---")
        for case in cases:
            print(
                f"  [{case.scenario_id}] locale={case.locale} | {case.label} | "
                f"{case.apprenant_email} | ideas={case.expect_ideas} | "
                f"ids={'non vide' if case.expect_recommended_ids else 'vide' if case.expect_recommended_ids is False else 'any'}"
            )
        print(MANUAL_CHECKLIST)
        return 0

    get_settings.cache_clear()
    try:
        provider, _, base_url, model = resolve_ai_provider_config(get_settings())
        print(f"Provider   : {provider}")
        print(f"Modèle IA  : {model}")
        if base_url:
            print(f"Base URL   : {base_url}")
        print()
    except RuntimeError as exc:
        print(f"ERREUR : {exc}")
        return 1

    db = SessionLocal()
    fixture = CatalogFixture(db)
    results: list[CaseResult] = []

    try:
        if prepare:
            print("--- Préparation des prérequis ---")
            for action in prepare_prerequisites(db):
                print(f"  {action}")
            print()

        prereq_issues = verify_prerequisites(db)
        if prereq_issues:
            print("ERREUR : prérequis non satisfaits :")
            for issue in prereq_issues:
                print(f"  - {issue}")
            print("\nRelancez avec --prepare pour restaurer apprenant@test en historique vide.")
            return 1

        fixture.setup()
        apprenant_ids = [
            row.id
            for row in db.scalars(
                select(User).where(
                    User.email.in_([APPRENANT_EMPTY_EMAIL, APPRENANT_SPARSE_EMAIL])
                )
            ).all()
        ]

        current_scenario = ""
        for case in cases:
            if case.scenario_id != current_scenario:
                current_scenario = case.scenario_id
                print(f"\n--- Scénario {current_scenario} : {case.label.split('×')[0].strip() if '×' in case.label else case.label} ---")

            print(f"\n>>> [{case.scenario_id}] locale={case.locale} | {case.apprenant_email}")
            result = run_case(db, fixture, case, apprenant_ids, verbose=verbose)
            results.append(result)
            print_case_line(result)

    finally:
        fixture.restore()
        db.close()

    ok = sum(1 for r in results if r.status == CaseStatus.OK)
    errors = sum(1 for r in results if r.status == CaseStatus.ERROR)
    skipped = sum(1 for r in results if r.status == CaseStatus.SKIP)

    print("\n=== Résumé gap-analysis matrix ===")
    print(f"  OK      : {ok}")
    print(f"  ERREUR  : {errors}")
    print(f"  SKIP    : {skipped}")
    print(f"  TOTAL   : {len(results)}")

    if errors:
        print("\nCas en erreur :")
        for result in results:
            if result.status == CaseStatus.ERROR:
                case = result.case
                print(f"  - [{case.scenario_id}] {case.locale} {case.label}")
                for err in result.errors:
                    print(f"      {err}")

    print(MANUAL_CHECKLIST)
    return 1 if errors else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Matrice de tests gap analysis §5.4")
    parser.add_argument(
        "--locales",
        default=",".join(DEFAULT_LOCALES),
        help="Locales à tester (défaut : fr,ar,en)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Afficher la matrice sans appeler l'IA",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Afficher le JSON complet pour chaque cas",
    )
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="Désassigne les tâches de apprenant@test pour restaurer history_richness=empty",
    )
    args = parser.parse_args()
    locales = [x.strip() for x in args.locales.split(",") if x.strip()]
    raise SystemExit(
        run_matrix(locales, dry_run=args.dry_run, verbose=args.verbose, prepare=args.prepare)
    )


if __name__ == "__main__":
    main()
