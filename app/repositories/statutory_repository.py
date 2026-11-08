"""
Statutory Library Repository
SQLite database queries for Bangladesh Inland Vessel Laws and Rules with FTS5 search.
"""

import os
import re
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'statutory_rules.db')


class StatutoryRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_all_books(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT b.*, COUNT(r.id) as rules_count
            FROM books b
            LEFT JOIN rules r ON b.id = r.book_id
            GROUP BY b.id
            ORDER BY b.id ASC
            """)
            return [dict(row) for row in cur.fetchall()]

    def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM books WHERE id = ?", (book_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_chapters_by_book(self, book_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT c.*, COUNT(r.id) as rules_count
            FROM chapters c
            LEFT JOIN rules r ON c.id = r.chapter_id
            WHERE c.book_id = ?
            GROUP BY c.id
            ORDER BY c.id ASC
            """, (book_id,))
            return [dict(row) for row in cur.fetchall()]

    def get_rules_by_book(self, book_id: int, limit: int = 150, offset: int = 0) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT r.id, r.book_id, b.short_title as book_short_title, r.chapter_title,
                   r.rule_no, r.rule_num_int, r.rule_title, r.page_no, r.tags, r.citation_text
            FROM rules r
            JOIN books b ON r.book_id = b.id
            WHERE r.book_id = ?
            ORDER BY r.id ASC
            LIMIT ? OFFSET ?
            """, (book_id, limit, offset))
            return [dict(row) for row in cur.fetchall()]

    def get_rule_by_id(self, rule_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT r.*, b.title as book_title, b.short_title as book_short_title
            FROM rules r
            JOIN books b ON r.book_id = b.id
            WHERE r.id = ?
            """, (rule_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def search(self, query: str, book_id: Optional[int] = None, limit: int = 40) -> List[Dict[str, Any]]:
        clean_q = query.strip()
        if not clean_q:
            return []

        with self._get_connection() as conn:
            cur = conn.cursor()
            results = []

            # Exact Rule Number or Title Match gets top priority
            rule_no_param = f"%{clean_q}%"
            book_filter = "AND r.book_id = ?" if book_id else ""
            params = [rule_no_param, rule_no_param]
            if book_id:
                params.append(book_id)

            cur.execute(f"""
            SELECT r.id, r.book_id, b.short_title as book_short_title, r.rule_no,
                   r.rule_title, substr(r.content_text, 1, 180) as snippet,
                   r.page_no, r.citation_text, 1.0 as match_score
            FROM rules r
            JOIN books b ON r.book_id = b.id
            WHERE (r.rule_no LIKE ? OR r.rule_title LIKE ?) {book_filter}
            ORDER BY r.id ASC
            LIMIT 15
            """, tuple(params))

            exact_rows = [dict(row) for row in cur.fetchall()]
            seen_ids = set()
            for row in exact_rows:
                seen_ids.add(row["id"])
                results.append(row)

            # Clean FTS5 expression: sanitize tokens to alphanumeric
            tokens = [re.sub(r'[^\w]', '', t) for t in clean_q.split() if re.sub(r'[^\w]', '', t)]
            if tokens:
                fts_expr = " AND ".join([f"{t}*" for t in tokens])
            else:
                fts_expr = f'"{clean_q}"'

            try:
                fts_params = [fts_expr]
                if book_id:
                    fts_params.append(book_id)

                cur.execute(f"""
                SELECT r.id, r.book_id, b.short_title as book_short_title, r.rule_no,
                       r.rule_title,
                       snippet(rules_fts, 2, '<mark class=\"bg-amber-200 text-slate-900 font-bold px-0.5 rounded\">', '</mark>', '...', 22) as snippet,
                       r.page_no, r.citation_text,
                       rank as match_score
                FROM rules_fts
                JOIN rules r ON rules_fts.rowid = r.id
                JOIN books b ON r.book_id = b.id
                WHERE rules_fts MATCH ? {book_filter}
                ORDER BY rank
                LIMIT ?
                """, tuple(fts_params + [limit]))

                fts_rows = [dict(row) for row in cur.fetchall()]
                for row in fts_rows:
                    if row["id"] not in seen_ids:
                        seen_ids.add(row["id"])
                        results.append(row)
            except Exception as e:
                # Fallback to LIKE if FTS expression encounters syntax quirk
                print(f"[StatutoryRepository] FTS error on '{clean_q}': {e}")
                like_param = f"%{clean_q}%"
                like_params = [like_param, like_param]
                if book_id:
                    like_params.append(book_id)
                cur.execute(f"""
                SELECT r.id, r.book_id, b.short_title as book_short_title, r.rule_no,
                       r.rule_title, substr(r.content_text, 1, 180) as snippet,
                       r.page_no, r.citation_text, 0.5 as match_score
                FROM rules r
                JOIN books b ON r.book_id = b.id
                WHERE (r.content_text LIKE ? OR r.tags LIKE ?) {book_filter}
                LIMIT 25
                """, tuple(like_params))
                for row in cur.fetchall():
                    d = dict(row)
                    if d["id"] not in seen_ids:
                        seen_ids.add(d["id"])
                        results.append(d)

            return results[:limit]

    def get_total_counts(self) -> Dict[str, int]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM books")
            books_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM rules")
            rules_count = cur.fetchone()[0]
            return {"books": books_count, "rules": rules_count}
