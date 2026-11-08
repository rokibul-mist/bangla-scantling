from typing import Dict, Any, Optional
from app.repositories.state_repository import StateRepository
from app.services.calculation_service import CalculationService

class StateService:
    def __init__(self, state_repo: Optional[StateRepository] = None):
        self.state_repo = state_repo or StateRepository()

    def get_initial_state(self) -> Dict[str, Any]:
        """
        Loads baseline state, applies saved overrides if present, and recomputes all formulas.
        """
        raw_data = self.state_repo.get_raw_data()
        master = CalculationService.compute_all_calculations(raw_data)
        
        saved = self.state_repo.get_saved_state()
        if saved:
            if not isinstance(saved, dict):
                saved = {}
            for k, v in saved.items():
                if isinstance(v, dict) and k in master and isinstance(master[k], dict):
                    master[k].update(v)
                elif v is not None:
                    master[k] = v
            # Recompute to ensure all derived values are consistent
            master = CalculationService.compute_all_calculations(master)

        master['application_form_pages'] = raw_data.get('application_form_pages', [])
        master['empirical_tables'] = raw_data.get('empirical_tables', [])
        return master

    def save_state(self, state_data: Dict[str, Any]) -> bool:
        return self.state_repo.save_state(state_data)

    def get_saved_state(self) -> Optional[Dict[str, Any]]:
        saved = self.state_repo.get_saved_state()
        if saved and isinstance(saved, dict):
            if not saved.get('application_form_pages') or not saved.get('empirical_tables'):
                raw_data = self.state_repo.get_raw_data()
                if not saved.get('application_form_pages'):
                    saved['application_form_pages'] = raw_data.get('application_form_pages', [])
                if not saved.get('empirical_tables'):
                    saved['empirical_tables'] = raw_data.get('empirical_tables', [])
        return saved

    def reset_state(self) -> bool:
        return self.state_repo.reset_state()
