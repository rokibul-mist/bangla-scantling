"""
Ingestion Pipeline for Bangladesh Inland Vessel Statutory Code & Rules
Parses all 13 rulebooks from 'Prevention_of_Inland_Vessel_Accidents_Laws_and_Rules_EN.pdf'
into a high-performance SQLite database with FTS5 Full-Text Search indexing.
"""

import os
import sys
import re
import sqlite3
import html
from typing import List, Dict, Any, Optional
import fitz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

PDF_PATH = os.path.join(BASE_DIR, 'app', 'assets', 'docs', 'Prevention_of_Inland_Vessel_Accidents_Laws_and_Rules_EN.pdf')
DB_DIR = os.path.join(BASE_DIR, 'app', 'data')
DB_PATH = os.path.join(DB_DIR, 'statutory_rules.db')

BOOKS_METADATA = [
    {
        "id": 1,
        "title": "Inland Steel-Built Ships Construction Rules, 2001",
        "short_title": "Construction Rules 2001",
        "category": "Structural & Construction",
        "start_page": 9,
        "end_page": 95,
        "description": "Scantlings for keel, bottom, bilge, side shell, deck plating, transverse & longitudinal framing, bulkheads, pillars, engine seating, anchors, welding, and hull girder strength & midship section modulus (Rules 1–227, Tables 1–67)."
    },
    {
        "id": 2,
        "title": "Inland Ships (Passenger) Rules, 2001",
        "short_title": "Passenger Rules",
        "category": "Passenger Safety",
        "start_page": 96,
        "end_page": 101,
        "description": "Passenger spaces, seating allowances, deck area requirements, exits, stairs, toilet facilities, and passenger vessel safety standards."
    },
    {
        "id": 3,
        "title": "Inland Ships (Free-board) Rules, 2001",
        "short_title": "Freeboard Rules",
        "category": "Load Line & Freeboard",
        "start_page": 101,
        "end_page": 105,
        "description": "Minimum statutory freeboard calculations, deck lines, load line marks, seasonal zones, hatchway coamings, and safety distances."
    },
    {
        "id": 4,
        "title": "Inland Ships (Stability) Rules, 2001",
        "short_title": "Stability Rules",
        "category": "Intact Stability",
        "start_page": 105,
        "end_page": 112,
        "description": "Intact stability standards, GM limits, righting levers (GZ), wind heeling criteria, inclining tests, and statutory stability booklets."
    },
    {
        "id": 5,
        "title": "Inland Ships (Life Saving) Rules, 2001",
        "short_title": "Life Saving Rules",
        "category": "Life Saving Appliances",
        "start_page": 112,
        "end_page": 117,
        "description": "Lifeboats, liferafts, buoyant apparatus, lifejackets, lifebuoys, line-throwing appliances, distress flares, and emergency stowage."
    },
    {
        "id": 6,
        "title": "Inland Ships (Fire Safety) Rules, 2001",
        "short_title": "Fire Safety Rules",
        "category": "Fire Protection",
        "start_page": 117,
        "end_page": 127,
        "description": "Fire detection, fire pumps, mains, hydrants, hoses, portable extinguishers, fixed CO2 / gas extinguishing systems, and structural fire protection."
    },
    {
        "id": 7,
        "title": "Inland Ships Examination Syllabus (Inland Master, Driver etc.) Rules, 2001",
        "short_title": "Examination Syllabus",
        "category": "Competency & Manning",
        "start_page": 128,
        "end_page": 131,
        "description": "Statutory syllabus, theoretical & practical criteria for Master Class 1, 2, 3 and Driver Class 1, 2, 3 certificates of competency."
    },
    {
        "id": 8,
        "title": "Inland Ships (Manning, Examination and Certification) Rules, 2001",
        "short_title": "Certification Rules",
        "category": "Competency & Manning",
        "start_page": 132,
        "end_page": 140,
        "description": "Age limits, qualifying sea service, medical fitness, examination conduct, issue, suspension, and endorsement of competency certificates."
    },
    {
        "id": 9,
        "title": "Inland Ships (Minimum Safe Manning) Rules, 2001",
        "short_title": "Safe Manning Scales",
        "category": "Competency & Manning",
        "start_page": 141,
        "end_page": 145,
        "description": "Statutory safe manning scales for cargo vessels, passenger vessels, oil tankers, tugs, and dredgers based on gross tonnage and BHP."
    },
    {
        "id": 10,
        "title": "Inland Ships (Navigation) Rules, 2001",
        "short_title": "Navigation Rules",
        "category": "River Navigation & Colregs",
        "start_page": 145,
        "end_page": 153,
        "description": "Collision prevention, masthead & side navigation lights, day shapes, sound signaling appliances, right-of-way, and river channel rules."
    },
    {
        "id": 11,
        "title": "Inland Ships (Dangerous Goods) Carriage Rules, 2001",
        "short_title": "Dangerous Goods Rules",
        "category": "Dangerous Cargo & Tankers",
        "start_page": 154,
        "end_page": 157,
        "description": "Classification of dangerous cargoes, packaging, labeling, tanker piping, venting, safety precautions, emergency drills, and spill response."
    },
    {
        "id": 12,
        "title": "Inland Ships (Tonnage Measurement) Rules, 2001",
        "short_title": "Tonnage Rules",
        "category": "Tonnage Measurement",
        "start_page": 158,
        "end_page": 165,
        "description": "Statutory determination of Gross Tonnage (GT) and Net Tonnage (NT), under-deck volume, enclosed spaces, and coefficient formulas."
    },
    {
        "id": 13,
        "title": "The Inland Shipping Ordinance, 1976 (Ordinance No. 72 of 1976)",
        "short_title": "Inland Shipping Ordinance 1976",
        "category": "Statutory Primary Act",
        "start_page": 166,
        "end_page": 201,
        "description": "Principal statutory act of Bangladesh: vessel registration, survey, survey certificates, unseaworthy vessel detention, casualties, inquiries, and legal penalties."
    }
]

