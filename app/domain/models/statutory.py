"""
Domain Models for Bangladesh Inland Statutory Code & Reference Library.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BookSummary(BaseModel):
    id: int
    title: str
    short_title: str
    category: str
    start_page: int
    end_page: int
    description: str
    rules_count: int = 0


class ChapterSummary(BaseModel):
    id: int
    book_id: int
    chapter_no: str
    title: str
    rules_count: int = 0


class RuleSummary(BaseModel):
    id: int
    book_id: int
    book_short_title: str
    chapter_title: Optional[str] = None
    rule_no: str
    rule_num_int: Optional[int] = None
    rule_title: str
    page_no: int
    tags: Optional[str] = None
    citation_text: str


class RuleDetail(RuleSummary):
    content_text: str
    content_html: str
    book_title: str


class SearchResultItem(BaseModel):
    id: int
    book_id: int
    book_short_title: str
    rule_no: str
    rule_title: str
    snippet: str
    page_no: int
    citation_text: str
    match_score: float = 0.0


class LibraryTocResponse(BaseModel):
    books: List[BookSummary]
    total_books: int
    total_rules: int


class SearchResponse(BaseModel):
    query: str
    total_matches: int
    results: List[SearchResultItem]
