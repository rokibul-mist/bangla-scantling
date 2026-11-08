from app.repositories.state_repository import StateRepository
from app.repositories.empirical_tables_repository import EmpiricalTablesRepository
from app.repositories.vessel_repository import VesselRepository
from app.services.state_service import StateService
from app.services.calculation_service import CalculationService
from app.services.vessel_service import VesselService

_state_repo = StateRepository()
_tables_repo = EmpiricalTablesRepository()
_state_service = StateService(_state_repo)
_vessel_repo = VesselRepository()
_vessel_service = VesselService(_vessel_repo, _state_repo)

def get_state_repository() -> StateRepository:
    return _state_repo

def get_tables_repository() -> EmpiricalTablesRepository:
    return _tables_repo

def get_state_service() -> StateService:
    return _state_service

def get_calculation_service() -> CalculationService:
    return CalculationService()

def get_vessel_repository() -> VesselRepository:
    return _vessel_repo

def get_vessel_service() -> VesselService:
    return _vessel_service
