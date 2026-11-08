"""
Central Table Interpolation Registry.
Coordinates and dispatches structural members to their dedicated statutory rule interpolators.
"""

from typing import Dict, Any, Optional, Type
from .base_interpolator import BaseTableInterpolator, InterpolationResult

from .table_00_rule08_min_plate import Table00Rule08MinPlateInterpolator
from .table_01_keel import Table01KeelInterpolator
from .table_02_bottom import Table02BottomInterpolator
from .table_03_bilge import Table03BilgeInterpolator
from .table_04_side import Table04SideInterpolator
from .table_05_deck_hatch import Table05DeckHatchInterpolator
from .table_06_deck_all import Table06DeckAllInterpolator
from .table_07_stem import (
    Table07StemInterpolator,
    Table08BarStemInterpolator,
    Table09SternBarInterpolator,
    Table10PropellerPostInterpolator,
    Table11SolePieceInterpolator,
    Table12PropellerBossInterpolator
)
from .table_13_floors import Table13FloorsInterpolator
from .table_14_16_keelson import Table1416KeelsonInterpolator, Table16CenterKeelsonInterpolator, Table15SideKeelsonInterpolator
from .table_17_frames import Table17FramesInterpolator
from .table_18_19_web_frames import Table1819WebFramesInterpolator
from .table_20_beams import Table20BeamsInterpolator
from .table_21_girders import Table21GirdersInterpolator, Table29DeckWebBeamsInterpolator
from .table_66_longitudinals import Table66LongitudinalsInterpolator
from .table_22_23_pillars import Table2223PillarsInterpolator
from .table_24_collision_bhd import Table24CollisionBhdInterpolator
from .table_25_26_bulkheads import Table2526BulkheadsInterpolator
from .table_27_28_tank_bulkheads import Table2728TankBulkheadsInterpolator
from .table_30_31_coamings import Table3031CoamingsInterpolator
from .table_32_35_hatch_beams_covers import Table3235HatchBeamsCoversInterpolator
from .table_36_37_roof import Table36RoofBeamsInterpolator, Table37RoofGirdersInterpolator
from .table_39_43_rudder import (
    Table3943RudderInterpolator,
    Table41RudderCouplingBoltsInterpolator,
    Table44SteeringChainsInterpolator
)
from .table_46_47_equipment import Table4546EquipmentInterpolator
from .table_48_49_bulwark_locker import Table4748BulwarkLockerInterpolator
from .table_49_50_struts import Table49VStrutInterpolator, Table50IStrutInterpolator
from .table_54_57_piping import Table54PipeWallInterpolator, Table57BilgePipeInterpolator


