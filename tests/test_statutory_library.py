"""
Unit tests for the Statutory Code & Reference Library.
Validates database ingestion, FTS5 search, repository methods, and API responses.
"""

import unittest
from app.repositories.statutory_repository import StatutoryRepository
from app.services.statutory_service import StatutoryService


class TestStatutoryLibrary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = StatutoryRepository()
        cls.svc = StatutoryService(cls.repo)

    def test_books_count(self):
        overview = self.svc.get_library_overview()
        self.assertEqual(overview["total_books"], 13)
        self.assertGreaterEqual(overview["total_rules"], 800)

    def test_rule_209_search(self):
        res = self.svc.search_rules("Rule 209")
        self.assertGreater(res["total_matches"], 0)
        top = res["results"][0]
        self.assertEqual(top["rule_no"], "Rule 209")
        self.assertIn("longitudinal", top["rule_title"].lower())
        self.assertEqual(top["page_no"], 57)

    def test_table_66_search(self):
        res = self.svc.search_rules("Table 66")
        self.assertGreater(res["total_matches"], 0)
        match_tables = [r for r in res["results"] if "Table 66" in r["rule_no"] or "Table 66" in r["rule_title"]]
        self.assertTrue(len(match_tables) > 0)

    def test_collision_bulkhead_search(self):
        res = self.svc.search_rules("collision bulkhead")
        self.assertGreater(res["total_matches"], 0)

    def test_stability_rules_search(self):
        res = self.svc.search_rules("stability")
        self.assertGreater(res["total_matches"], 0)
        book_ids = {r["book_id"] for r in res["results"]}
        # Should include Stability Rules (Book 4) or Construction Rules (Book 1)
        self.assertTrue(1 in book_ids or 4 in book_ids)

    def test_citation_formatting(self):
        res = self.svc.search_rules("Rule 209")
        rule_id = res["results"][0]["id"]
        citation = self.svc.format_dos_citation(rule_id)
        self.assertIn("Rule 209", citation)
        self.assertIn("Inland Steel-Built Ships Construction Rules", citation)
        self.assertIn("Page 57", citation)


if __name__ == "__main__":
    unittest.main()