NAVAL_KEYWORD_MAP = {
    "keel": "keel plate, flat plate keel, bar keel, centerline girder",
    "bottom": "bottom shell plating, outer bottom, double bottom, floor plates, keelsons",
    "bilge": "bilge plating, bilge strake, bilge radius, bilge keel, bilge well, chine",
    "side": "side shell plating, sheer strake, web frames, side stringers, side frames",
    "deck": "deck plating, weather deck, stringer plate, deck beams, deck girders, pillars",
    "strength": "hull girder strength, midship section modulus, bending moment, shear force, table 66, longitudinal strength",
    "modulus": "section modulus, Z_req, Z_actual, parallel axis theorem, neutral axis, inertia",
    "bulkhead": "watertight bulkhead, collision bulkhead, after peak bulkhead, bulkhead stiffeners",
    "pillar": "stanchion, pillar, deck support, load column",
    "rudder": "rudder stock, rudder blade, pintles, coupling bolts, steering gear, tiller",
    "anchor": "anchors, chain cable, windlass, hawse pipe, chain locker, mooring lines",
    "frame": "transverse frame, web frame, frame spacing, longitudinals, stiffeners",
    "engine": "engine seating, machinery space, shaft tunnel, propeller post, stern tube",
    "welding": "butt weld, fillet weld, welding electrode, weld inspection, continuity",
    "stability": "intact stability, initial GM, righting lever GZ, inclining test, wind heeling, heel angle",
    "freeboard": "freeboard mark, deck line, load line, seasonal zones, safety distance, freeing ports",
    "passenger": "passenger accommodation, clear deck area, seating, stairways, exits, passenger count",
    "life": "lifeboat, liferaft, buoyant apparatus, lifejacket, lifebuoy, distress flares",
    "fire": "fire pump, fire main, hydrant, hose, nozzle, portable extinguisher, CO2 fixed system, fire boundary",
    "tonnage": "gross tonnage, net tonnage, under-deck volume, enclosed spaces, tonnage calculation",
    "survey": "certificate of survey, surveyor, annual survey, special survey, drydocking, registration"
}


