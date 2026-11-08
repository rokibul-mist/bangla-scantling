import sqlite3

conn = sqlite3.connect(':memory:')
cur = conn.cursor()

cur.execute("""
CREATE VIRTUAL TABLE rules_fts USING fts5(
    rule_no,
    rule_title,
    content_text,
    tags,
    book_title
)
""")

cur.execute("""
INSERT INTO rules_fts (rowid, rule_no, rule_title, content_text, tags, book_title)
VALUES (1, 'Rule 209', 'Longitudinal Strength', 'Every ship shall have sufficient hull girder section modulus to withstand wave bending moments and still water bending moments.', 'strength, modulus', 'Construction Rules 2001')
""")

cur.execute("SELECT rowid, snippet(rules_fts, 2, '<b>', '</b>', '...', 10) FROM rules_fts WHERE rules_fts MATCH 'bending*'")
print("Snippet test on standalone FTS5:", cur.fetchall())
