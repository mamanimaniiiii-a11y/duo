"""
Démo pas-à-pas du score mentor §5bis.2.

Usage :
  python scripts/demo_mentor_score.py
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.mentor_score import calculate_mentor_score_breakdown


def _print_case(title: str, **kwargs) -> None:
    breakdown = calculate_mentor_score_breakdown(**kwargs)
    print(f"\n=== {title} ===")
    for key, value in kwargs.items():
        print(f"{key}: {value}")
    print("--- composantes ---")
    for key in (
        "project_part",
        "apprentice_part",
        "client_bayesian_normalized",
        "client_reviews_part",
        "apprentice_bayesian_normalized",
        "apprentice_reviews_part",
        "total",
    ):
        print(f"  {key}: {breakdown[key]}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    _print_case(
        "Historique vide (prior bayésien uniquement)",
        projects_completed=0,
        apprentices_mentored=0,
        client_reviews=[],
        apprentice_reviews=[],
    )

    _print_case(
        "Exemple documenté (8 projets, 3 apprentis, 10 avis clients ~4.5, 5 avis apprentis ~4.8)",
        projects_completed=8,
        apprentices_mentored=3,
        client_reviews=[5, 5, 5, 5, 5, 4, 4, 4, 4, 4],
        apprentice_reviews=[5, 5, 5, 5, 4],
    )

    _print_case(
        "Plafond projets (25 terminés → cap 20)",
        projects_completed=25,
        apprentices_mentored=0,
        client_reviews=[],
        apprentice_reviews=[],
    )

    _print_case(
        "Une review extrême (1/5) avec prior",
        projects_completed=0,
        apprentices_mentored=0,
        client_reviews=[1],
        apprentice_reviews=[],
    )


if __name__ == "__main__":
    main()