def setup_database(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS rules_fts")
    cur.execute("DROP TABLE IF EXISTS rules")
    cur.execute("DROP TABLE IF EXISTS chapters")
    cur.execute("DROP TABLE IF EXISTS books")

    cur.execute("""
    CREATE TABLE books (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        short_title TEXT NOT NULL,
        category TEXT NOT NULL,
        start_page INTEGER NOT NULL,
        end_page INTEGER NOT NULL,
        description TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        chapter_no TEXT NOT NULL,
        title TEXT NOT NULL,
        FOREIGN KEY(book_id) REFERENCES books(id)
    )
    """)

    cur.execute("""
    CREATE TABLE rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        chapter_id INTEGER,
        chapter_title TEXT,
        rule_no TEXT NOT NULL,
        rule_num_int INTEGER,
        rule_title TEXT NOT NULL,
        content_text TEXT NOT NULL,
        content_html TEXT NOT NULL,
        page_no INTEGER NOT NULL,
        tags TEXT,
        citation_text TEXT NOT NULL,
        FOREIGN KEY(book_id) REFERENCES books(id),
        FOREIGN KEY(chapter_id) REFERENCES chapters(id)
    )
    """)

    # FTS5 virtual table for full-text sub-millisecond search
    cur.execute("""
    CREATE VIRTUAL TABLE rules_fts USING fts5(
        rule_no,
        rule_title,
        content_text,
        tags,
        book_title
    )
    """)

    conn.commit()
    return conn


def extract_tags(title: str, text: str) -> str:
    combined = (title + " " + text).lower()
    tags = set()
    for kw, expanded in NAVAL_KEYWORD_MAP.items():
        if kw in combined:
            tags.add(kw)
            for t in expanded.split(", "):
                if t in combined:
                    tags.add(t)
    return ", ".join(sorted(tags))


def text_to_html(title: str, text: str) -> str:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    html_parts = [f"<h3 class='text-base font-bold text-slate-900 mb-2'>{html.escape(title)}</h3>"]
    for p in paragraphs:
        escaped = html.escape(p)
        # Highlight sub-clauses like 1., 2., a., b.
        escaped = re.sub(r"^(\d+\.|\([a-z\d]+\)|[a-z]\.)", r"<strong class='text-indigo-700 font-bold'>\1</strong>", escaped)
        html_parts.append(f"<p class='text-sm text-slate-700 leading-relaxed mb-2'>{escaped}</p>")

    return "".join(html_parts)


def parse_and_ingest():
    print(f"[*] Opening PDF: {PDF_PATH}")
    if not os.path.exists(PDF_PATH):
        print(f"[!] Error: PDF not found at {PDF_PATH}")
        sys.exit(1)

    doc = fitz.open(PDF_PATH)
    print(f"[*] PDF opened successfully with {len(doc)} pages.")

    conn = setup_database(DB_PATH)
    cur = conn.cursor()

    # Insert books metadata
    for b in BOOKS_METADATA:
        cur.execute(
            "INSERT INTO books (id, title, short_title, category, start_page, end_page, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (b["id"], b["title"], b["short_title"], b["category"], b["start_page"], b["end_page"], b["description"])
        )
    conn.commit()

    total_rules = 0

    # Rule extraction patterns
    rule_patterns = [
        # e.g., "p.185 ### 1. Short title" or "1. Short title" or "209. Longitudinally-framed ships"
        re.compile(r'^(?:p\.\d+\s+)?(?:#{1,3}\s+)?(\d+[A-Z]?)\.\s+([A-Za-z][^\n:]+)', re.MULTILINE),
        # Tables: "Table 66" or "### Table 1"
        re.compile(r'^(?:p\.\d+\s+)?(?:#{1,3}\s+)?(Table\s+\d+[A-Z]?)(?:[:\.\s\-]+([^\n]*))?', re.MULTILINE | re.IGNORECASE),
        # Sections in Ordinance: "Section 14" or "14. Power of surveyor"
        re.compile(r'^(?:p\.\d+\s+)?(?:#{1,3}\s+)?(?:Section\s+)?(\d+[A-Z]?)\.\s+([A-Za-z][^\n:]+)', re.MULTILINE),
    ]

    chapter_pattern = re.compile(r'^(?:p\.\d+\s+)?(?:#{1,3}\s+)?(Chapter\s+[IVX\d]+[A-Z]?)\s*[\u2014\-:]*\s*([^\n]*)', re.IGNORECASE)

    for book in BOOKS_METADATA:
        b_id = book["id"]
        b_title = book["title"]
        s_page = book["start_page"]
        e_page = book["end_page"]

        print(f"\n--- Ingesting Book {b_id}: {book['short_title']} (Pages {s_page} - {e_page}) ---")

        current_chapter_title = "General"
        current_chapter_id = None

        # Collect raw text across pages with page offsets
        page_texts = []
        for p_idx in range(s_page - 1, min(e_page, len(doc))):
            p_no = p_idx + 1
            txt = doc[p_idx].get_text()
            page_texts.append((p_no, txt))

        # First pass: parse chapters and rules
        # Let's extract items sequentially per page
        for p_no, txt in page_texts:
            lines = txt.split('\n')
            
            # Check for chapter header on page
            for l in lines:
                l_s = l.strip()
                ch_m = chapter_pattern.match(l_s)
                if ch_m:
                    ch_no = ch_m.group(1).strip()
                    ch_name = ch_m.group(2).strip() or "General Provisions"
                    current_chapter_title = f"{ch_no}: {ch_name}"
                    cur.execute(
                        "INSERT INTO chapters (book_id, chapter_no, title) VALUES (?, ?, ?)",
                        (b_id, ch_no, ch_name)
                    )
                    current_chapter_id = cur.lastrowid
                    break

            # Find rule matches in page text
            # We look for lines matching rule/table numbers
            rule_splits = []
            for idx, line in enumerate(lines):
                line_s = line.strip()
                
                # Check Table
                t_m = re.match(r'^(?:p\.\d+\s+)?(?:#{1,3}\s+)?(Table\s+\d+[A-Z]?)(?:[:\.\s\-]+([^\n]*))?', line_s, re.IGNORECASE)
                if t_m:
                    t_no = t_m.group(1).title()
                    t_title = (t_m.group(2) or "").strip() or f"Schedule {t_no}"
                    rule_splits.append((idx, t_no, t_title, "table"))
                    continue

                # Check Rule / Section
                r_m = re.match(r'^(?:p\.\d+\s+)?(?:#{1,3}\s+)?(\d+[A-Z]?)\.\s+([A-Za-z][^\n:]+)', line_s)
                if r_m:
                    num_str = r_m.group(1).strip()
                    title_str = r_m.group(2).strip()
                    # Filter out false positives (e.g. subclauses like '1. A ship built...' inside rules)
                    # Real rule titles are short, typically under 80 chars and don't end in punctuation
                    if len(title_str) < 85 and not title_str.endswith((';', ',', 'and', 'or', 'that')):
                        prefix = "Section" if b_id == 13 else "Rule"
                        rule_splits.append((idx, f"{prefix} {num_str}", title_str, "rule"))

            if not rule_splits:
                # If page has continuous text without a rule header, we append to previous rule if exists
                if cur.lastrowid:
                    cur.execute("SELECT content_text, content_html FROM rules WHERE id = ?", (cur.lastrowid,))
                    row = cur.fetchone()
                    if row:
                        appended_text = row[0] + "\n\n" + txt.strip()
                        appended_html = text_to_html(cur.execute("SELECT rule_title FROM rules WHERE id = ?", (cur.lastrowid,)).fetchone()[0], appended_text)
                        cur.execute("UPDATE rules SET content_text = ?, content_html = ? WHERE id = ?", (appended_text, appended_html, cur.lastrowid))
                continue

            # Split page text by detected rule headers
            for s_i, (line_idx, item_no, item_title, item_type) in enumerate(rule_splits):
                start_l = line_idx + 1
                end_l = rule_splits[s_i + 1][0] if s_i + 1 < len(rule_splits) else len(lines)
                body_lines = lines[start_l:end_l]
                body_text = "\n".join(body_lines).strip()
                if not body_text:
                    body_text = f"{item_no} — {item_title}. Refer to official gazette Schedule and Table entries."

                num_int = None
                num_digits = re.findall(r'\d+', item_no)
                if num_digits:
                    num_int = int(num_digits[0])

                tags = extract_tags(item_title, body_text)
                citation = f"{b_title}, {item_no}"
                html_body = text_to_html(f"{item_no}: {item_title}", body_text)

                cur.execute("""
                INSERT INTO rules (
                    book_id, chapter_id, chapter_title, rule_no, rule_num_int,
                    rule_title, content_text, content_html, page_no, tags, citation_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    b_id, current_chapter_id, current_chapter_title, item_no, num_int,
                    item_title, body_text, html_body, p_no, tags, citation
                ))

                rule_id = cur.lastrowid
                # Insert into FTS5
                cur.execute("""
                INSERT INTO rules_fts (rowid, rule_no, rule_title, content_text, tags, book_title)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (rule_id, item_no, item_title, body_text, tags, b_title))

                total_rules += 1

        conn.commit()

    print(f"\n[+] Ingestion Complete! Successfully indexed {total_rules} rules/sections across all 13 books.")
    print(f"[+] Database saved to: {DB_PATH}")

    # Verification query
    cur.execute("SELECT COUNT(*) FROM books")
    b_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM rules")
    r_count = cur.fetchone()[0]
    print(f"[+] Verification: {b_count} Books, {r_count} Rules/Tables in database.")

    # Test FTS5 search
    test_queries = ["Rule 209", "Table 66", "collision bulkhead", "stability", "freeboard", "fire pump"]
    print("\n--- Test Search Sample Results ---")
    for q in test_queries:
        cur.execute("""
        SELECT r.rule_no, r.rule_title, b.short_title, r.page_no
        FROM rules_fts f
        JOIN rules r ON f.rowid = r.id
        JOIN books b ON r.book_id = b.id
        WHERE rules_fts MATCH ?
        LIMIT 2
        """, (q,))
        matches = cur.fetchall()
        print(f"Query '{q}': {len(matches)} matches found -> {matches}")

    conn.close()


if __name__ == '__main__':
    parse_and_ingest()
