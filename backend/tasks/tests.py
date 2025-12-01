from django.test import TestCase
from .scoring import analyze_tasks

class ScoringTests(TestCase):
    def test_missing_fields_and_defaults(self):
        tasks = [{"title":"No meta"}]
        results = analyze_tasks(tasks)
        self.assertEqual(len(results), 1)
        self.assertIn("score", results[0])
        self.assertIsInstance(results[0]["score"], float)

    def test_priority_order_and_components(self):
        tasks = [
            {"id":"t1","title":"Urgent small","due_date":"2025-01-01","estimated_hours":1,"importance":6},
            {"id":"t2","title":"Far heavy","due_date":"2030-01-01","estimated_hours":12,"importance":9},
            {"id":"t3","title":"Medium","due_date":"2025-12-01","estimated_hours":2,"importance":5}
        ]
        results = analyze_tasks(tasks, strategy="smart_balance")
        self.assertEqual(len(results), 3)
        # Highest score should be either t1 or t3 (urgent/quick)
        self.assertTrue(results[0]["id"] in ["t1", "t3"])
        # component keys present
        for r in results:
            self.assertIn("components", r)
            self.assertIn("urgency", r["components"])

    def test_cycle_detection_and_penalty(self):
        tasks = [
            {"id":"a","title":"A","dependencies":["b"]},
            {"id":"b","title":"B","dependencies":["c"]},
            {"id":"c","title":"C","dependencies":["a"]}
        ]
        results = analyze_tasks(tasks)
        self.assertTrue(all(r["circular"] for r in results))
