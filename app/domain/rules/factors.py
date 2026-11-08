from typing import Tuple, Dict, Any

def evaluate_statutory_factors(inputs: Dict[str, Any]) -> Tuple[float, float, str]:
    """
    Evaluates statutory factor multiplier according to statutory rules
    (Bangladesh Inland Shipping Rules 2001 / SRO 308 / ISO 1976):
    - Steel (Old): kt = 1.40, kz = 1.40
    - Bay crossing / Coastal: kt = 1.20, kz = 1.25
    - Rough water: kt = 1.10, kz = 1.15
    - Seasonal crossing: kt = 1.15, kz = 1.20
    - Round seasonal: kt = 1.05, kz = 1.10
    - Calm water: kt = 1.00, kz = 1.00
    - Custom mode: user override
    Returns: (kt, kz, rule_desc)
    """
    factor_rule = str(inputs.get('factor_rule', 'auto')).lower()
    route = str(inputs.get('proposed_route', inputs.get('route', 'Inland & bay crossing')))
    r_lower = route.lower()
    
    mat = str(inputs.get('hull_material', '')).lower()
    is_old_steel = 'old' in mat

    if inputs.get('factor_mode') == 'manual' or ('custom_kt' in inputs and 'custom_kz' in inputs) or factor_rule == 'custom':
        kt = float(inputs.get('custom_kt', inputs.get('effective_kt', 1.20)))
        kz = float(inputs.get('custom_kz', inputs.get('effective_kz', 1.25)))
        rule_desc = f"Custom Factor ({kt:.2f} / {kz:.2f})"
    elif is_old_steel:
        kt = 1.40
        kz = 1.40
        rule_desc = "Statutory Rule for Steel (Old): kt=1.40, kz=1.40"
    elif 'bay' in r_lower or 'coastal' in r_lower or 'sro 308' in factor_rule:
        kt = 1.20
        kz = 1.25
        rule_desc = "Rule 4(3) SRO 308 (Bay Crossing: kt=1.20, kz=1.25)"
    elif 'rough' in r_lower:
        kt = 1.10
        kz = 1.15
        rule_desc = "Inland Rough Water Regulation (kt=1.10, kz=1.15)"
    elif 'seasonal crossing' in r_lower:
        kt = 1.15
        kz = 1.20
        rule_desc = "Seasonal Coastal Crossing (kt=1.15, kz=1.20)"
    elif 'round seasonal' in r_lower:
        kt = 1.05
        kz = 1.10
        rule_desc = "Round Seasonal Regulation (kt=1.05, kz=1.10)"
    else:
        # Standard Inland Waterway / Calm Water
        kt = 1.00
        kz = 1.00
        rule_desc = "Rule Baseline - Inland Calm Water (kt=1.00, kz=1.00)"

    return kt, kz, rule_desc
