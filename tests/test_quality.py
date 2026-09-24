import unittest
from app.search import rank, validate_answer


class QualityTests(unittest.TestCase):
    def test_personalization_breaks_retrieval_tie(self):
        python = {"id": "python", "skills": ["python"]}
        react = {"id": "react", "skills": ["react"]}
        result = rank([python, react], [react, python], ["react"])
        self.assertEqual(result[0]["id"], "react")
        self.assertEqual(result[0]["matched_skills"], ["react"])

    def test_rejects_hallucinated_job(self):
        with self.assertRaises(ValueError):
            validate_answer({"summary": "Found one", "picks": [{"id": "fake", "reason": "Fit"}]}, [])

    def test_result_facts_come_from_index(self):
        result = validate_answer(
            {"summary": "Found one", "picks": [{"id": "one", "reason": "Fit", "company": "Fake"}]},
            [{"id": "one", "company": "Fixture company"}],
        )
        self.assertEqual(result["jobs"][0]["company"], "Fixture company")
