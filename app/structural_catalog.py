"""
Compatibility shim for app.structural_catalog
Re-exports from app.domain.catalog.structural_catalog
"""
from app.domain.catalog.structural_catalog import STRUCTURAL_MEMBERS, get_active_members

__all__ = ["STRUCTURAL_MEMBERS", "get_active_members"]
