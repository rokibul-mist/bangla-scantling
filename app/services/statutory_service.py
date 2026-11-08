"""
Statutory Service
Business logic layer for Bangladesh Inland Laws and Rules knowledge base.
"""

from typing import List, Dict, Any, Optional
from app.repositories.statutory_repository import StatutoryRepository
from app.domain.models.statutory import (
    BookSummary, RuleDetail, RuleSummary, SearchResultItem, LibraryTocResponse, SearchResponse
)


class StatutoryService:
    def __init__(self, repo: Optional[StatutoryRepository] = None):
        self.repo = repo or StatutoryRepository()

    def get_library_overview(self) -> Dict[str, Any]:
        books = self.repo.get_all_books()
        counts = self.repo.get_total_counts()
        return {
            "books": books,
            "total_books": counts["books"],
            "total_rules": counts["rules"]
        }

    def get_book_details(self, book_id: int) -> Optional[Dict[str, Any]]:
        book = self.repo.get_book_by_id(book_id)
        if not book:
            return None
        chapters = self.repo.get_chapters_by_book(book_id)
        rules = self.repo.get_rules_by_book(book_id, limit=200)
        return {
            "book": book,
            "chapters": chapters,
            "rules": rules
        }

    def get_rule_by_id(self, rule_id: int) -> Optional[Dict[str, Any]]:
        return self.repo.get_rule_by_id(rule_id)

    def search_rules(self, query: str, book_id: Optional[int] = None, limit: int = 40) -> Dict[str, Any]:
        results = self.repo.search(query=query, book_id=book_id, limit=limit)
        return {
            "query": query,
            "total_matches": len(results),
            "results": results
        }

    def format_dos_citation(self, rule_id: int) -> str:
        rule = self.repo.get_rule_by_id(rule_id)
        if not rule:
            return ""
        return (
            f"{rule['citation_text']} (Page {rule['page_no']}), "
            f"Statutory Inland Vessel Rules & Laws of Bangladesh (S.R.O. 308/Law-2001 & ISO 1976)."
        )
