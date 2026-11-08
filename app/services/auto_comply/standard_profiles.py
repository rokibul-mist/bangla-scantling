"""
Auto-Comply Standard Shipbuilding Profile Catalogs.
Contains standard British/European/ISO Rolled Angles (L), Built-up Tees (T), and Flat Bars (FB)
commonly specified in naval architecture and inland shipbuilding yards.
"""

from typing import List, Dict, Any

# Standard Rolled Angles (Equal and Unequal Angles - L profiles)
# hw: web depth (mm), tw: web thk (mm), bf: flange width (mm), tf: flange thk (mm)
STANDARD_ANGLES: List[Dict[str, Any]] = [
    {"label": "L 65×50×5", "profile_type": "L", "web_depth": 65, "web_thk": 5, "flange_width": 50, "flange_thk": 5},
    {"label": "L 75×50×6", "profile_type": "L", "web_depth": 75, "web_thk": 6, "flange_width": 50, "flange_thk": 6},
    {"label": "L 75×65×7", "profile_type": "L", "web_depth": 75, "web_thk": 7, "flange_width": 65, "flange_thk": 7},
    {"label": "L 90×65×7", "profile_type": "L", "web_depth": 90, "web_thk": 7, "flange_width": 65, "flange_thk": 7},
    {"label": "L 100×65×7", "profile_type": "L", "web_depth": 100, "web_thk": 7, "flange_width": 65, "flange_thk": 7},
    {"label": "L 100×75×8", "profile_type": "L", "web_depth": 100, "web_thk": 8, "flange_width": 75, "flange_thk": 8},
    {"label": "L 125×75×8", "profile_type": "L", "web_depth": 125, "web_thk": 8, "flange_width": 75, "flange_thk": 8},
    {"label": "L 125×75×10", "profile_type": "L", "web_depth": 125, "web_thk": 10, "flange_width": 75, "flange_thk": 10},
    {"label": "L 150×90×9", "profile_type": "L", "web_depth": 150, "web_thk": 9, "flange_width": 90, "flange_thk": 9},
    {"label": "L 150×90×10", "profile_type": "L", "web_depth": 150, "web_thk": 10, "flange_width": 90, "flange_thk": 10},
    {"label": "L 150×90×12", "profile_type": "L", "web_depth": 150, "web_thk": 12, "flange_width": 90, "flange_thk": 12},
    {"label": "L 160×100×10", "profile_type": "L", "web_depth": 160, "web_thk": 10, "flange_width": 100, "flange_thk": 10},
    {"label": "L 180×100×10", "profile_type": "L", "web_depth": 180, "web_thk": 10, "flange_width": 100, "flange_thk": 10},
    {"label": "L 200×100×10", "profile_type": "L", "web_depth": 200, "web_thk": 10, "flange_width": 100, "flange_thk": 10},
    {"label": "L 200×100×12", "profile_type": "L", "web_depth": 200, "web_thk": 12, "flange_width": 100, "flange_thk": 12},
    {"label": "L 200×150×12", "profile_type": "L", "web_depth": 200, "web_thk": 12, "flange_width": 150, "flange_thk": 12},
    {"label": "L 250×100×12", "profile_type": "L", "web_depth": 250, "web_thk": 12, "flange_width": 100, "flange_thk": 12},
    {"label": "L 250×150×14", "profile_type": "L", "web_depth": 250, "web_thk": 14, "flange_width": 150, "flange_thk": 14},
]

