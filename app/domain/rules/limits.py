from typing import Tuple, Dict, Any

def evaluate_frame_spacing_limit(lbp: float, spacing: float) -> Tuple[float, bool, float]:
    """
    Computes statutory maximum transverse frame spacing limit:
    s_max = 450 + 2 * Lbp (mm)
    Returns: (req_limit, is_compliant, margin)
    """
    max_s = 450.0 + 2.0 * float(lbp)
    req_limit = round(max_s, 2)
    margin = round(max_s - float(spacing), 2)
    is_compliant = float(spacing) <= max_s
    return req_limit, is_compliant, margin

def evaluate_collision_bulkhead_limit(lbp: float, actual_pos: float) -> Tuple[float, float, bool, float]:
    """
    Computes statutory collision bulkhead position limits:
    min_pos = 0.05 * Lbp
    max_pos = 0.08 * Lbp
    Returns: (min_pos, max_pos, is_compliant, margin)
    """
    min_pos = round(0.05 * float(lbp), 2)
    max_pos = round(0.08 * float(lbp), 2)
    act = float(actual_pos)
    is_compliant = (act >= min_pos) and (act <= max_pos)
    margin = round(act - min_pos, 2)
    return min_pos, max_pos, is_compliant, margin
