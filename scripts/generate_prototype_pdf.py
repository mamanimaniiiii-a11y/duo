"""
Generate Duo platform prototype PDF (architecture, database, UML, API, pages).

Usage:
  python scripts/generate_prototype_pdf.py
  python scripts/generate_prototype_pdf.py --output docs/Duo-Prototype.pdf
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from fpdf import FPDF

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "Duo-Prototype.pdf"
LOGO_PATH = REPO_ROOT / "frontend" / "public" / "duo-logo.png"


def ascii_safe(text: str) -> str:
    """fpdf core fonts are Latin-1 only; normalize Unicode for PDF output."""
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2192": "->",
        "\u2190": "<-",
        "\u251c": "|",
        "\u2514": "+",
        "\u2500": "-",
        "\u2502": "|",
        "\u250c": "+",
        "\u2510": "+",
        "\u2518": "+",
        "\u2534": "+",
        "\u252c": "+",
        "\u25bc": "v",
        "\u2022": "*",
        "\u2194": "<->",
        "\u00a7": "",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", errors="replace").decode("latin-1")


class PrototypePDF(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, ascii_safe("Duo Agency - Technical Prototype"), align="L")
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def cover(self) -> None:
        if LOGO_PATH.is_file():
            self.image(str(LOGO_PATH), x=55, y=35, w=100)
            self.ln(75)
        else:
            self.ln(40)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(30, 60, 100)
        self.cell(0, 14, "DUO AGENCY", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_font("Helvetica", "", 16)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, "Platform Technical Prototype", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(8)
        self.set_font("Helvetica", "", 11)
        self.multi_cell(
            0,
            6,
            "Freelancing, mentoring and learning through real projects - Algerian market.\n"
            f"Document version 1.0 - {date.today().isoformat()}",
            align="C",
        )
        self.ln(20)
        self.set_font("Helvetica", "", 10)
        bullets = [
            "System architecture & stack",
            "PostgreSQL database schema (ERD)",
            "UML: use cases, classes, sequences",
            "REST API catalogue",
            "Frontend pages by role",
            "AI services (matching, tasks, gap analysis)",
            "Deployment topology",
        ]
        for item in bullets:
            self.cell(0, 7, f"  *  {item}", new_x="LMARGIN", new_y="NEXT")
        self.add_page()

    def section(self, title: str) -> None:
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 60, 100)
        self.cell(0, 10, ascii_safe(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 60, 100)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def subsection(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, ascii_safe(title), new_x="LMARGIN", new_y="NEXT")

    def body(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, ascii_safe(text))
        self.ln(2)

    def mono(self, text: str) -> None:
        self.set_font("Courier", "", 8)
        self.multi_cell(0, 4, ascii_safe(text))
        self.ln(2)


def build_pdf(output: Path) -> None:
    pdf = PrototypePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.cover()

    # 1. Vision
    pdf.section("1. Vision & Problem")
    pdf.body(
        "Duo connects clients, mentors (freelancers) and learners (apprenants) around real projects. "
        "Clients publish missions; mentors deliver work and supervise learners; learners build a verifiable "
        "portfolio on authentic tasks. AI assists matching, task breakdown, gap detection and future review flows."
    )
    pdf.subsection("1.1 User roles")
    pdf.mono(
        "Client      -> publishes projects, assigns mentor, validates delivery\n"
        "Mentor      -> takes projects, recruits learners, delegates tasks, reviews work\n"
        "Apprenant   -> applies to listings, executes assigned tasks, buys mentor packs\n"
        "Admin       -> users, categories, disputes, boost/premium configuration"
    )

    # 2. Stack
    pdf.section("2. Technology Stack")
    pdf.mono(
        "Frontend   Next.js 16 + TypeScript + Tailwind CSS + next-intl (FR/EN/AR, RTL)\n"
        "Backend    FastAPI (Python 3.11+) + SQLAlchemy + Alembic\n"
        "Database   PostgreSQL on Supabase (DB only, no Supabase Auth)\n"
        "Auth       JWT (access + refresh), role-based guards\n"
        "AI         OpenAI / Groq via AIProvider abstraction\n"
        "Deploy     Vercel (frontend), Render (backend), Supabase (DB)"
    )

    # 3. Architecture
    pdf.add_page()
    pdf.section("3. System Architecture")
    pdf.mono(
        "┌─────────────────────────────────────────────────────────────┐\n"
        "│  Browser (Next.js App Router, locale /fr|en|ar)             │\n"
        "│  lib/api/*  →  fetchApi(NEXT_PUBLIC_API_URL)              │\n"
        "└───────────────────────────┬─────────────────────────────────┘\n"
        "                            │ HTTPS / JSON\n"
        "┌───────────────────────────▼─────────────────────────────────┐\n"
        "│  FastAPI API  /api/v1                                       │\n"
        "│  routers: auth, account, client, mentor, apprenant, admin,  │\n"
        "│           public, reviews, ai, common                       │\n"
        "└───────────┬─────────────────────────────┬───────────────────┘\n"
        "            │                             │\n"
        "   ┌────────▼────────┐           ┌────────▼────────┐\n"
        "   │  services/*     │           │  services/ai/*  │\n"
        "   │  auth, match,   │           │  task_breakdown,  │\n"
        "   │  score, notify  │           │  gap_analysis     │\n"
        "   └────────┬────────┘           └────────┬────────┘\n"
        "            │                             │\n"
        "   ┌────────▼─────────────────────────────▼────────┐\n"
        "   │  SQLAlchemy models  →  PostgreSQL (Supabase)   │\n"
        "   └────────────────────────────────────────────────┘"
    )

    # 4. Database ERD
    pdf.section("4. Database Schema (PostgreSQL)")
    pdf.subsection("4.1 Core entities")
    pdf.mono(
        "users (id PK, email UK, username UK, role, display_name, locale, ...)\n"
        "  ├── client_profiles (user_id FK 1:1)\n"
        "  ├── mentor_profiles (user_id FK 1:1, score, skills JSONB, ...)\n"
        "  │     └── mentor_categories (M:N with categories)\n"
        "  └── apprenant_profiles (user_id FK 1:1, skills, career_goal, score)\n"
        "\n"
        "categories (slug UK, name_fr/en/ar)\n"
        "skills (slug UK, category_id FK optional)\n"
        "\n"
        "projects (client_id FK, mentor_id FK?, category_id FK, status, budget_dzd,\n"
        "          required_skills JSONB, learner_complexity_level, description_format)\n"
        "  ├── tasks (project_id FK, assigned_apprenant_id FK?, status, acceptance_criteria)\n"
        "  │     └── submissions (task_id FK)\n"
        "  ├── deliverables (project_id FK)\n"
        "  └── listings (mentor_id FK, project_id FK?, required_skills, status)\n"
        "        └── applications (listing_id FK, apprenant_id FK, ai_match_score)\n"
        "\n"
        "reviews (from_user_id, to_user_id, project_id?, type, rating, comment)\n"
        "mentor_packs → pack_purchases (apprenant ↔ mentor)\n"
        "boost_options / premium_plans → subscriptions\n"
        "notifications, messages, disputes"
    )

    pdf.subsection("4.2 Enumerations (selected)")
    pdf.mono(
        "user_role: client | mentor | apprenant | admin\n"
        "project_status: draft → published → assigned → in_progress → delivered → completed\n"
        "task_status: todo | in_progress | submitted | revision | approved\n"
        "listing_status: draft | open | closed | archived\n"
        "application_status: pending | accepted | rejected | withdrawn\n"
        "review_type: client_to_mentor | mentor_to_apprenant | apprenant_to_mentor"
    )

    # 5. UML Use cases
    pdf.add_page()
    pdf.section("5. UML — Use Cases (summary)")
    pdf.mono(
        "                    ┌──────────────── Duo Platform ────────────────┐\n"
        "                    │                                              │\n"
        "  Client ──────────►│  Publish project, assign mentor, review      │\n"
        "  Mentor ──────────►│  Take project, AI task breakdown, recruit,   │\n"
        "                    │  assign tasks, approve submissions             │\n"
        "  Apprenant ───────►│  Apply to listing, execute mission, gap AI   │\n"
        "  Admin ───────────►│  Moderate users, categories, disputes       │\n"
        "                    └──────────────────────────────────────────────┘"
    )

    pdf.subsection("5.1 Class diagram (domain core)")
    pdf.mono(
        "┌──────────┐     1:1      ┌────────────────┐\n"
        "│   User   │─────────────►│ MentorProfile  │\n"
        "└────┬─────┘              └───────┬────────┘\n"
        "     │ 1:N                        │ creates\n"
        "     ▼                            ▼\n"
        "┌──────────┐              ┌──────────┐      ┌──────────┐\n"
        "│ Project  │◄─────────────│ Listing  │─────►│Application│\n"
        "└────┬─────┘              └──────────┘      └──────────┘\n"
        "     │ 1:N\n"
        "     ▼\n"
        "┌──────────┐      ┌────────────┐\n"
        "│   Task   │─────►│ Submission │\n"
        "└──────────┘      └────────────┘"
    )

    pdf.subsection("5.2 Sequence — Client assigns mentor (§5.1 matching)")
    pdf.mono(
        "Client → GET /client/projects/{id}/mentor-matches\n"
        "       ← match_service: 50% skills overlap + 50% mentor score\n"
        "Client → POST /client/projects/{id}/assign-mentor { mentor_id }\n"
        "       → project.mentor_id set, status → assigned\n"
        "       → notification_service → mentor notified"
    )

    pdf.subsection("5.3 Sequence — AI gap analysis (§5.4)")
    pdf.mono(
        "Apprenant → GET /ai/apprenant/gap-analysis\n"
        "          → build_learner_gap_context (missions, reviews, catalogue)\n"
        "          → AIProvider.complete_json_schema (locale-aware prompt)\n"
        "          → guardrails: filter UUIDs; if catalogue non-empty → ideas=[]\n"
        "          ← skill_gap, recommended_project_ids, explanation,\n"
        "             suggested_project_ideas (only if catalogue empty)"
    )

    # 6. API
    pdf.add_page()
    pdf.section("6. REST API Catalogue (/api/v1)")
    pdf.mono(
        "AUTH\n"
        "  POST /auth/register | /login | /refresh    GET /auth/me\n"
        "ACCOUNT\n"
        "  GET/PATCH /account   PATCH /{role}-profile   POST /onboarding/complete\n"
        "PUBLIC\n"
        "  GET /categories /mentors /mentors/{id} /apprenants/{id} /listings\n"
        "CLIENT\n"
        "  GET /dashboard /projects   POST /projects   PATCH /projects/{id}\n"
        "  POST /projects/{id}/publish\n"
        "  GET /projects/{id}/mentor-matches   POST .../assign-mentor\n"
        "MENTOR\n"
        "  GET /dashboard /projects /projects/disponibles\n"
        "  POST /projects/{id}/take   GET/PATCH tasks, listings, applications, packs\n"
        "  POST /ai/projects/{id}/task-breakdown (+ /apply)\n"
        "APPRENANT\n"
        "  GET /dashboard /decouvrir/listings /missions /packs /progression\n"
        "  POST /applications   GET /ai/apprenant/gap-analysis\n"
        "ADMIN\n"
        "  GET /dashboard /utilisateurs /litiges /configuration/categories\n"
        "COMMON\n"
        "  GET/POST /messages   GET/PATCH /notifications"
    )

    # 7. Frontend pages
    pdf.section("7. Frontend Pages (Next.js)")
    pdf.mono(
        "Public: /, /mentors, /mentors/[id], /annonces/[id], /apprenants/[id], /legal\n"
        "Auth: /auth/connexion, /auth/inscription, /auth/mot-de-passe\n"
        "Client: /client/dashboard, /client/projets, /client/projets/nouveau,\n"
        "        /client/projets/[id], /client/onboarding\n"
        "Mentor: /mentor/dashboard, /mentor/projets, /mentor/projets/[id],\n"
        "        /mentor/recrutement, /mentor/apprenants, /mentor/packs, /mentor/boost\n"
        "Apprenant: /apprenant/dashboard, /apprenant/decouvrir, /apprenant/missions,\n"
        "           /apprenant/progression, /apprenant/packs, /apprenant/profil\n"
        "Admin: /admin/dashboard, /admin/utilisateurs, /admin/litiges,\n"
        "       /admin/configuration, /admin/boost-premium\n"
        "Shared: /account, /messages, /notifications"
    )

    # 8. AI
    pdf.add_page()
    pdf.section("8. AI Capabilities")
    pdf.mono(
        "5.1 Matching     match_service - skills + mentor score (client->mentor)\n"
        "5.2 Task break   task_breakdown - LLM JSON schema, 3-8 subtasks\n"
        "5.3 Review       (planned) submission pre-check vs acceptance criteria\n"
        "5.4 Gap analysis gap_analysis - skill_gap, project recommendations,\n"
        "                  fictional project ideas when catalogue empty\n"
        "\n"
        "Mentor score formula (5bis.2): Bayesian priors, weights 25/15/35/25\n"
        "Triggers: review created, project completed, task approved"
    )

    # 9. Security & deploy
    pdf.section("9. Security & Deployment")
    pdf.mono(
        "JWT in httpOnly-style cookies (duo_access_token, duo_refresh_token)\n"
        "Role guards on routers; Pydantic validation on all I/O\n"
        "CORS_ORIGINS whitelist; secrets in env (never committed)\n"
        "\n"
        "Production topology:\n"
        "  [User] → Vercel CDN (Next.js) → Render Web Service (FastAPI)\n"
        "                                    ↓\n"
        "                              Supabase PostgreSQL\n"
        "                              Groq/OpenAI (AI calls)"
    )

    pdf.section("10. Repository & Links")
    pdf.body(
        "GitHub: https://github.com/mamanimaniiiii-a11y/5ibra\n"
        "Regenerate this PDF: python scripts/generate_prototype_pdf.py\n"
        "Gap analysis test matrix: python backend/scripts/test_gap_analysis_matrix.py --prepare"
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output))
    print(f"Generated: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Duo prototype PDF")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build_pdf(args.output)


if __name__ == "__main__":
    main()
