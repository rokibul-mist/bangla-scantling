"""
Auto-Comply Service.
Coordinates statutory analysis, optimal scantling sizing, and synchronized state updates.
"""

from typing import Dict, Any, List
import copy
import math

from app.services.calculation_service import CalculationService
from .optimizer import ScantlingOptimizer


class AutoComplyService:
    """
    Automated scantling compliance optimizer service.
    """

    # Mapping of primary calculation brain plate IDs to dashboard input keys
    PLATE_DASHBOARD_MAP = {
        "plate_keel": "t_keel",
        "plate_bottom": "t_bottom",
        "plate_bilge": "t_bilge",
        "plate_side": "t_side",
        "plate_main_deck": "t_deck",
        "plate_deck_all": "t_deck"
    }

    @classmethod
    def generate_compliance_preview(cls, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes current state, identifies non-compliant components,
        and generates a detailed comparison of proposed changes to achieve 100% compliance.
        """
        # Run calculation to obtain authoritative rule values and margins
        computed_master = CalculationService.compute_all_calculations(copy.deepcopy(current_state))
        brain_members = computed_master.get("calculation_brain", [])
        dashboard_inputs = copy.deepcopy(computed_master.get("dashboard_inputs", {}))
        custom_brain_dact = copy.deepcopy(computed_master.get("custom_brain_dact", {}))
        stiffener_custom_dims = copy.deepcopy(computed_master.get("stiffener_custom_dims", {}))

        spacing = float(dashboard_inputs.get("frame_spacing") or dashboard_inputs.get("spacing") or 550.0)
        lbp = float(dashboard_inputs.get("lbp") or dashboard_inputs.get("L") or 69.85)

        changes: List[Dict[str, Any]] = []
        old_compliant_count = sum(1 for m in brain_members if m.get("status") == "COMPLIANT")
        total_items = len(brain_members)

        for m in brain_members:
            m_id = m.get("id")
            m_type = m.get("type")
            m_name = m.get("name")
            unit = m.get("unit", "mm")
            rreq = float(m.get("rreq") or 0.0)
            dact = float(m.get("dact") or 0.0)
            status = m.get("status", "NON-COMPLIANT")
            margin = float(m.get("margin") or 0.0)

            # Skip items that are already strictly compliant
            if status == "COMPLIANT" and margin >= 0:
                continue

            # 1. Plating Member Optimization
            if m_type == "plate":
                opt_val = ScantlingOptimizer.find_compliant_plate_thickness(rreq, dact)
                # Ensure it has a positive margin
                if opt_val < rreq:
                    opt_val = math.ceil(rreq + 0.5)

                new_margin = round(opt_val - rreq, 2)
                custom_brain_dact[m_id] = opt_val

                # If mapped to dashboard input, synchronize dashboard input
                dash_key = cls.PLATE_DASHBOARD_MAP.get(m_id)
                if dash_key:
                    dashboard_inputs[dash_key] = opt_val

                bound_key = m.get("bound_plate_key")
                if bound_key:
                    dashboard_inputs[bound_key] = opt_val

                changes.append({
                    "id": m_id,
                    "name": m_name,
                    "type": "plate",
                    "category": m.get("category", "Plating"),
                    "unit": unit,
                    "rreq": rreq,
                    "old_val": dact,
                    "new_val": opt_val,
                    "old_profile": f"{dact} {unit}",
                    "new_profile": f"{opt_val} {unit}",
                    "new_margin": f"+{new_margin} {unit}",
                    "old_status": status,
                    "new_status": "COMPLIANT"
                })

            # 2. Stiffener Member Optimization
            elif m_type == "stiffener":
                w_key = m.get("welded_plate_key", "t_side")
                
                # Derive exact attached plate thickness matching CalculationService plate_thk_map
                plate_thk_map_defaults = {
                    't_keel': 12.0, 't_bottom': 10.0, 't_bilge': 10.0, 't_side': 10.0,
                    't_deck': 8.0, 't_inner_bottom': 10.0, 't_inner_side': 8.5,
                    't_collision_bhd': 10.0, 't_transverse_bhd': 8.5, 't_stem': 14.0,
                    't_transom': 12.0, 't_bulwark': 6.0, 't_poop_deck': 7.0,
                    't_forecastle_deck': 7.0, 't_nav_deck': 6.0, 't_second_deck': 6.5,
                    't_passenger_deck': 6.0, 't_wet_deck': 8.0, 't_tunnel_side': 8.5,
                    't_chine': 14.0, 't_rake': 12.0, 't_long_bhd': 10.0, 't_tank_bhd': 10.0,
                    't_cofferdam': 9.0, 't_wash_bhd': 9.0, 't_pump_room_bhd': 9.0,
                    't_deck_strip': 12.0, 't_floor_web': 10.0, 't_chain_locker': 8.0,
                    't_rudder': 10.0, 't_tank_boundary': 11.0,
                }
                tp = float(dashboard_inputs.get(w_key) or custom_brain_dact.get(w_key) or plate_thk_map_defaults.get(w_key, 10.0))

                cur_dim = stiffener_custom_dims.get(m_id, {}) or m.get("default_profile", {}) or {}
                pref_type = cur_dim.get("profile_type") or m.get("profile_type", "L")
                cur_hw = float(cur_dim.get("web_depth") or m.get("web_depth", 150))
                cur_tw = float(cur_dim.get("web_thk") or m.get("web_thk", 10))
                cur_bf = float(cur_dim.get("flange_width") or m.get("flange_width", 100))
                cur_tf = float(cur_dim.get("flange_thk") or m.get("flange_thk", 10))

                old_prof_label = f"{pref_type} {int(cur_hw)}x{int(cur_bf)}x{int(cur_tw)}"
                if cur_tf > 0 and cur_tf != cur_tw:
                    old_prof_label += f"/{int(cur_tf)}"

                # Check for multi-criterion component minimums
                raw_comps = m.get('components') or m.get('derivation', {}).get('components') or []
                min_tw = 0.0
                min_fa = 0.0
                min_bf = 0.0
                for c in raw_comps:
                    p = c.get('param')
                    rq = float(c.get('rreq', 0.0))
                    if p == 'web_thk':
                        min_tw = max(min_tw, rq)
                    elif p in ['face_area', 'flange_area']:
                        min_fa = max(min_fa, rq)
                    elif p in ['face_width', 'flange_width']:
                        min_bf = max(min_bf, rq)

                opt_prof = ScantlingOptimizer.find_compliant_stiffener_profile(
                    rreq_z=rreq,
                    spacing=spacing,
                    tp=tp,
                    preferred_type=pref_type,
                    current_hw=cur_hw,
                    current_tw=cur_tw,
                    current_bf=cur_bf,
                    current_tf=cur_tf,
                    min_web_thk=min_tw,
                    min_face_area=min_fa,
                    min_face_width=min_bf
                )

                stiffener_custom_dims[m_id] = {
                    "profile_type": opt_prof["profile_type"],
                    "web_depth": opt_prof["web_depth"],
                    "web_thk": opt_prof["web_thk"],
                    "flange_width": opt_prof["flange_width"],
                    "flange_thk": opt_prof["flange_thk"]
                }

                changes.append({
                    "id": m_id,
                    "name": m_name,
                    "type": "stiffener",
                    "category": m.get("category", "Stiffeners"),
                    "unit": unit,
                    "rreq": rreq,
                    "old_val": dact,
                    "new_val": opt_prof["prov_z"],
                    "old_profile": old_prof_label,
                    "new_profile": opt_prof["label"],
                    "new_margin": f"+{opt_prof['margin']} {unit}",
                    "old_status": status,
                    "new_status": "COMPLIANT"
                })

            # 3. Dimension / Limit Optimization
            else:
                if m_id == "frame_spacing_limit":
                    # Frame spacing limit compliance
                    max_allowed = rreq
                    new_spacing = min(spacing, max_allowed)
                    dashboard_inputs["frame_spacing"] = new_spacing
                    dashboard_inputs["spacing"] = new_spacing
                    custom_brain_dact[m_id] = new_spacing
                    new_margin = round(max_allowed - new_spacing, 2)
                    changes.append({
                        "id": m_id,
                        "name": m_name,
                        "type": "dimension",
                        "category": m.get("category", "Limits"),
                        "unit": unit,
                        "rreq": rreq,
                        "old_val": spacing,
                        "new_val": new_spacing,
                        "old_profile": f"{spacing} {unit}",
                        "new_profile": f"{new_spacing} {unit}",
                        "new_margin": f"{new_margin} {unit}",
                        "old_status": status,
                        "new_status": "COMPLIANT"
                    })
                elif m_id == "bhd_collision_pos":
                    min_pos = round(0.05 * lbp, 2)
                    max_pos = round(0.08 * lbp, 2)
                    opt_pos = round((min_pos + max_pos) / 2.0, 2)
                    dashboard_inputs["actual_collision_bhd_pos"] = opt_pos
                    custom_brain_dact[m_id] = opt_pos
                    changes.append({
                        "id": m_id,
                        "name": m_name,
                        "type": "dimension",
                        "category": m.get("category", "Bulkheads"),
                        "unit": unit,
                        "rreq": rreq,
                        "old_val": dact,
                        "new_val": opt_pos,
                        "old_profile": f"{dact} {unit}",
                        "new_profile": f"{opt_pos} {unit}",
                        "new_margin": f"+{round(opt_pos - min_pos, 2)} {unit}",
                        "old_status": status,
                        "new_status": "COMPLIANT"
                    })
                else:
                    opt_val = math.ceil(rreq) if unit == "mm" else round(rreq * 1.05, 1)
                    custom_brain_dact[m_id] = opt_val
                    dashboard_inputs[m_id] = opt_val
                    changes.append({
                        "id": m_id,
                        "name": m_name,
                        "type": "dimension",
                        "category": m.get("category", "Equipment"),
                        "unit": unit,
                        "rreq": rreq,
                        "old_val": dact,
                        "new_val": opt_val,
                        "old_profile": f"{dact} {unit}",
                        "new_profile": f"{opt_val} {unit}",
                        "new_margin": f"+{round(opt_val - rreq, 2)} {unit}",
                        "old_status": status,
                        "new_status": "COMPLIANT"
                    })

        # Assemble updated proposed state
        proposed_state = copy.deepcopy(current_state)
        proposed_state["dashboard_inputs"] = dashboard_inputs
        proposed_state["custom_brain_dact"] = custom_brain_dact
        proposed_state["stiffener_custom_dims"] = stiffener_custom_dims

        # Verify new compliance with full master computation
        recomputed = CalculationService.compute_all_calculations(proposed_state)
        new_compliant_count = sum(1 for m in recomputed.get("calculation_brain", []) if m.get("status") == "COMPLIANT")

        return {
            "status": "success",
            "total_items": total_items,
            "old_compliant_count": old_compliant_count,
            "new_compliant_count": new_compliant_count,
            "items_updated_count": len(changes),
            "changes": changes,
            "proposed_state": {
                "dashboard_inputs": dashboard_inputs,
                "custom_brain_dact": custom_brain_dact,
                "stiffener_custom_dims": stiffener_custom_dims
            }
        }

    @classmethod
    def apply_compliance(cls, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes auto-compliance on the provided state, recomputes all formulas,
        and returns the fully compliant master state.
        """
        preview = cls.generate_compliance_preview(current_state)
        prop = preview["proposed_state"]

        new_state = copy.deepcopy(current_state)
        new_state["dashboard_inputs"].update(prop["dashboard_inputs"])
        new_state["custom_brain_dact"] = prop["custom_brain_dact"]
        new_state["stiffener_custom_dims"] = prop["stiffener_custom_dims"]

        master = CalculationService.compute_all_calculations(new_state)
        return {
            "status": "success",
            "message": f"Successfully updated {preview['items_updated_count']} scantlings to 100% compliance.",
            "preview_summary": {
                "total_items": preview["total_items"],
                "old_compliant_count": preview["old_compliant_count"],
                "new_compliant_count": preview["new_compliant_count"],
                "items_updated_count": preview["items_updated_count"]
            },
            "master_state": master
        }
