"""
Statutory Gross & Net Tonnage Calculation Service as per ISO 2001.

Statutory Basis:
- Primary Act: The Inland Shipping Ordinance, 1976 (Ordinance No. 72 of 1976)
- Statutory Rules: The Inland Ships (Tonnage Measurement) Rules, 2001 (S.R.O. No. 308-Law/2001)
  * Rule 10: Definitions of Upper Deck, Moulded Depth, Breadth, Enclosed & Excluded Spaces
  * Rule 11: Gross Tonnage Formula: GT = K1 * V, where K1 = 0.2 + 0.02 * log10(V)
  * Rule 12: Net Tonnage Formula: NT = K2 * Vc * (4d / 3D)^2 + K3 * (N1 + N2/10)
  * Rule 14: Calculation of volume (inner surface of shell plating, appendages included)
  * Rule 15: Measurement & calculation accuracy
  * Appendix 1: Bangladesh Inland Ship Tonnage Measurement Certificate
  * Appendix 3: Table of Coefficients K1 and K2
"""

import math
from typing import Dict, Any, List, Optional


class TonnageService:
    """
    Evaluates Gross Tonnage (GT) and Net Tonnage (NT) strictly compliant with
    Bangladesh Inland Ships (Tonnage Measurement) Rules, 2001 (ISO 2001).
    """

    @classmethod
    def calculate_tonnage(cls, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates GT and NT from vessel dimensions, superstructures, and spaces.
        """
        # 1. Vessel Principal Dimensions
        loa = float(inputs.get("loa", 76.21) or 76.21)
        lbp = float(inputs.get("lbp", 69.85) or (loa * 0.95))
        breadth = float(inputs.get("breadth", 15.24) or 15.24)
        depth = float(inputs.get("depth", 4.87) or 4.87)
        draft = float(inputs.get("draft", 4.0) or 4.0)
        cb = float(inputs.get("block_coeff", 0.721) or 0.721)

        # Underdeck volume coefficient Cv (typically cb or ~0.75-0.80 for inland cargo vessels)
        cv = float(inputs.get("underdeck_coeff", cb) or cb)
        if cv <= 0.3 or cv > 1.0:
            cv = 0.75

        # Custom underdeck volume if specified
        custom_underdeck = inputs.get("v_underdeck_custom")
        if custom_underdeck is not None and float(custom_underdeck) > 0:
            v_underdeck = round(float(custom_underdeck), 2)
        else:
            v_underdeck = round(lbp * breadth * depth * cv, 2)

        # 2. Superstructures and Deckhouses (Rule 10 & Rule 14)
        superstructures = inputs.get("superstructures")
        if not superstructures or not isinstance(superstructures, list):
            # Standard default erections for an inland vessel if none provided
            superstructures = [
                {
                    "name": "Wheelhouse / Nav Bridge",
                    "length": 5.0,
                    "breadth": 4.5,
                    "height": 2.4,
                    "volume": round(5.0 * 4.5 * 2.4, 2),
                    "is_enclosed": True,
                },
                {
                    "name": "Aft Deckhouse (Crew Accommodation)",
                    "length": 14.0,
                    "breadth": 9.0,
                    "height": 2.4,
                    "volume": round(14.0 * 9.0 * 2.4, 2),
                    "is_enclosed": True,
                },
                {
                    "name": "Machinery / Engine Casing",
                    "length": 8.5,
                    "breadth": 4.0,
                    "height": 2.2,
                    "volume": round(8.5 * 4.0 * 2.2, 2),
                    "is_enclosed": True,
                },
                {
                    "name": "Forecastle Erection",
                    "length": 7.5,
                    "breadth": 6.5,
                    "height": 1.8,
                    "volume": round(7.5 * 6.5 * 1.8 * 0.85, 2),
                    "is_enclosed": True,
                },
            ]

        v_superstructures = 0.0
        for s in superstructures:
            vol = float(s.get("volume", 0) or 0)
            if vol <= 0:
                l_s = float(s.get("length", 0) or 0)
                b_s = float(s.get("breadth", 0) or 0)
                h_s = float(s.get("height", 0) or 0)
                vol = round(l_s * b_s * h_s, 2)
                s["volume"] = vol
            if s.get("is_enclosed", True):
                v_superstructures += vol
        v_superstructures = round(v_superstructures, 2)

        # 3. Appendages (Rule 14(2))
        appendages = inputs.get("appendages")
        if not appendages or not isinstance(appendages, list):
            appendages = [
                {"name": "Rudder Blade & Skeg", "volume": 14.5},
                {"name": "Propeller Bossings & Stern Appendages", "volume": 8.0},
            ]
        v_appendages = round(sum(float(a.get("volume", 0) or 0) for a in appendages), 2)

        # 4. Excluded Spaces (Rule 10(5))
        excluded = inputs.get("excluded_spaces")
        if not excluded or not isinstance(excluded, list):
            excluded = []
        v_excluded = round(sum(float(e.get("volume", 0) or 0) for e in excluded), 2)

        # Total Volume of Enclosed Spaces V (Rule 11)
        v_total = round(v_underdeck + v_superstructures + v_appendages - v_excluded, 2)
        if v_total <= 0:
            v_total = 1.0

        # 5. Gross Tonnage Formula: GT = K1 * V (Rule 11)
        # K1 = 0.2 + 0.02 * log10(V)
        k1 = round(0.2 + 0.02 * math.log10(v_total), 4)
        gt = round(k1 * v_total, 2)

        # 6. Net Tonnage Formula (Rule 12)
        # NT = K2 * Vc * (4d / 3D)^2 + K3 * (N1 + N2/10)
        # Total volume of cargo spaces Vc (m³)
        custom_vc = inputs.get("cargo_volume_vc")
        if custom_vc is not None and float(custom_vc) > 0:
            vc = round(float(custom_vc), 2)
        else:
            # For cargo vessel: typically ~68% of underdeck volume
            cargo_pct = float(inputs.get("cargo_percent", 68.0) or 68.0)
            vc = round(v_underdeck * (cargo_pct / 100.0), 2)

        if vc <= 0:
            vc = 1.0

        # K2 = 0.2 + 0.02 * log10(Vc)
        k2 = round(0.2 + 0.02 * math.log10(vc), 4)

        # Draught ratio factor: (4d / 3D)^2 <= 1.0 (Rule 12(1)(a))
        raw_draft_ratio = (4.0 * draft) / (3.0 * depth) if depth > 0 else 1.0
        draft_factor_squared = raw_draft_ratio ** 2
        draft_factor_applied = min(1.0, draft_factor_squared)

        # Main Cargo Term: K2 * Vc * (4d / 3D)^2
        raw_cargo_term = k2 * vc * draft_factor_applied
        # Rule 12(1)(b): term shall never be taken as less than 0.25 GT
        cargo_term_min = 0.25 * gt
        cargo_floor_applied = raw_cargo_term < cargo_term_min
        effective_cargo_term = round(max(raw_cargo_term, cargo_term_min), 2)

        # Passenger Term: K3 * (N1 + N2 / 10)
        n1 = int(inputs.get("passengers_cabin_n1", 0) or 0)
        n2 = int(inputs.get("passengers_other_n2", 0) or 0)
        # Rule 12(1): Where N1 + N2 is less than 13, N1 and N2 shall be taken as zero
        pax_zeroed = (n1 + n2) < 13
        eff_n1 = 0 if pax_zeroed else n1
        eff_n2 = 0 if pax_zeroed else n2

        # K3 = 1.25 * (GT + 10,000) / 10,000
        k3 = round(1.25 * (gt + 10000.0) / 10000.0, 4)
        pax_term = round(k3 * (eff_n1 + eff_n2 / 10.0), 2)

        # Preliminary NT
        nt_preliminary = effective_cargo_term + pax_term

        # Rule 12(1)(c): NT shall never be taken as less than 0.30 GT
        nt_min = 0.30 * gt
        min_floor_applied = nt_preliminary < nt_min
        nt = round(max(nt_preliminary, nt_min), 2)

        # Step by Step derivations for engineering transparency
        step_by_step = [
            {
                "rule": "Rule 10 & 14",
                "title": "Under-Deck Volume (V_underdeck)",
                "formula": "V1 = LBP * B * D * Cv",
                "values": f"{lbp:.2f}m * {breadth:.2f}m * {depth:.2f}m * {cv:.3f}",
                "result": f"{v_underdeck:.2f} m³",
            },
            {
                "rule": "Rule 10 & 14",
                "title": "Enclosed Superstructures & Deckhouses (V_super)",
                "formula": "V2 = sum(L_i * B_i * H_i) for all enclosed erections",
                "values": f"{len(superstructures)} erections evaluated",
                "result": f"{v_superstructures:.2f} m³",
            },
            {
                "rule": "Rule 14(2)",
                "title": "Appendages Volume (V_appendages)",
                "formula": "V3 = sum(V_rudder, V_bossing, ...)",
                "values": f"{len(appendages)} appendages included",
                "result": f"{v_appendages:.2f} m³",
            },
            {
                "rule": "Rule 11",
                "title": "Total Volume of All Enclosed Spaces (V)",
                "formula": "V = V1 + V2 + V3 - V_excluded",
                "values": f"{v_underdeck:.2f} + {v_superstructures:.2f} + {v_appendages:.2f} - {v_excluded:.2f}",
                "result": f"{v_total:.2f} m³",
            },
            {
                "rule": "Rule 11 & Appendix 3",
                "title": "Gross Tonnage Coefficient (K1)",
                "formula": "K1 = 0.2 + 0.02 * log10(V)",
                "values": f"0.2 + 0.02 * log10({v_total:.2f})",
                "result": f"{k1:.4f}",
            },
            {
                "rule": "Rule 11",
                "title": "Statutory Gross Tonnage (GT)",
                "formula": "GT = K1 * V",
                "values": f"{k1:.4f} * {v_total:.2f}",
                "result": f"{gt:.2f}",
            },
            {
                "rule": "Rule 12 & Appendix 3",
                "title": "Cargo Space Volume (Vc) & Factor (K2)",
                "formula": "K2 = 0.2 + 0.02 * log10(Vc)",
                "values": f"Vc = {vc:.2f} m³, 0.2 + 0.02 * log10({vc:.2f})",
                "result": f"K2 = {k2:.4f}",
            },
            {
                "rule": "Rule 12(1)(a)",
                "title": "Draught Factor [(4d / 3D)² <= 1.0]",
                "formula": "(4 * {d:.2f} / (3 * {D:.2f}))² = {raw:.4f} -> capped <= 1.0".format(
                    d=draft, D=depth, raw=draft_factor_squared
                ),
                "values": f"d = {draft:.2f}m, D = {depth:.2f}m",
                "result": f"{draft_factor_applied:.4f}",
            },
            {
                "rule": "Rule 12(1)(b)",
                "title": "Cargo Space Term & 0.25 GT Floor",
                "formula": "max(K2 * Vc * (4d/3D)², 0.25 * GT)",
                "values": f"Raw = {raw_cargo_term:.2f}, 0.25*GT = {cargo_term_min:.2f}",
                "result": f"{effective_cargo_term:.2f} ({'Floor Applied' if cargo_floor_applied else 'Normal'})",
            },
            {
                "rule": "Rule 12(1)",
                "title": "Passenger Factor (K3) & Term",
                "formula": "K3 * (N1 + N2/10) where N1+N2 < 13 is taken as 0",
                "values": f"N1={eff_n1}, N2={eff_n2}, K3={k3:.4f}",
                "result": f"{pax_term:.2f}",
            },
            {
                "rule": "Rule 12(1)(c)",
                "title": "Statutory Net Tonnage (NT) & 0.30 GT Floor",
                "formula": "max(Cargo_Term + Pax_Term, 0.30 * GT)",
                "values": f"Raw = {nt_preliminary:.2f}, 0.30*GT = {nt_min:.2f}",
                "result": f"{nt:.2f} ({'0.30 GT Floor Applied' if min_floor_applied else 'Compliant'})",
            },
        ]

        return {
            "success": True,
            "vessel_name": inputs.get("vessel_name", "M. V. YOUNUS MOLLA-1"),
            "particulars": {
                "loa": loa,
                "lbp": lbp,
                "breadth": breadth,
                "depth": depth,
                "draft": draft,
                "block_coeff": cb,
                "underdeck_coeff": cv,
            },
            "volumes": {
                "v_underdeck": v_underdeck,
                "v_superstructures": v_superstructures,
                "v_appendages": v_appendages,
                "v_excluded": v_excluded,
                "v_total": v_total,
                "v_cargo": vc,
            },
            "superstructures": superstructures,
            "appendages": appendages,
            "excluded_spaces": excluded,
            "coefficients": {
                "k1": k1,
                "k2": k2,
                "k3": k3,
                "draft_factor_squared": round(draft_factor_squared, 4),
                "draft_factor_applied": round(draft_factor_applied, 4),
            },
            "passengers": {
                "n1_declared": n1,
                "n2_declared": n2,
                "n1_effective": eff_n1,
                "n2_effective": eff_n2,
                "pax_zeroed": pax_zeroed,
            },
            "tonnage": {
                "gross_tonnage": gt,
                "net_tonnage": nt,
                "cargo_term": effective_cargo_term,
                "pax_term": pax_term,
                "is_cargo_floor_applied": cargo_floor_applied,
                "is_min_floor_applied": min_floor_applied,
                "gt_formula": f"GT = K1 * V = {k1:.4f} * {v_total:.2f} = {gt:.2f}",
                "nt_formula": f"NT = {effective_cargo_term:.2f} + {pax_term:.2f} = {nt:.2f}",
            },
            "step_by_step": step_by_step,
            "statutory_reference": {
                "book": "Inland Ships (Tonnage Measurement) Rules, 2001 (Book 12)",
                "rules": ["Rule 10", "Rule 11", "Rule 12", "Rule 14", "Rule 15", "Appendix 1", "Appendix 3"],
                "statutory_authority": "Department of Shipping, Government of the People's Republic of Bangladesh",
                "ordinance": "Inland Shipping Ordinance, 1976 (Ordinance No. 72 of 1976)",
            },
        }
