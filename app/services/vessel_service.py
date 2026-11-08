import copy
from typing import Dict, Any, List, Optional
from app.repositories.vessel_repository import VesselRepository
from app.repositories.state_repository import StateRepository
from app.services.calculation_service import CalculationService

class VesselService:
    def __init__(
        self,
        vessel_repo: Optional[VesselRepository] = None,
        state_repo: Optional[StateRepository] = None
    ):
        self.vessel_repo = vessel_repo or VesselRepository()
        self.state_repo = state_repo or StateRepository()
        self._ensure_seeds()

    def _ensure_seeds(self):
        """Seeds default vessels if the database is brand new and empty"""
        existing = self.vessel_repo.list_vessels()
        if not existing:
            self._seed_flagship_vessel()

    def _seed_flagship_vessel(self):
        """Seeds the current flagship evaluated vessel (M.V. CROWN MARINERS - 67)"""
        state = self.state_repo.get_state()
        if state and 'dashboard_inputs' in state:
            try:
                self.save_vessel_from_state(
                    state,
                    vessel_id="vsl_crown_mariners_67",
                    custom_meta={
                        "owner": "Crown Navigation Ltd.",
                        "yard_ref": "YD-2026/089",
                        "notes": "Flagship 69.85m Steel Cargo Vessel fully compliant with DOS SRO 308/2001 & Inland Shipping Rules."
                    }
                )
            except Exception as e:
                print(f"[VesselService] Seeding flagship error: {e}")

    def list_vessels(
        self,
        query: Optional[str] = None,
        vessel_type: Optional[str] = None,
        sort_by: str = 'updated_at',
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        return self.vessel_repo.list_vessels(
            query=query,
            vessel_type=vessel_type,
            sort_by=sort_by,
            ascending=ascending
        )

    def get_vessel(self, vessel_id: str) -> Optional[Dict[str, Any]]:
        return self.vessel_repo.get_vessel(vessel_id)

    def save_vessel_from_state(
        self,
        state: Dict[str, Any],
        vessel_id: Optional[str] = None,
        custom_meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extracts particulars, summaries, and saves the complete calculation state into the vessel database.
        """
        custom_meta = custom_meta or {}
        inputs = state.get('dashboard_inputs', {}) or {}
        ls_summary = state.get('lightship_summary', {}) or {}
        stats = state.get('summary_stats', {}) or {}

        vessel_name = custom_meta.get('vessel_name') or inputs.get('vessel_name') or 'M.V. CROWN MARINERS - 67'
        vessel_type = custom_meta.get('vessel_type') or inputs.get('vessel_type') or 'Steel Body Cargo Vessel'
        hull_type = custom_meta.get('hull_type') or inputs.get('hull_type') or 'Single Hull'
        route = custom_meta.get('route') or inputs.get('route') or 'Inland & bay crossing'
        owner = custom_meta.get('owner') or inputs.get('owner') or ''
        yard_ref = custom_meta.get('yard_ref') or inputs.get('yard_ref') or ''
        notes = custom_meta.get('notes') or inputs.get('notes') or ''

        # Ensure latest synchronized calculation
        evaluated_state = CalculationService.compute_all_calculations(state)

        ls_summary = evaluated_state.get('lightship_summary', {}) or {}
        stats = evaluated_state.get('summary_stats', {}) or {}

        particulars = {
            'lbp': float(inputs.get('lbp', 69.85) or 69.85),
            'breadth': float(inputs.get('breadth', 13.41) or 13.41),
            'depth': float(inputs.get('depth', 5.18) or 5.18),
            'draft': float(inputs.get('draft', 4.0) or 4.0),
            'cb': float(inputs.get('cb', 0.75) or 0.75),
            'frame_spacing': float(inputs.get('frame_spacing', 550) or 550),
            'speed': float(inputs.get('speed', 10.0) or 10.0),
        }

        results_summary = {
            'net_steel_tonnes': float(ls_summary.get('net_steel_t', 704.38) or 704.38),
            'lightship_tonnes': float(ls_summary.get('total_lightship_t', 1098.83) or 1098.83),
            'compliant_count': int(stats.get('compliant_count', 0)),
            'total_count': int(stats.get('total_count', 0)),
            'compliance_pct': float(stats.get('compliance_pct', 100.0)),
            'status': str(stats.get('status', 'COMPLIANT')),
            'factor_kt': float(inputs.get('effective_kt', inputs.get('kt', 1.0)) or 1.0),
            'factor_kz': float(inputs.get('effective_kz', inputs.get('kz', 1.0)) or 1.0)
        }

        # Embed state payload
        record = {
            'id': vessel_id or custom_meta.get('id'),
            'vessel_name': vessel_name,
            'vessel_type': vessel_type,
            'hull_type': hull_type,
            'route': route,
            'owner': owner,
            'yard_ref': yard_ref,
            'notes': notes,
            'particulars': particulars,
            'results_summary': results_summary,
            'state_data': evaluated_state
        }

        return self.vessel_repo.save_vessel(record)

    def load_vessel_into_workspace(self, vessel_id: str) -> Optional[Dict[str, Any]]:
        """
        Loads the selected vessel from the database into the active workspace,
        saving it to saved_state.json and returning the live evaluated state.
        """
        vessel = self.vessel_repo.get_vessel(vessel_id)
        if not vessel or 'state_data' not in vessel:
            return None

        state_data = copy.deepcopy(vessel['state_data'])
        # Re-compute calculations to verify integrity
        evaluated = CalculationService.compute_all_calculations(state_data)
        evaluated['active_vessel_id'] = vessel_id
        evaluated['active_vessel_name'] = vessel.get('vessel_name')

        # Persist as the active state on disk
        self.state_repo.save_state(evaluated)
        return evaluated

    def duplicate_vessel(self, vessel_id: str, new_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Duplicates an existing vessel record to create a new calculation variant.
        """
        original = self.vessel_repo.get_vessel(vessel_id)
        if not original:
            return None

        clone = copy.deepcopy(original)
        clone['id'] = None  # Force generation of new ID
        orig_name = original.get('vessel_name', 'Vessel')
        clone['vessel_name'] = new_name or f"{orig_name} (Copy)"
        clone['notes'] = f"Cloned from {orig_name}. {original.get('notes', '')}".strip()

        if 'state_data' in clone and 'dashboard_inputs' in clone['state_data']:
            clone['state_data']['dashboard_inputs']['vessel_name'] = clone['vessel_name']

        return self.vessel_repo.save_vessel(clone)

    def delete_vessel(self, vessel_id: str) -> bool:
        return self.vessel_repo.delete_vessel(vessel_id)

    def import_vessel(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imports a vessel record or .dos project file payload into the database.
        """
        # If payload is raw state or .dos export
        if 'dashboard_inputs' in payload and 'state_data' not in payload:
            return self.save_vessel_from_state(payload)
        
        # If payload is already a full vessel record
        if 'state_data' in payload:
            payload['id'] = None  # Generate new ID on import to avoid clashing
            return self.vessel_repo.save_vessel(payload)

        raise ValueError("Invalid vessel data format")
