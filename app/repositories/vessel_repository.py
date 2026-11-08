import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VESSELS_DIR = os.path.join(BASE_DIR, 'data', 'vessels')
VESSELS_INDEX_FILE = os.path.join(BASE_DIR, 'data', 'vessels_index.json')

class VesselRepository:
    def __init__(self, base_dir: str = BASE_DIR):
        self.base_dir = base_dir
        self.vessels_dir = os.path.join(base_dir, 'data', 'vessels')
        self.index_file = os.path.join(base_dir, 'data', 'vessels_index.json')
        os.makedirs(self.vessels_dir, exist_ok=True)
        self._ensure_index_file()

    def _ensure_index_file(self):
        """Ensures the vessels_index.json exists"""
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

    def _read_index(self) -> List[Dict[str, Any]]:
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _write_index(self, index: List[Dict[str, Any]]):
        temp_file = self.index_file + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, self.index_file)

    def _vessel_file_path(self, vessel_id: str) -> str:
        safe_id = "".join(c for c in vessel_id if c.isalnum() or c in ('-', '_')).rstrip()
        return os.path.join(self.vessels_dir, f"{safe_id}.json")

    def list_vessels(
        self,
        query: Optional[str] = None,
        vessel_type: Optional[str] = None,
        sort_by: str = 'updated_at',
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Returns list of vessel summary cards from the database index.
        """
        items = self._read_index()

        if query:
            q = query.lower().strip()
            items = [
                v for v in items
                if q in str(v.get('vessel_name', '')).lower()
                or q in str(v.get('owner', '')).lower()
                or q in str(v.get('vessel_type', '')).lower()
                or q in str(v.get('notes', '')).lower()
            ]

        if vessel_type and vessel_type != 'all':
            vt = vessel_type.lower().strip()
            items = [
                v for v in items
                if vt in str(v.get('vessel_type', '')).lower()
            ]

        def get_sort_key(item):
            val = item.get(sort_by)
            if val is None:
                return ''
            return val

        items.sort(key=get_sort_key, reverse=not ascending)
        return items

    def get_vessel(self, vessel_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves full vessel record including calculation state from disk.
        """
        path = self._vessel_file_path(vessel_id)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[VesselRepository] Error reading {path}: {e}")
                return None
        return None

    def save_vessel(self, vessel_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves or updates a vessel record in the database and updates the index.
        """
        v_id = vessel_record.get('id')
        if not v_id:
            v_id = f"vsl_{uuid.uuid4().hex[:12]}"
            vessel_record['id'] = v_id

        now_iso = datetime.now().isoformat()
        if 'created_at' not in vessel_record or not vessel_record['created_at']:
            vessel_record['created_at'] = now_iso
        vessel_record['updated_at'] = now_iso

        # 1. Write full vessel record file
        path = self._vessel_file_path(v_id)
        temp_path = path + '.tmp'
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(vessel_record, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, path)

        # 2. Extract summary index entry (excluding heavy calculation arrays)
        summary = {
            'id': v_id,
            'vessel_name': vessel_record.get('vessel_name', 'Unnamed Vessel'),
            'vessel_type': vessel_record.get('vessel_type', 'Steel Body Cargo Vessel'),
            'hull_type': vessel_record.get('hull_type', 'Single Hull'),
            'route': vessel_record.get('route', 'Inland & bay crossing'),
            'owner': vessel_record.get('owner', ''),
            'yard_ref': vessel_record.get('yard_ref', ''),
            'notes': vessel_record.get('notes', ''),
            'created_at': vessel_record.get('created_at'),
            'updated_at': vessel_record.get('updated_at'),
            'particulars': vessel_record.get('particulars', {}),
            'results_summary': vessel_record.get('results_summary', {})
        }

        # 3. Update index
        index = self._read_index()
        idx_map = {item['id']: i for i, item in enumerate(index)}
        if v_id in idx_map:
            index[idx_map[v_id]] = summary
        else:
            index.insert(0, summary)

        self._write_index(index)
        return summary

    def delete_vessel(self, vessel_id: str) -> bool:
        """
        Deletes a vessel record and removes it from the index.
        """
        path = self._vessel_file_path(vessel_id)
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"[VesselRepository] Error removing {path}: {e}")

        index = self._read_index()
        new_index = [item for item in index if item.get('id') != vessel_id]
        if len(new_index) != len(index):
            self._write_index(new_index)
            return True
        return False