# Standard Built-up Tees (T profiles - Heavy frames, Floors, Girders, Transverses)
STANDARD_TEES: List[Dict[str, Any]] = [
    {"label": "T 180×90×8/10", "profile_type": "T", "web_depth": 180, "web_thk": 8, "flange_width": 90, "flange_thk": 10},
    {"label": "T 200×100×9/10", "profile_type": "T", "web_depth": 200, "web_thk": 9, "flange_width": 100, "flange_thk": 10},
    {"label": "T 250×100×9/12", "profile_type": "T", "web_depth": 250, "web_thk": 9, "flange_width": 100, "flange_thk": 12},
    {"label": "T 250×125×10/12", "profile_type": "T", "web_depth": 250, "web_thk": 10, "flange_width": 125, "flange_thk": 12},
    {"label": "T 300×125×10/12", "profile_type": "T", "web_depth": 300, "web_thk": 10, "flange_width": 125, "flange_thk": 12},
    {"label": "T 300×150×10/14", "profile_type": "T", "web_depth": 300, "web_thk": 10, "flange_width": 150, "flange_thk": 14},
    {"label": "T 350×150×10/15", "profile_type": "T", "web_depth": 350, "web_thk": 10, "flange_width": 150, "flange_thk": 15},
    {"label": "T 400×150×11/16", "profile_type": "T", "web_depth": 400, "web_thk": 11, "flange_width": 150, "flange_thk": 16},
    {"label": "T 450×150×12/18", "profile_type": "T", "web_depth": 450, "web_thk": 12, "flange_width": 150, "flange_thk": 18},
    {"label": "T 500×180×12/20", "profile_type": "T", "web_depth": 500, "web_thk": 12, "flange_width": 180, "flange_thk": 20},
    {"label": "T 550×200×12/22", "profile_type": "T", "web_depth": 550, "web_thk": 12, "flange_width": 200, "flange_thk": 22},
    {"label": "T 600×200×14/25", "profile_type": "T", "web_depth": 600, "web_thk": 14, "flange_width": 200, "flange_thk": 25},
    {"label": "T 700×250×15/28", "profile_type": "T", "web_depth": 700, "web_thk": 15, "flange_width": 250, "flange_thk": 28},
    {"label": "T 800×300×16/30", "profile_type": "T", "web_depth": 800, "web_thk": 16, "flange_width": 300, "flange_thk": 30},
    {"label": "T 900×300×18/32", "profile_type": "T", "web_depth": 900, "web_thk": 18, "flange_width": 300, "flange_thk": 32},
    {"label": "T 1000×350×20/35", "profile_type": "T", "web_depth": 1000, "web_thk": 20, "flange_width": 350, "flange_thk": 35},
]

# Standard Flat Bars (FB profiles)
STANDARD_FLAT_BARS: List[Dict[str, Any]] = [
    {"label": "FB 75×8", "profile_type": "FB", "web_depth": 75, "web_thk": 8, "flange_width": 0, "flange_thk": 0},
    {"label": "FB 100×8", "profile_type": "FB", "web_depth": 100, "web_thk": 8, "flange_width": 0, "flange_thk": 0},
    {"label": "FB 100×10", "profile_type": "FB", "web_depth": 100, "web_thk": 10, "flange_width": 0, "flange_thk": 0},
    {"label": "FB 125×10", "profile_type": "FB", "web_depth": 125, "web_thk": 10, "flange_width": 0, "flange_thk": 0},
    {"label": "FB 150×10", "profile_type": "FB", "web_depth": 150, "web_thk": 10, "flange_width": 0, "flange_thk": 0},
    {"label": "FB 150×12", "profile_type": "FB", "web_depth": 150, "web_thk": 12, "flange_width": 0, "flange_thk": 0},
    {"label": "FB 180×12", "profile_type": "FB", "web_depth": 180, "web_thk": 12, "flange_width": 0, "flange_thk": 0},
    {"label": "FB 200×12", "profile_type": "FB", "web_depth": 200, "web_thk": 12, "flange_width": 0, "flange_thk": 0},
    {"label": "FB 250×14", "profile_type": "FB", "web_depth": 250, "web_thk": 14, "flange_width": 0, "flange_thk": 0},
]

# Standard Commercial Millimeter Plate Thicknesses
STANDARD_PLATE_THICKNESSES: List[float] = [
    4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 18.0, 20.0, 22.0, 25.0, 28.0, 30.0, 32.0, 35.0, 40.0
]
