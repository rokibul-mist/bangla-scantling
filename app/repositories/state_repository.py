import os
import json
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data_extracted.json')
SCHEDULE_FILE = os.path.join(BASE_DIR, 'schedule_tables.json')
SAVED_STATE_FILE = os.path.join(BASE_DIR, 'saved_state.json')

class StateRepository:
    def __init__(self, base_dir: str = BASE_DIR):
        self.base_dir = base_dir
        self.data_file = os.path.join(base_dir, 'data_extracted.json')
        self.schedule_file = os.path.join(base_dir, 'schedule_tables.json')
        self.saved_state_file = os.path.join(base_dir, 'saved_state.json')
        self._raw_cache: Optional[Dict[str, Any]] = None

    def get_raw_data(self) -> Dict[str, Any]:
        """
        Loads the baseline extracted raw data and empirical schedule tables.
        """
        if self._raw_cache is None:
            raw = {}
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
            if os.path.exists(self.schedule_file):
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    raw['empirical_tables'] = json.load(f)
            self._raw_cache = raw
        return json.loads(json.dumps(self._raw_cache))

    def get_saved_state(self) -> Optional[Dict[str, Any]]:
        """
        Loads saved user state from saved_state.json if it exists.
        """
        if os.path.exists(self.saved_state_file):
            try:
                with open(self.saved_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def get_state(self) -> Dict[str, Any]:
        """
        Loads saved user state from saved_state.json, or falls back to baseline raw data.
        """
        saved = self.get_saved_state()
        if saved:
            return saved
        return self.get_raw_data()

    def save_state(self, state: Dict[str, Any]) -> bool:
        """
        Persists current user state to saved_state.json.
        """
        try:
            with open(self.saved_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def reset_state(self) -> bool:
        """
        Removes saved_state.json to revert to baseline defaults.
        """
        if os.path.exists(self.saved_state_file):
            try:
                os.remove(self.saved_state_file)
                return True
            except Exception:
                return False
        return True