class TableInterpolationRegistry:
    """Registry coordinating empirical statutory table calculations."""

    _MAPPING: Dict[str, Type[BaseTableInterpolator]] = {
        # Rule 8(1) Statutory Minimum Hull Material
        "mat_min_hull": Table00Rule08MinPlateInterpolator,

        # Plating (Tables 1-7)
        "plate_keel": Table01KeelInterpolator,
        "plate_keel_width": Table01KeelInterpolator,
        "w_keel": Table01KeelInterpolator,
        "plate_bottom": Table02BottomInterpolator,
        "plate_bilge": Table03BilgeInterpolator,
        "plate_chine": Table03BilgeInterpolator,
        "plate_rake": Table02BottomInterpolator,
        "plate_side": Table04SideInterpolator,
        "plate_sheer_strake": Table04SideInterpolator,
        "plate_main_deck": Table06DeckAllInterpolator,
        "plate_deck_all": Table06DeckAllInterpolator,
        "plate_hatchway_deck": Table05DeckHatchInterpolator,
        "plate_deck_hatch": Table05DeckHatchInterpolator,
        "plate_poop_deck": Table06DeckAllInterpolator,
        "plate_forecastle_deck": Table06DeckAllInterpolator,
        "plate_second_deck": Table06DeckAllInterpolator,
        "plate_upper_passenger_deck": Table06DeckAllInterpolator,
        "plate_nav_deck": Table06DeckAllInterpolator,
        "plate_wet_deck": Table06DeckAllInterpolator,
        "plate_deck_strip": Table06DeckAllInterpolator,
        "plate_inner_bottom": Table02BottomInterpolator,
        "plate_margin": Table02BottomInterpolator,
        "plate_stem": Table07StemInterpolator,
        "plate_transom": Table04SideInterpolator,
        "plate_inner_side": Table04SideInterpolator,
        "plate_tunnel_side": Table04SideInterpolator,
        "plate_solid_floor_web": Table02BottomInterpolator,
        "plate_hopper": Table02BottomInterpolator,

        # Stems & Stern Posts (Tables 7-12)
        "bar_stem": Table08BarStemInterpolator,
        "stern_frame_bar": Table09SternBarInterpolator,
        "propeller_post": Table10PropellerPostInterpolator,
        "sole_piece": Table11SolePieceInterpolator,
        "sole_piece_thk": Table11SolePieceInterpolator,
        "propeller_boss_thk": Table12PropellerBossInterpolator,

        # Floors & Keelsons (Tables 13, 14, 16)
        "stiff_floor_single": Table13FloorsInterpolator,
        "stiff_solid_floor": Table13FloorsInterpolator,
        "stiff_open_bracket_floor": Table13FloorsInterpolator,
        "stiff_bottom_transverse_barge": Table13FloorsInterpolator,
        "stiff_bottom_longitudinal": Table66LongitudinalsInterpolator,
        "stiff_inner_bottom_longitudinal": Table66LongitudinalsInterpolator,
        "stiff_centre_keelson": Table16CenterKeelsonInterpolator,
        "stiff_centre_girder": Table16CenterKeelsonInterpolator,
        "stiff_side_keelson": Table15SideKeelsonInterpolator,
        "stiff_side_girder": Table15SideKeelsonInterpolator,

        # Frames & Stringers (Tables 17, 18, 19)
        "stiff_main_frame": Table17FramesInterpolator,
        "stiff_side_frame": Table17FramesInterpolator,
        "stiff_side_longitudinal": Table17FramesInterpolator,
        "stiff_side_longitudinal_barge": Table17FramesInterpolator,
        "stiff_inner_side_longitudinal": Table17FramesInterpolator,
        "stiff_hopper_longitudinal": Table17FramesInterpolator,
        "stiff_web_frame": Table1819WebFramesInterpolator,
        "stiff_side_stringer": Table1819WebFramesInterpolator,

        # Decks & Girders (Tables 20, 21)
        "stiff_deck_beam": Table20BeamsInterpolator,
        "stiff_deck_longitudinal": Table20BeamsInterpolator,
        "stiff_deck_girder": Table21GirdersInterpolator,
        "stiff_deck_web_beam": Table29DeckWebBeamsInterpolator,
        "stiff_deck_transverse": Table29DeckWebBeamsInterpolator,

        # Superstructure Roof (Tables 36-37)
        "stiff_roof_beam": Table36RoofBeamsInterpolator,
        "stiff_roof_girder_side": Table37RoofGirdersInterpolator,
        "stiff_roof_girder_centre": Table37RoofGirdersInterpolator,

        # Pillars (Tables 22, 23)
        "pillar_solid_dia": Table2223PillarsInterpolator,
        "pillar_tubular_dia": Table2223PillarsInterpolator,

        # Bulkheads (Tables 24, 25, 26, 27, 28)
        "bhd_collision_pos": Table24CollisionBhdInterpolator,
        "plate_bhd_wt": Table2526BulkheadsInterpolator,
        "plate_bhd_collision": Table2526BulkheadsInterpolator,
        "plate_long_bhd": Table2526BulkheadsInterpolator,
        "plate_cofferdam": Table2526BulkheadsInterpolator,
        "plate_wash_bhd": Table2526BulkheadsInterpolator,
        "plate_pump_room_bhd": Table2526BulkheadsInterpolator,
        "stiff_bhd_transverse": Table2526BulkheadsInterpolator,
        "plate_bhd_tank": Table2728TankBulkheadsInterpolator,
        "plate_tank_boundary": Table2728TankBulkheadsInterpolator,
        "stiff_tank_bhd_web": Table2728TankBulkheadsInterpolator,
        "stiff_tank_bhd_stringer": Table2728TankBulkheadsInterpolator,

        # Coamings & Hatches (Tables 30, 31, 32, 34, 35)
        "plate_coaming_long": Table3031CoamingsInterpolator,
        "plate_coaming_trans": Table3031CoamingsInterpolator,
        "stiff_portable_hatch_beam": Table3235HatchBeamsCoversInterpolator,
        "stiff_hatch_end_beam": Table3235HatchBeamsCoversInterpolator,
        "stiff_hatch_side_girder": Table3235HatchBeamsCoversInterpolator,
        "stiff_hatch_cover": Table3235HatchBeamsCoversInterpolator,
        "stiff_superstructure_wall": Table3235HatchBeamsCoversInterpolator,
        "stiff_superstructure_frame": Table3235HatchBeamsCoversInterpolator,

        # Rudders & Steering (Tables 39-44)
        "rudder_stock_dia": Table3943RudderInterpolator,
        "rudder_stock_spade_dia": Table3943RudderInterpolator,
        "rudder_pintle_dia": Table3943RudderInterpolator,
        "rudder_coupling_bolts": Table41RudderCouplingBoltsInterpolator,
        "rudder_flange_thk": Table41RudderCouplingBoltsInterpolator,
        "steering_tiller_quadrant": Table44SteeringChainsInterpolator,
        "steering_chains_shackles": Table44SteeringChainsInterpolator,
        "rudder_blade_thk": Table04SideInterpolator,

        # Shaft Brackets / Struts (Tables 49-50)
        "v_strut_shaft": Table49VStrutInterpolator,
        "i_strut_shaft": Table50IStrutInterpolator,

        # Piping Systems (Tables 54, 57)
        "pipe_wall_thk": Table54PipeWallInterpolator,
        "pipe_main_bilge_dia": Table57BilgePipeInterpolator,

        # Equipment & Outfitting (Tables 45, 46, 47, 48)
        "equipment_number": Table4546EquipmentInterpolator,
        "anchor_mass": Table4546EquipmentInterpolator,
        "chain_cable_length": Table4546EquipmentInterpolator,
        "plate_bulwark": Table4748BulwarkLockerInterpolator,
        "plate_chain_locker_wall": Table4748BulwarkLockerInterpolator,
    }

    @classmethod
    def get_interpolator(cls, member_id: str) -> Optional[Type[BaseTableInterpolator]]:
        return cls._MAPPING.get(member_id)

    @classmethod
    def interpolate_member(
        cls,
        member_id: str,
        inputs: Dict[str, Any]
    ) -> Optional[InterpolationResult]:
        """Calculates dynamic table interpolation for the specified member."""
        interpolator_cls = cls.get_interpolator(member_id)
        if not interpolator_cls:
            return None
        try:
            return interpolator_cls.interpolate(inputs, member_id)
        except Exception as e:
            err_msg = str(e).encode('ascii', 'replace').decode('ascii')
            print(f"[TableInterpolationRegistry] Error interpolating {member_id}: {err_msg}")
            return None
