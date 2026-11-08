from typing import Dict, Any, List

def calc_plate_weight(l_dim: float, b_dim: float, t: float, density: float = 7850.0, qty: int = 1) -> Dict[str, float]:
    """
    Computes volume (m3), weight (kg), and weight (tonne) for a steel plate.
    Dimensions in mm.
    """
    l_val = float(l_dim or 0)
    b_val = float(b_dim or 0)
    t_val = float(t or 0)
    density_val = float(density or 7850.0)
    qty_val = int(qty or 1)

    vol = (l_val * b_val * t_val) / 1e9
    weight_kg = vol * density_val * qty_val
    weight_tonne = weight_kg / 1000.0

    return {
        'vol': round(vol, 6),
        'weight_kg': round(weight_kg, 2),
        'weight_tonne': round(weight_tonne, 3)
    }

def calc_angle_weight(l_dim: float, b_dim: float, t: float, length: float, density: float = 7850.0, qty: int = 1) -> Dict[str, float]:
    """
    Computes cross-section area (mm2), volume (m3), weight (kg), and weight (tonne) for an angle/profile.
    Dimensions in mm.
    """
    ld = float(l_dim or 0)
    bd = float(b_dim or 0)
    thk = float(t or 0)
    len_mm = float(length or 0)
    density_val = float(density or 7850.0)
    qty_val = int(qty or 1)

    area = (ld + bd) * thk
    vol = (area / 1e6) * (len_mm / 1000.0)
    weight_kg = vol * density_val * qty_val
    weight_tonne = weight_kg / 1000.0

    return {
        'area': round(area, 2),
        'vol': round(vol, 6),
        'weight_kg': round(weight_kg, 2),
        'weight_tonne': round(weight_tonne, 3)
    }

def calc_lightship_allowances(total_steel_t: float) -> Dict[str, float]:
    """
    Calculates statutory outfitting weight breakdown (56% standard total):
    - Margin: 20%
    - Outfit & Deck Equipment: 15%
    - Piping, Valves & Fittings: 10%
    - Electrical & Instrumentation: 3%
    - Accommodation: 1%
    - Miscellaneous: 7%
    Total Lightship = Net Steel * 1.56
    """
    allowance_t = total_steel_t * 0.20
    outfit_t = total_steel_t * 0.15
    piping_t = total_steel_t * 0.10
    electrical_t = total_steel_t * 0.03
    accom_t = total_steel_t * 0.01
    misc_t = total_steel_t * 0.07
    total_lightship_t = total_steel_t + allowance_t + outfit_t + piping_t + electrical_t + accom_t + misc_t

    return {
        'allowance_tonne': round(allowance_t, 3),
        'outfit_tonne': round(outfit_t, 3),
        'piping_tonne': round(piping_t, 3),
        'electrical_tonne': round(electrical_t, 3),
        'accom_tonne': round(accom_t, 3),
        'misc_tonne': round(misc_t, 3),
        'total_lightship_tonne': round(total_lightship_t, 3)
    }
