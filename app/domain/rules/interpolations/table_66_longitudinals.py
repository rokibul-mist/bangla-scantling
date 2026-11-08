"""
Table 66 & 52: Bottom & Inner Bottom Longitudinals Section Modulus Interpolator.
Statutory Reference: Rules 25 & 105, Tables 66 & 52.
Governing parameters: Frame Spacing s (mm), Vessel Length L (m), and Route Factor kz.
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table66LongitudinalsInterpolator(BaseTableInterpolator):
    table_index = 65  # Table 66
    table_no_str = "Table 66"
    table_title = "Bottom & Inner Bottom Longitudinals Section Modulus"
    ref_rule = "Rules 25 & 105, Tables 66 & 52"
    default_unit = "cm³"

    # Baseline statutory Section Modulus (cm³) at standard 550mm spacing:
    # Outer bottom longitudinal: 145.0 cm³ (scaled by length L / 70.0 for smaller vessels)
    # Inner bottom longitudinal: 125.0 cm³ (scaled by length L / 70.0 for smaller vessels)
    BASE_BOTTOM_LONG_70M = 145.0
    BASE_INNER_BOTTOM_LONG_70M = 125.0

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_bottom_longitudinal") -> InterpolationResult:
        lbp = float(inputs.get('lbp', inputs.get('L', 69.85)) or 69.85)
        spacing = float(inputs.get('frame_spacing', inputs.get('spacing', 550.0)) or 550.0)
        kz = float(inputs.get('effective_kz', inputs.get('kz', 1.25)) or 1.25)

        is_inner = "inner" in member_id.lower()
        base_70m = cls.BASE_INNER_BOTTOM_LONG_70M if is_inner else cls.BASE_BOTTOM_LONG_70M

        # Length scaling factor: (L / 70.0), bounded between 0.40 and 1.00
        l_scale = min(1.0, max(0.40, lbp / 70.0))
        z_base = round(base_70m * l_scale, 2)

        # Spacing correction for spacing != 550 mm
        z_corr, sp_factor = cls.apply_spacing_correction(z_base, spacing, is_sm=True)
        rreq = round(z_corr * kz, 2)

        title = "Inner Bottom Longitudinal" if is_inner else "Bottom Longitudinal"
        derivation = (
            f"Table 66 & 52 ({title}, L={lbp:.2f} m, Spacing={spacing:.0f} mm): "
            f"Base Z={z_base:.1f} cm³"
        )
        if sp_factor > 1.0:
            derivation += f" x Spacing Corr({sp_factor:.3f}) = {z_corr:.1f} cm³"
        derivation += f" x kz({kz:.2f}) = {rreq:.2f} cm³"

        return InterpolationResult(
            baseline=round(z_corr, 2),
            rreq=rreq,
            unit=cls.default_unit,
            table_no="Table 66, Table 52",
            table_title=f"{title} Section Modulus",
            formula_desc="Rule 105, Table 66 & 52 Longitudinal Section Modulus with Spacing Correction",
            inputs_used={"lbp": lbp, "frame_spacing": spacing, "kz": kz, "is_inner": is_inner},
            bounding_nodes={"L": lbp, "base_at_70m": base_70m},
            lambda_ratio=round(l_scale, 4),
            spacing_correction=sp_factor,
            extrapolated=False,
            derivation_text=derivation,
            table_view=None
        )
