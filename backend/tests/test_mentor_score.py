import unittest

from app.services.mentor_score import (
    bayesian_normalized_score,
    calculate_mentor_score,
    calculate_mentor_score_breakdown,
)


class MentorScoreTests(unittest.TestCase):
    def test_empty_history_uses_bayesian_prior(self) -> None:
        score = calculate_mentor_score(0, 0, [], [])
        self.assertEqual(score, 45)

    def test_documented_example(self) -> None:
        client_reviews = [5, 5, 5, 5, 5, 4, 4, 4, 4, 4]
        apprentice_reviews = [5, 5, 5, 5, 4]
        score = calculate_mentor_score(8, 3, client_reviews, apprentice_reviews)
        breakdown = calculate_mentor_score_breakdown(8, 3, client_reviews, apprentice_reviews)
        self.assertEqual(score, 66)
        self.assertEqual(breakdown["total"], 66)
        self.assertAlmostEqual(breakdown["project_part"], 10.0)
        self.assertAlmostEqual(breakdown["apprentice_part"], 4.5)
        self.assertAlmostEqual(breakdown["client_reviews_part"], 29.62, places=1)
        self.assertAlmostEqual(breakdown["apprentice_reviews_part"], 21.88, places=1)

    def test_project_cap_at_20(self) -> None:
        low = calculate_mentor_score(20, 0, [], [])
        high = calculate_mentor_score(25, 0, [], [])
        self.assertEqual(low, high)

    def test_apprentice_cap_at_10(self) -> None:
        low = calculate_mentor_score(0, 10, [], [])
        high = calculate_mentor_score(0, 15, [], [])
        self.assertEqual(low, high)

    def test_single_extreme_review_does_not_dominate(self) -> None:
        with_prior = calculate_mentor_score(0, 0, [1], [])
        without = calculate_mentor_score(0, 0, [], [])
        self.assertGreater(with_prior, 0)
        self.assertGreater(without, with_prior)

    def test_invalid_rating_raises(self) -> None:
        with self.assertRaises(ValueError):
            calculate_mentor_score(0, 0, [6], [])

    def test_bayesian_normalized_empty(self) -> None:
        self.assertAlmostEqual(bayesian_normalized_score([]), 75.0)


if __name__ == "__main__":
    unittest.main()
