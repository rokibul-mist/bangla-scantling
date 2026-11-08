import math
from typing import Dict, Any

def calc_stiffener_section(
    bp: float,
    tp: float,
    hw: float,
    tw: float,
    bf: float,
    tf: float,
    profile_type: str = 'L'
) -> Dict[str, Any]:
    """
    Computes Section Modulus and Moment of Inertia for a stiffener with attached plating.
    bp: Attached plate width (mm) (usually frame spacing)
    tp: Attached plate thickness (mm) (from the plate it is welded to)
    hw: Web depth / height (mm)
    tw: Web thickness (mm)
    bf: Flange width (mm) (0 if flat bar)
    tf: Flange thickness (mm) (0 if flat bar)
    profile_type: 'T', 'L', or 'FB'
    """
    bp = float(bp or 0)
    if bp <= 0:
        bp = 550.0
    tp = float(tp or 0)
    hw = float(hw or 0)
    tw = float(tw or 0)
    bf = float(bf or 0)
    tf = float(tf or 0)
    ptype = (profile_type or ('FB' if bf <= 0 else 'L')).upper()
    is_fb = (ptype == 'FB' or bf <= 0)

    if is_fb:
        bf = 0.0
        tf = 0.0

    ap = bp * tp
    aw = hw * tw
    af = bf * tf if not is_fb else 0.0
    atot = ap + aw + af

    if atot <= 0:
        return {
            'ap': 0.0, 'aw': 0.0, 'af': 0.0, 'atot': 0.0,
            'yna': 0.0, 'ip': 0.0, 'iw': 0.0, 'if': 0.0, 'ina': 0.0,
            'ymax': 0.0, 'z_mm3': 0.0, 'z_cm3': 0.0, 'profile_type': ptype
        }

    # Centroid distance from outer face of plate (mm)
    if is_fb:
        yna = (ap * (tp / 2.0) + aw * (tp + hw / 2.0)) / atot
    else:
        yna = (ap * (tp / 2.0) + aw * (tp + hw / 2.0) + af * (tp + hw + tf / 2.0)) / atot

    # Parallel axis theorem moments of inertia (mm4)
    ip = (bp * (tp**3)) / 12.0 + ap * ((yna - tp / 2.0)**2)
    iw = (tw * (hw**3)) / 12.0 + aw * ((tp + hw / 2.0 - yna)**2)
    iff = (bf * (tf**3)) / 12.0 + af * ((tp + hw + tf / 2.0 - yna)**2) if not is_fb else 0.0

    ina = ip + iw + iff
    total_depth = tp + hw + (0.0 if is_fb else tf)
    ymax = max(yna, total_depth - yna)

    z_mm3 = ina / ymax if ymax > 0 else 0.0
    z_cm3 = z_mm3 / 1000.0

    return {
        'ap': round(ap, 2),
        'aw': round(aw, 2),
        'af': round(af, 2),
        'atot': round(atot, 2),
        'yna': yna,
        'ip': ip,
        'iw': iw,
        'if': iff,
        'ina': ina,
        'ymax': ymax,
        'z_mm3': z_mm3,
        'z_cm3': z_cm3,
        'profile_type': ptype
    }
