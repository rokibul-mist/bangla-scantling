import os
import json
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULE_FILE = os.path.join(BASE_DIR, 'schedule_tables.json')

class EmpiricalTablesRepository:
    def __init__(self, schedule_file: str = SCHEDULE_FILE):
        self.schedule_file = schedule_file
        self._tables_cache: Optional[List[Dict[str, Any]]] = None

    def get_all_tables(self) -> List[Dict[str, Any]]:
        """
        Loads all 67 statutory empirical rule tables.
        """
        if self._tables_cache is None:
            if os.path.exists(self.schedule_file):
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    self._tables_cache = json.load(f)
            else:
                self._tables_cache = []
        return self._tables_cache

    def get_table_by_id(self, table_id: str) -> Optional[Dict[str, Any]]:
        tables = self.get_all_tables()
        for t in tables:
            if str(t.get('id', '')).lower() == str(table_id).lower() or str(t.get('table_no', '')).lower() == str(table_id).lower():
                return t
        return None
