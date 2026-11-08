import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.repositories.statutory_repository import StatutoryRepository
from app.services.statutory_service import StatutoryService

repo = StatutoryRepository()
svc = StatutoryService(repo)

overview = svc.get_library_overview()
print(f"Total Books: {overview['total_books']}, Total Rules: {overview['total_rules']}")

queries = ['Rule 209', 'Table 66', 'collision bulkhead', 'freeboard', 'stability', 'fire pump', 'lifejacket', 'gross tonnage']
for q in queries:
    res = svc.search_rules(q, limit=3)
    count = res['total_matches']
    if res['results']:
        first = res['results'][0]
        print(f"Query [{q:18s}]: {count:2d} matches -> {first['rule_no']} ({first['book_short_title']}) p.{first['page_no']}: {first['rule_title'][:40]}")
    else:
        print(f"Query [{q:18s}]: 0 matches")
