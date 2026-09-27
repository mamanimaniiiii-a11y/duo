"""Formule de score mentor §5bis.2 — fonctions pures, testables sans base."""

from __future__ import annotations

BAYESIAN_PRIOR_COUNT = 3
BAYESIAN_PRIOR_MEAN = 4.0

PROJECT_WEIGHT = 0.25
PROJECT_CAP = 20

APPRENTICE_WEIGHT = 0.15
APPRENTICE_CAP = 10

CLIENT_REVIEWS_WEIGHT = 0.35
APPRENTICE_REVIEWS_WEIGHT = 0.25


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def bayesian_normalized_score(ratings: list[int]) -> float:
    """Prior 3×4.0/5, puis normalisation (avg-1)/4×100 sur 0-100."""
    prior_sum = BAYESIAN_PRIOR_COUNT * BAYESIAN_PRIOR_MEAN
    real_sum = sum(ratings)
    real_count = len(ratings)
    bayesian_avg = (prior_sum + real_sum) / (BAYESIAN_PRIOR_COUNT + real_count)
    return (bayesian_avg - 1.0) / 4.0 * 100.0


def _volume_component(count: int, cap: int, weight: float) -> float:
    return weight * (min(count, cap) / cap) * 100.0


def calculate_mentor_score(
    projects_completed: int,
    apprentices_mentored: int,
    client_reviews: list[int],
    apprentice_reviews: list[int],
) -> int:
    """
    Score mentor §5bis.2 — entier 0-100.

    client_reviews      : notes 1-5, type client_to_mentor
    apprentice_reviews  : notes 1-5, type apprenant_to_mentor
    """
    if projects_completed < 0 or apprentices_mentored < 0:
        raise ValueError("Les compteurs ne peuvent pas être négatifs")

    for rating in client_reviews + apprentice_reviews:
        if not 1 <= rating <= 5:
            raise ValueError(f"Note invalide : {rating} (attendu 1-5)")

    project_part = _volume_component(projects_completed, PROJECT_CAP, PROJECT_WEIGHT)
    apprentice_part = _volume_component(apprentices_mentored, APPRENTICE_CAP, APPRENTICE_WEIGHT)
    client_part = CLIENT_REVIEWS_WEIGHT * bayesian_normalized_score(client_reviews)
    apprentice_review_part = APPRENTICE_REVIEWS_WEIGHT * bayesian_normalized_score(apprentice_reviews)

    return _clamp_score(project_part + apprentice_part + client_part + apprentice_review_part)


def calculate_mentor_score_breakdown(
    projects_completed: int,
    apprentices_mentored: int,
    client_reviews: list[int],
    apprentice_reviews: list[int],
) -> dict[str, float | int]:
    """Même calcul, avec détail par composante."""
    project_part = _volume_component(projects_completed, PROJECT_CAP, PROJECT_WEIGHT)
    apprentice_part = _volume_component(apprentices_mentored, APPRENTICE_CAP, APPRENTICE_WEIGHT)
    client_bayesian = bayesian_normalized_score(client_reviews)
    apprentice_bayesian = bayesian_normalized_score(apprentice_reviews)
    client_part = CLIENT_REVIEWS_WEIGHT * client_bayesian
    apprentice_review_part = APPRENTICE_REVIEWS_WEIGHT * apprentice_bayesian
    total = _clamp_score(project_part + apprentice_part + client_part + apprentice_review_part)

    return {
        "total": total,
        "project_part": round(project_part, 2),
        "apprentice_part": round(apprentice_part, 2),
        "client_reviews_part": round(client_part, 2),
        "apprentice_reviews_part": round(apprentice_review_part, 2),
        "client_bayesian_normalized": round(client_bayesian, 2),
        "apprentice_bayesian_normalized": round(apprentice_bayesian, 2),
    }
