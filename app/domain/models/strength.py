"""
Domain models for Hull Longitudinal Strength and Midship Section Calculations.
Statutory Reference: Rules 209 & 223, Schedule Tables 66 & 67 (SRO 308/Law-2001).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class MidshipElement:
    """Represents a continuous structural member contributing to the midship section modulus."""
    id: str
    name: str
    category: str  # 'deck', 'bottom', 'side', 'inner_bottom', 'girder'
    width_mm: float  # breadth or web depth
    thk_mm: float  # thickness
    quantity: int = 1
    area_mm2: float = 0.0
    lever_y_mm: float = 0.0  # height above baseline (keel outer face)
    own_inertia_mm4: float = 0.0  # i_0 = 1/12 * b * t^3 (or 1/12 * t * h^3 for vertical plates)
    is_vertical: bool = False
    is_included: bool = True
    notes: str = ""

    def __post_init__(self):
        if self.area_mm2 <= 0.0:
            self.area_mm2 = round(self.width_mm * self.thk_mm * self.quantity, 2)
        if self.own_inertia_mm4 <= 0.0:
            if self.is_vertical:
                self.own_inertia_mm4 = round((1.0 / 12.0) * (self.thk_mm * (self.width_mm ** 3)) * self.quantity, 2)
            else:
                self.own_inertia_mm4 = round((1.0 / 12.0) * (self.width_mm * (self.thk_mm ** 3)) * self.quantity, 2)


@dataclass
class BendingMoments:
    """Still water, wave, and total design bending moments per Rule 209."""
    m_sw_knm: float  # Still water bending moment (kN·m)
    m_wave_hog_knm: float  # Wave bending moment in hogging condition (kN·m)
    m_wave_sag_knm: float  # Wave bending moment in sagging condition (kN·m)
    m_total_hog_knm: float  # M_sw + M_w,hog (kN·m)
    m_total_sag_knm: float  # M_sw + |M_w,sag| (kN·m)
    m_design_knm: float  # Maximum governing design bending moment (kN·m)
    design_condition: str  # 'HOGGING' or 'SAGGING'
    wave_coefficient_cw: float
    shear_force_design_kn: float  # Estimated maximum hull girder shear force Q_t (kN)


@dataclass
class MidshipSectionProperties:
    """Calculated midship cross-section geometrical and mechanical properties."""
    elements: List[MidshipElement]
    total_area_cm2: float
    neutral_axis_above_keel_m: float  # y_NA from baseline (m)
    neutral_axis_above_keel_mm: float
    distance_to_deck_m: float  # D - y_NA (m)
    distance_to_deck_mm: float
    moment_of_inertia_cm4: float  # I_NA about horizontal neutral axis (cm^4)
    moment_of_inertia_m4: float  # I_NA in m^4
    modulus_deck_cm3: float  # Z_deck = I_NA / (D - y_NA)
    modulus_bottom_cm3: float  # Z_bottom = I_NA / y_NA
    modulus_actual_cm3: float  # min(Z_deck, Z_bottom)
    modulus_rule_required_cm3: float  # Rule statutory required minimum SM
    modulus_margin_cm3: float  # Z_act - Z_req
    modulus_margin_pct: float  # (Z_act - Z_req)/Z_req * 100


@dataclass
class Table66StressResult:
    """Hull girder stress evaluation per Schedule Table 66."""
    bending_stress_deck_n_mm2: float
    bending_stress_bottom_n_mm2: float
    max_bending_stress_n_mm2: float
    allowable_bending_stress_n_mm2: float = 130.0  # Table 66 Col 1

    hull_shear_stress_n_mm2: float = 0.0
    allowable_shear_stress_n_mm2: float = 70.0  # Table 66 Col 3

    equivalent_stress_n_mm2: float = 0.0
    allowable_equivalent_stress_n_mm2: float = 150.0  # Table 66 Col 4

    status_bending: str = "COMPLIANT"
    status_shear: str = "COMPLIANT"
    status_equivalent: str = "COMPLIANT"
    is_overall_compliant: bool = True


@dataclass
class LocalMemberStrengthItem:
    """Individual local structural member stress audit per Schedule Table 67."""
    member_name: str
    member_type: str  # 'floor', 'web_frame', 'pillar', 'bulkhead', 'hatch_beam', 'rudder'
    governing_load_desc: str
    calculated_stress_n_mm2: float
    allowable_stress_n_mm2: float
    unit: str = "N/mm²"
    status: str = "COMPLIANT"
    margin: float = 0.0
    notes: str = ""


@dataclass
class HullStrengthReport:
    """Comprehensive statutory hull strength calculation report."""
    vessel_name: str
    vessel_type: str
    route_name: str
    factor_kt: float
    factor_kz: float
    particulars: Dict[str, Any]
    bending_moments: BendingMoments
    midship_properties: MidshipSectionProperties
    table_66_stresses: Table66StressResult
    local_stresses: List[LocalMemberStrengthItem]
    overall_status: str  # 'COMPLIANT' or 'NON-COMPLIANT'
    executive_summary: str
