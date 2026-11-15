"""
Naval Architecture Lines Plan, Hull Geometry & Offset Table Service.
Provides parametric hull generation, file parsing (CSV, TXT, OBJ, STL, DXF),
Simpson's rule hydrostatic integration, and CAD DXF / Excel export.
"""

import io
import math
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import ezdxf

from app.domain.models.lines_plan import (
    ReferenceFrame,
    StationDef,
    WaterlineDef,
    ButtockDef,
    DesignGrid,
    DeckProfilePoint,
    HullHydrostatics,
    OffsetTableData
)


class LinesPlanService:
    """Core service for hull geometry, offset tables, frame of reference, and lines plan."""

    @staticmethod
    def generate_default_grid(
        lbp: float = 69.85,
        beam: float = 13.41,
        depth: float = 5.18,
        draft: float = 4.00,
        num_stations: int = 11,
        num_wls: int = 9,
        num_buttocks: int = 5
    ) -> DesignGrid:
        """Generates standard equidistant design stations, waterlines, and buttocks."""
        stations: List[StationDef] = []
        for i in range(num_stations):
            x = (i / (num_stations - 1)) * lbp
            if i == 0:
                s_id = "AP"
                label = "St. 0 (AP)"
            elif i == num_stations - 1:
                s_id = "FP"
                label = f"St. {i} (FP)"
            else:
                s_id = str(i)
                label = f"St. {i}"
            stations.append(StationDef(id=s_id, index=i, x_pos=round(x, 3), label=label))

        waterlines: List[WaterlineDef] = []
        # Key waterlines: Base (0), intervals up to draft and main deck
        max_wl = depth
        for j in range(num_wls):
            z = (j / (num_wls - 1)) * max_wl
            wl_id = f"WL_{z:.2f}".replace('.', '_')
            label = f"WL {z:.2f} m"
            waterlines.append(WaterlineDef(id=wl_id, z_height=round(z, 3), label=label))

        buttocks: List[ButtockDef] = []
        half_b = beam / 2.0
        for k in range(num_buttocks):
            y = (k / (num_buttocks - 1)) * (half_b * 0.85)
            b_id = f"BUTT_{y:.2f}".replace('.', '_')
            label = f"Buttock {y:.2f} m"
            buttocks.append(ButtockDef(id=b_id, y_offset=round(y, 3), label=label))

        return DesignGrid(
            stations=stations,
            waterlines=waterlines,
            buttocks=buttocks,
            lbp=lbp,
            beam=beam,
            depth=depth,
            draft=draft
        )

    @classmethod
    def generate_parametric_offsets(
        cls,
        lbp: float = 69.85,
        beam: float = 13.41,
        depth: float = 5.18,
        draft: float = 4.00,
        cb: float = 0.75,
        cm: float = 0.98,
        reference_frame: Optional[ReferenceFrame] = None,
        design_grid: Optional[DesignGrid] = None,
        preset_type: str = "general_cargo",
        vessel_name: str = "M. V. YOUNUS MOLLA-1"
    ) -> OffsetTableData:
        """
        Synthesizes a fair, realistic naval architecture hull form based on
        dimension ratios and block coefficient, populating the full Table of Offsets.
        """
        frame = reference_frame or ReferenceFrame()
        grid = design_grid or cls.generate_default_grid(lbp, beam, depth, draft)

        half_beam = beam / 2.0
        half_breadths: Dict[str, Dict[str, float]] = {}
        heights_above_bl: Dict[str, Dict[str, float]] = {}
        deck_profile: List[DeckProfilePoint] = []

        # Bilge radius estimation from midship coefficient Cm:
        # Delta Area = (1 - Cm) * B * d. For circular bilge with angle 90 deg: Area loss = (1 - pi/4)*2*R^2 = (2 - pi/2)*R^2
        # R_bilge = sqrt((1 - Cm) * B * d / (2 - pi/2))
        r_bilge = math.sqrt(max(0.01, (1.0 - min(0.995, cm)) * beam * draft / (2.0 - math.pi / 2.0)))
        r_bilge = min(half_beam * 0.45, max(0.4, r_bilge))

        # Parallel middle body extent based on Cb
        # Higher Cb -> longer parallel middle body
        mid_start = lbp * max(0.20, (1.0 - cb) * 0.8)
        mid_end = lbp * min(0.80, 0.45 + (cb * 0.4))

        for st in grid.stations:
            s_id = st.id
            x = st.x_pos
            half_breadths[s_id] = {}

            # Longitudinal form factor fx in [0, 1]
            if mid_start <= x <= mid_end:
                fx = 1.0
            elif x < mid_start:
                # Aft run (stern)
                xi = x / max(0.001, mid_start)
                fx = 0.15 + 0.85 * (math.sin(xi * math.pi / 2.0) ** 1.35)
                # Stern cut-up at AP
                if x < lbp * 0.05:
                    fx *= 0.5 + 0.5 * (x / (lbp * 0.05))
            else:
                # Forward entrance (bow)
                xi = (lbp - x) / max(0.001, lbp - mid_end)
                fx = 0.98 * (math.sin(xi * math.pi / 2.0) ** 1.15)
                if x >= lbp * 0.98:
                    fx = max(0.02, fx)

            st_max_beam = half_beam * fx

            # Sheer profile calculation: standard parabolic sheer
            # Sheer forward = L/50, Sheer aft = L/100
            xi_mid = (x - (lbp / 2.0)) / (lbp / 2.0)
            if xi_mid > 0:
                sheer = (lbp / 50.0) * (xi_mid ** 2.0)
            else:
                sheer = (lbp / 100.0) * (xi_mid ** 2.0)

            st_deck_h = depth + sheer
            deck_profile.append(DeckProfilePoint(
                station_id=s_id,
                x_pos=round(x, 3),
                deck_height=round(st_deck_h, 3),
                deck_half_breadth=round(st_max_beam, 3),
                sheer_height=round(sheer, 3)
            ))

            # Heights above baseline
            heights_above_bl[s_id] = {
                "keel": 0.0,
                "deck_at_side": round(st_deck_h, 3),
                "deck_at_cl": round(st_deck_h + (frame.deck_camber_mm / 1000.0), 3),
                "knuckle": round(st_deck_h * 0.75, 3) if preset_type == "sand_barge" else 0.0
            }

            # Waterlines half-breadths at this station
            for wl in grid.waterlines:
                w_id = wl.id
                z = wl.z_height

                if z > st_deck_h:
                    # Above deck height
                    hb = 0.0
                elif z <= 0.0:
                    # On baseline: flat of bottom
                    if x < lbp * 0.10:
                        hb = 0.0
                    elif x > lbp * 0.95:
                        hb = 0.0
                    else:
                        flat_bottom_w = max(0.0, st_max_beam - r_bilge)
                        hb = flat_bottom_w
                else:
                    # Vertical height fraction
                    fz = z / depth

                    if preset_type == "sand_barge":
                        # Chined hull form
                        hb = st_max_beam * min(1.0, 0.4 + 0.6 * math.sqrt(fz))
                    else:
                        # Standard rounded bilge naval ship section
                        if z < r_bilge and st_max_beam > r_bilge:
                            # In bilge arc
                            dz = r_bilge - z
                            dy = math.sqrt(max(0.0, r_bilge**2 - dz**2))
                            hb = (st_max_beam - r_bilge) + dy
                        else:
                            # Above bilge arc: slight wall-sided flare up to deck
                            flare = 1.0 + 0.04 * (z / depth)
                            hb = st_max_beam * min(1.04, flare)

                # Ensure bow flare at upper waterlines for forward stations
                if x > lbp * 0.85 and z > draft:
                    flare_boost = ((x - lbp * 0.85) / (lbp * 0.15)) * (z / depth) * (half_beam * 0.25)
                    hb = min(half_beam, hb + flare_boost)

                half_breadths[s_id][w_id] = round(max(0.0, hb), 3)

        table_data = OffsetTableData(
            vessel_name=vessel_name,
            reference_frame=frame,
            design_grid=grid,
            half_breadths=half_breadths,
            heights_above_baseline=heights_above_bl,
            deck_profile=deck_profile,
            preset_type=preset_type
        )

        table_data.hydrostatics = cls.calculate_hydrostatics(table_data)
        return table_data

    @staticmethod
    def _integrate_trapz(y_vals: List[float], x_vals: List[float]) -> float:
        """Composite trapezoidal numerical integration compatible with NumPy 1.x & 2.x."""
        if len(y_vals) < 2 or len(x_vals) < 2 or len(y_vals) != len(x_vals):
            return 0.0
        # Use np.trapezoid (NumPy 2.0+) or np.trapz (NumPy 1.x) or direct manual trapezoid
        if hasattr(np, 'trapezoid'):
            return float(np.trapezoid(y_vals, x_vals))
        elif hasattr(np, 'trapz'):
            return float(np.trapz(y_vals, x_vals))
        else:
            return float(sum((y_vals[i] + y_vals[i+1]) * 0.5 * (x_vals[i+1] - x_vals[i]) for i in range(len(x_vals)-1)))

    @classmethod
    def calculate_hydrostatics(cls, table_data: OffsetTableData) -> HullHydrostatics:
        """
        Calculates hydrostatic particulars by Simpson's 1st Rule integration
        across waterlines and transverse stations.
        """
        grid = table_data.design_grid
        draft = grid.draft
        stations = sorted(grid.stations, key=lambda s: s.x_pos)
        waterlines = sorted([w for w in grid.waterlines if w.z_height <= draft + 0.01], key=lambda w: w.z_height)

        if len(stations) < 3 or len(waterlines) < 2:
            return HullHydrostatics(draft_m=draft)

        # 1. Integrate each waterline along stations to get Waterplane Area Awp(z) and LCF
        awp_list: List[Tuple[float, float, float]] = []  # (z, Awp, LCF)
        for wl in waterlines:
            z = wl.z_height
            w_id = wl.id
            x_vals = [st.x_pos for st in stations]
            y_vals = [table_data.half_breadths.get(st.id, {}).get(w_id, 0.0) for st in stations]

            # Trapezoidal / Simpson composite integration along X for waterplane (full breadth = 2 * y)
            awp = 2.0 * cls._integrate_trapz(y_vals, x_vals)
            # First moment of area about AP for LCF
            moment_x = 2.0 * cls._integrate_trapz([x * y for x, y in zip(x_vals, y_vals)], x_vals)
            lcf = (moment_x / awp) if awp > 0.01 else (grid.lbp / 2.0)
            awp_list.append((z, awp, lcf))

        # 2. Integrate Waterplane Areas vertically along Z up to draft for Volume & LCB
        z_vals = [item[0] for item in awp_list]
        a_vals = [item[1] for item in awp_list]
        m_x_vals = [item[1] * item[2] for item in awp_list]

        volume = cls._integrate_trapz(a_vals, z_vals)
        volume = max(0.1, volume)

        # Displacement in metric tonnes for fresh/brackish water (rho = 1.000 t/m3 standard for inland waterways)
        density = 1.000
        displacement = volume * density

        # Longitudinal Center of Buoyancy LCB from AP
        total_moment_long = cls._integrate_trapz(m_x_vals, z_vals)
        lcb = total_moment_long / volume

        # Transverse Moment of Inertia IT at design waterline for BM_T
        # For the design draft waterline:
        des_wl_idx = min(range(len(z_vals)), key=lambda i: abs(z_vals[i] - draft))
        des_wl_id = waterlines[des_wl_idx].id
        des_y_vals = [table_data.half_breadths.get(st.id, {}).get(des_wl_id, 0.0) for st in stations]
        x_vals = [st.x_pos for st in stations]

        it_transverse = (2.0 / 3.0) * cls._integrate_trapz([y**3 for y in des_y_vals], x_vals)
        bm_t = it_transverse / volume
        # Vertical center of buoyancy KB
        kb = cls._integrate_trapz([z * a for z, a in zip(z_vals, a_vals)], z_vals) / volume
        km_t = kb + bm_t

        design_awp = a_vals[des_wl_idx]
        design_lcf = awp_list[des_wl_idx][2]

        # Hull form coefficients
        lbp = grid.lbp
        beam = grid.beam
        cb = volume / (lbp * beam * draft)
        cwp = design_awp / (lbp * beam)
        # Midship coefficient Cm from station nearest midship
        mid_idx = min(range(len(stations)), key=lambda i: abs(stations[i].x_pos - (lbp / 2.0)))
        mid_st_id = stations[mid_idx].id
        mid_wls = [table_data.half_breadths.get(mid_st_id, {}).get(w[0], 0.0) for w in [(w.id,) for w in waterlines]]
        mid_area = 2.0 * cls._integrate_trapz(mid_wls, z_vals)
        cm = mid_area / (beam * draft)
        cm = max(0.70, min(0.995, cm))
        cp = cb / cm if cm > 0.01 else cb

        # Approximate wetted surface area: Denny-Mumford formula S = L * (1.7*d + Cb*B)
        wetted_surface = lbp * (1.7 * draft + cb * beam)

        return HullHydrostatics(
            draft_m=round(draft, 3),
            volume_m3=round(volume, 2),
            displacement_tonnes=round(displacement, 2),
            waterplane_area_m2=round(design_awp, 2),
            wetted_surface_m2=round(wetted_surface, 2),
            block_coefficient_cb=round(cb, 4),
            prismatic_coefficient_cp=round(cp, 4),
            midship_coefficient_cm=round(cm, 4),
            waterplane_coefficient_cwp=round(cwp, 4),
            lcb_from_ap_m=round(lcb, 3),
            lcb_percent_lbp=round((lcb / lbp) * 100.0, 2),
            lcf_from_ap_m=round(design_lcf, 3),
            kmt_m=round(km_t, 3)
        )

    @classmethod
    def parse_uploaded_file(cls, filename: str, content_bytes: bytes, frame: Optional[ReferenceFrame] = None) -> OffsetTableData:
        """
        Parses an uploaded hull file:
        - .csv, .txt, .dat: Table of Offsets or XYZ points
        - .obj, .stl: 3D mesh slicing
        """
        ext = filename.lower().split('.')[-1]
        frame = frame or ReferenceFrame()

        if ext in ['csv', 'txt', 'dat', 'offsets']:
            return cls._parse_csv_offsets(filename, content_bytes, frame)
        elif ext in ['obj', 'stl']:
            return cls._parse_3d_mesh(filename, content_bytes, frame)
        else:
            raise ValueError(f"Unsupported hull file extension: .{ext}. Supported formats: .csv, .txt, .dat, .obj, .stl")

    @classmethod
    def _parse_csv_offsets(cls, filename: str, content_bytes: bytes, frame: ReferenceFrame) -> OffsetTableData:
        """Parses standard CSV or delimited table of offsets."""
        text = content_bytes.decode('utf-8', errors='ignore')
        lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith('#')]

        if not lines:
            raise ValueError("Uploaded file is empty or contains no readable lines.")

        delimiter = ',' if ',' in lines[0] else ('\t' if '\t' in lines[0] else None)
        header_parts = [p.strip() for p in (lines[0].split(delimiter) if delimiter else lines[0].split())]

        # Check if first row is waterlines header
        # E.g.: Station, WL 0.0, WL 0.5, WL 1.0, ...
        # Or Station, 0.0, 0.5, 1.0, 1.5, ...
        wl_headers = header_parts[1:]
        waterlines: List[WaterlineDef] = []
        for idx, wh in enumerate(wl_headers):
            # Clean numeric value
            clean_str = wh.lower().replace('wl', '').replace('m', '').replace('_', '.').strip()
            try:
                z_val = float(clean_str) * frame.scale
            except ValueError:
                z_val = idx * 0.5
            w_id = f"WL_{z_val:.2f}".replace('.', '_')
            waterlines.append(WaterlineDef(id=w_id, z_height=round(z_val, 3), label=f"WL {z_val:.2f} m"))

        stations: List[StationDef] = []
        half_breadths: Dict[str, Dict[str, float]] = {}
        deck_profile: List[DeckProfilePoint] = []
        heights_above_bl: Dict[str, Dict[str, float]] = {}

        max_b = 0.0
        max_d = 0.0
        row_count = len(lines) - 1

        for r_idx, line in enumerate(lines[1:]):
            parts = [p.strip() for p in (line.split(delimiter) if delimiter else line.split())]
            if not parts:
                continue
            st_label = parts[0]
            st_id = st_label.replace(' ', '_').replace('.', '_')

            # Longitudinal position estimate
            x_pos = (r_idx / max(1, row_count - 1)) * 69.85
            stations.append(StationDef(id=st_id, index=r_idx, x_pos=round(x_pos, 3), label=st_label))
            half_breadths[st_id] = {}

            st_max_y = 0.0
            for w_idx, wl_def in enumerate(waterlines):
                val = 0.0
                if w_idx + 1 < len(parts):
                    try:
                        val = float(parts[w_idx + 1]) * frame.scale
                    except ValueError:
                        val = 0.0
                half_breadths[st_id][wl_def.id] = round(val, 3)
                st_max_y = max(st_max_y, val)
                max_b = max(max_b, val * 2.0)
                max_d = max(max_d, wl_def.z_height)

            deck_profile.append(DeckProfilePoint(
                station_id=st_id,
                x_pos=round(x_pos, 3),
                deck_height=round(max_d, 3),
                deck_half_breadth=round(st_max_y, 3),
                sheer_height=0.0
            ))
            heights_above_bl[st_id] = {
                "keel": 0.0,
                "deck_at_side": round(max_d, 3),
                "deck_at_cl": round(max_d + 0.25, 3),
                "knuckle": 0.0
            }

        grid = DesignGrid(
            stations=stations,
            waterlines=waterlines,
            buttocks=[ButtockDef(id=f"BUTT_{i}", y_offset=round(i * (max_b / 8.0), 3), label=f"Buttock {i}") for i in range(5)],
            lbp=69.85,
            beam=round(max_b if max_b > 1.0 else 13.41, 2),
            depth=round(max_d if max_d > 1.0 else 5.18, 2),
            draft=round(max_d * 0.75 if max_d > 1.0 else 4.0, 2)
        )

        res = OffsetTableData(
            vessel_name=filename.rsplit('.', 1)[0],
            reference_frame=frame,
            design_grid=grid,
            half_breadths=half_breadths,
            heights_above_baseline=heights_above_bl,
            deck_profile=deck_profile,
            source_file=filename
        )
        res.hydrostatics = cls.calculate_hydrostatics(res)
        return res

    @classmethod
    def _parse_3d_mesh(cls, filename: str, content_bytes: bytes, frame: ReferenceFrame) -> OffsetTableData:
        """Slices 3D OBJ or STL mesh into naval architecture design stations and waterlines."""
        import trimesh

        file_obj = io.BytesIO(content_bytes)
        file_type = filename.lower().split('.')[-1]
        mesh = trimesh.load(file_obj, file_type=file_type)

        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate([g for g in mesh.geometry.values() if isinstance(g, trimesh.Trimesh)])

        bounds = mesh.bounds  # [[min_x, min_y, min_z], [max_x, max_y, max_z]]
        min_pt, max_pt = bounds[0], bounds[1]
        len_x = (max_pt[0] - min_pt[0]) * frame.scale
        width_y = (max_pt[1] - min_pt[1]) * frame.scale
        height_z = (max_pt[2] - min_pt[2]) * frame.scale

        lbp = max(5.0, len_x)
        beam = max(2.0, width_y)
        depth = max(1.5, height_z)
        draft = depth * 0.75

        # Build design grid
        grid = cls.generate_default_grid(lbp=lbp, beam=beam, depth=depth, draft=draft)

        # Slice mesh along station planes X = x_i
        half_breadths: Dict[str, Dict[str, float]] = {}
        heights_above_bl: Dict[str, Dict[str, float]] = {}
        deck_profile: List[DeckProfilePoint] = []

        for st in grid.stations:
            s_id = st.id
            x_mesh = min_pt[0] + (st.x_pos / frame.scale)
            half_breadths[s_id] = {}

            # Planar cross section cut at plane normal = [1, 0, 0], origin = [x_mesh, 0, 0]
            try:
                slice_2d = mesh.section(plane_origin=[x_mesh, 0, 0], plane_normal=[1, 0, 0])
            except Exception:
                slice_2d = None

            st_max_y = 0.0
            for wl in grid.waterlines:
                w_id = wl.id
                z_mesh = min_pt[2] + (wl.z_height / frame.scale)

                hb = 0.0
                if slice_2d is not None and len(slice_2d.vertices) > 0:
                    # Find vertices near this waterline height
                    verts = slice_2d.vertices
                    near_wl = [abs(v[1]) for v in verts if abs(v[2] - z_mesh) <= (0.25 / frame.scale)]
                    if near_wl:
                        hb = max(near_wl) * frame.scale
                    else:
                        hb = 0.0

                hb = round(hb, 3)
                half_breadths[s_id][w_id] = hb
                st_max_y = max(st_max_y, hb)

            deck_profile.append(DeckProfilePoint(
                station_id=s_id,
                x_pos=round(st.x_pos, 3),
                deck_height=round(depth, 3),
                deck_half_breadth=round(st_max_y, 3),
                sheer_height=0.0
            ))
            heights_above_bl[s_id] = {
                "keel": 0.0,
                "deck_at_side": round(depth, 3),
                "deck_at_cl": round(depth + 0.25, 3),
                "knuckle": 0.0
            }

        res = OffsetTableData(
            vessel_name=filename.rsplit('.', 1)[0],
            reference_frame=frame,
            design_grid=grid,
            half_breadths=half_breadths,
            heights_above_baseline=heights_above_bl,
            deck_profile=deck_profile,
            source_file=filename
        )
        res.hydrostatics = cls.calculate_hydrostatics(res)
        return res

    @classmethod
    def export_to_dxf(cls, table_data: OffsetTableData) -> bytes:
        """
        Exports production-ready 2D & 3D AutoCAD DXF file with dedicated layers:
        - STATIONS_BODY_PLAN (Cyan)
        - WATERLINES_HALF_BREADTH (Blue)
        - BUTTOCKS_PROFILE (Green)
        - DECK_SHEER_PROFILE (Magenta)
        - GRID_CONSTRUCTION (Grey 8)
        - ANNOTATIONS (White 7)
        """
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()

        # Define CAD layers with standardized colors
        doc.layers.new("STATIONS_BODY_PLAN", dxfattribs={"color": 4})        # Cyan
        doc.layers.new("WATERLINES_HALF_BREADTH", dxfattribs={"color": 5})   # Blue
        doc.layers.new("BUTTOCKS_PROFILE", dxfattribs={"color": 3})          # Green
        doc.layers.new("DECK_SHEER_PROFILE", dxfattribs={"color": 6})        # Magenta
        doc.layers.new("GRID_CONSTRUCTION", dxfattribs={"color": 8})         # Grey
        doc.layers.new("ANNOTATIONS", dxfattribs={"color": 7})               # White

        grid = table_data.design_grid
        stations = sorted(grid.stations, key=lambda s: s.x_pos)
        waterlines = sorted(grid.waterlines, key=lambda w: w.z_height)
        lbp = grid.lbp
        beam = grid.beam
        depth = grid.depth

        # -------------------------------------------------------------
        # VIEW 1: SHEER PLAN / PROFILE VIEW (Offset Origin X=0, Y=0)
        # -------------------------------------------------------------
        msp.add_text("SHEER PLAN / PROFILE ELEVATION", dxfattribs={"layer": "ANNOTATIONS", "height": 0.8}).set_placement((0, depth + 3.0))
        # Baseline and Centerline
        msp.add_line((0, 0), (lbp, 0), dxfattribs={"layer": "GRID_CONSTRUCTION"})
        # Stations Grid Lines in Elevation
        for st in stations:
            msp.add_line((st.x_pos, 0), (st.x_pos, depth + 1.5), dxfattribs={"layer": "GRID_CONSTRUCTION"})
            msp.add_text(st.label, dxfattribs={"layer": "ANNOTATIONS", "height": 0.4}).set_placement((st.x_pos - 0.5, -0.8))
        # Waterlines in Elevation
        for wl in waterlines:
            msp.add_line((0, wl.z_height), (lbp, wl.z_height), dxfattribs={"layer": "GRID_CONSTRUCTION"})
            msp.add_text(f"WL {wl.z_height:.2f}", dxfattribs={"layer": "ANNOTATIONS", "height": 0.35}).set_placement((lbp + 0.5, wl.z_height))

        # Deck Sheer curve
        sheer_pts = [(dp.x_pos, dp.deck_height) for dp in table_data.deck_profile]
        if len(sheer_pts) > 1:
            msp.add_lwpolyline(sheer_pts, dxfattribs={"layer": "DECK_SHEER_PROFILE"})

        # Stem & Stern contours
        if len(sheer_pts) >= 2:
            # Stem line
            msp.add_line(sheer_pts[-1], (lbp, 0), dxfattribs={"layer": "DECK_SHEER_PROFILE"})
            # Stern post
            msp.add_line(sheer_pts[0], (0, 0), dxfattribs={"layer": "DECK_SHEER_PROFILE"})

        # -------------------------------------------------------------
        # VIEW 2: HALF BREADTH PLAN (Offset Y = -beam - 5.0)
        # -------------------------------------------------------------
        y_hb_origin = -beam - 6.0
        msp.add_text("HALF BREADTH / WATERLINES PLAN", dxfattribs={"layer": "ANNOTATIONS", "height": 0.8}).set_placement((0, y_hb_origin + (beam / 2.0) + 2.5))
        # Centerline
        msp.add_line((0, y_hb_origin), (lbp, y_hb_origin), dxfattribs={"layer": "GRID_CONSTRUCTION"})
        # Stations across half-breadth
        for st in stations:
            msp.add_line((st.x_pos, y_hb_origin), (st.x_pos, y_hb_origin + (beam / 2.0) + 0.5), dxfattribs={"layer": "GRID_CONSTRUCTION"})

        # Waterline curves
        for wl in waterlines:
            w_pts = []
            for st in stations:
                hb = table_data.half_breadths.get(st.id, {}).get(wl.id, 0.0)
                w_pts.append((st.x_pos, y_hb_origin + hb))
            if len(w_pts) > 1:
                msp.add_lwpolyline(w_pts, dxfattribs={"layer": "WATERLINES_HALF_BREADTH"})
                msp.add_text(wl.label, dxfattribs={"layer": "ANNOTATIONS", "height": 0.3}).set_placement((lbp + 0.5, y_hb_origin + w_pts[-1][1] - y_hb_origin))

        # -------------------------------------------------------------
        # VIEW 3: BODY PLAN (Offset X = lbp + 15.0, Y = 0)
        # Standard Split: Forebody on Right (+Y), Afterbody on Left (-Y)
        # -------------------------------------------------------------
        x_body_cl = lbp + 15.0 + (beam / 2.0)
        msp.add_text("BODY PLAN (TRANSVERSE SECTIONS)", dxfattribs={"layer": "ANNOTATIONS", "height": 0.8}).set_placement((x_body_cl - (beam / 2.0), depth + 3.0))
        # Centerline & Baseline
        msp.add_line((x_body_cl, 0), (x_body_cl, depth + 2.0), dxfattribs={"layer": "GRID_CONSTRUCTION"})
        msp.add_line((x_body_cl - (beam / 2.0) - 1.0, 0), (x_body_cl + (beam / 2.0) + 1.0, 0), dxfattribs={"layer": "GRID_CONSTRUCTION"})

        mid_x = lbp / 2.0
        for st in stations:
            is_fore = st.x_pos >= mid_x
            sign = 1.0 if is_fore else -1.0
            st_pts = []
            # Start at keel (0, 0)
            st_pts.append((x_body_cl, 0.0))
            for wl in waterlines:
                hb = table_data.half_breadths.get(st.id, {}).get(wl.id, 0.0)
                if hb > 0.001 or wl.z_height == 0.0:
                    st_pts.append((x_body_cl + sign * hb, wl.z_height))

            if len(st_pts) > 1:
                msp.add_lwpolyline(st_pts, dxfattribs={"layer": "STATIONS_BODY_PLAN"})
                # Label at deck top
                top_pt = st_pts[-1]
                msp.add_text(st.id, dxfattribs={"layer": "ANNOTATIONS", "height": 0.35}).set_placement((top_pt[0] - 0.2, top_pt[1] + 0.2))

        # Save to memory buffer
        stream = io.StringIO()
        doc.write(stream)
        return stream.getvalue().encode('utf-8')

    @classmethod
    def export_to_excel(cls, table_data: OffsetTableData) -> bytes:
        """Generates formatted Table of Offsets Excel workbook with live formulas."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Table of Offsets"

        # Theme styling (Professional Light Navy / Slate)
        navy_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        title_font = Font(name="Arial", size=14, bold=True, color="FFFFFF")
        sub_font = Font(name="Arial", size=10, italic=True, color="E2E8F0")
        hdr_font = Font(name="Arial", size=10, bold=True, color="0F172A")
        cell_font = Font(name="Consolas", size=9.5, color="1E293B")
        bold_cell_font = Font(name="Consolas", size=9.5, bold=True, color="0F172A")

        thin_side = Side(border_style="thin", color="CBD5E1")
        border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

        # Title Block
        ws.merge_cells("A1:M1")
        ws["A1"] = f"{table_data.vessel_name.upper()} — STATUTORY TABLE OF OFFSETS"
        ws["A1"].font = title_font
        ws["A1"].fill = navy_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 28

        ws.merge_cells("A2:M2")
        p = table_data.design_grid
        ws["A2"] = (
            f"Particulars: LBP = {p.lbp:.2f} m | Beam (mld) = {p.beam:.2f} m | Depth = {p.depth:.2f} m | "
            f"Draft = {p.draft:.2f} m | Frame of Reference: Origin at {table_data.reference_frame.origin_longitudinal}, "
            f"Baseline at {table_data.reference_frame.baseline} (Molded)"
        )
        ws["A2"].font = sub_font
        ws["A2"].fill = navy_fill
        ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[2].height = 18

        # SECTION 1: HALF BREADTHS TABLE
        ws["A4"] = "1. HALF BREADTHS FROM CENTERLINE (METERS)"
        ws["A4"].font = Font(name="Arial", size=11, bold=True, color="1E3A8A")
        ws.row_dimensions[4].height = 20

        # Header Row
        stations = sorted(table_data.design_grid.stations, key=lambda s: s.x_pos)
        waterlines = sorted(table_data.design_grid.waterlines, key=lambda w: w.z_height)

        headers = ["Waterline (Z)"] + [st.label for st in stations]
        for col_idx, h_text in enumerate(headers, start=1):
            cell = ws.cell(row=5, column=col_idx, value=h_text)
            cell.font = hdr_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
        ws.row_dimensions[5].height = 22

        current_row = 6
        for wl in waterlines:
            # First column: WL label
            c0 = ws.cell(row=current_row, column=1, value=f"{wl.label} (Z={wl.z_height:.2f}m)")
            c0.font = bold_cell_font
            c0.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
            c0.border = border
            c0.alignment = Alignment(horizontal="left", vertical="center")

            for col_idx, st in enumerate(stations, start=2):
                hb = table_data.half_breadths.get(st.id, {}).get(wl.id, 0.0)
                cell = ws.cell(row=current_row, column=col_idx, value=hb)
                cell.font = cell_font
                cell.number_format = "0.000"
                cell.border = border
                cell.alignment = Alignment(horizontal="right", vertical="center")
            current_row += 1

        # SECTION 2: HEIGHTS ABOVE BASELINE TABLE
        current_row += 2
        ws.cell(row=current_row, column=1, value="2. HEIGHTS ABOVE BASELINE & DECK CONTOURS (METERS)").font = Font(name="Arial", size=11, bold=True, color="1E3A8A")
        current_row += 1

        sec2_headers = ["Profile Feature"] + [st.label for st in stations]
        for col_idx, h_text in enumerate(sec2_headers, start=1):
            cell = ws.cell(row=current_row, column=col_idx, value=h_text)
            cell.font = hdr_font
            cell.fill = header_fill
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")
        current_row += 1

        features = [
            ("Deck at Side (Molded Depth + Sheer)", lambda st: next((dp.deck_height for dp in table_data.deck_profile if dp.station_id == st.id), 0.0)),
            ("Deck Half-Breadth at Side", lambda st: next((dp.deck_half_breadth for dp in table_data.deck_profile if dp.station_id == st.id), 0.0)),
            ("Deck at Centerline (with Camber)", lambda st: table_data.heights_above_baseline.get(st.id, {}).get("deck_at_cl", 0.0)),
            ("Keel Bottom Line", lambda st: 0.0)
        ]

        for feat_name, feat_fn in features:
            c0 = ws.cell(row=current_row, column=1, value=feat_name)
            c0.font = bold_cell_font
            c0.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
            c0.border = border
            for col_idx, st in enumerate(stations, start=2):
                val = feat_fn(st)
                cell = ws.cell(row=current_row, column=col_idx, value=val)
                cell.font = cell_font
                cell.number_format = "0.000"
                cell.border = border
                cell.alignment = Alignment(horizontal="right", vertical="center")
            current_row += 1

        # SECTION 3: HYDROSTATICS PARTICULARS
        current_row += 2
        ws.cell(row=current_row, column=1, value="3. FORM COEFFICIENTS & HYDROSTATIC PARTICULARS").font = Font(name="Arial", size=11, bold=True, color="1E3A8A")
        current_row += 1

        h = table_data.hydrostatics or HullHydrostatics()
        hydro_rows = [
            ("Molded Loaded Draft (d)", f"{h.draft_m:.3f} m", "Block Coefficient (Cb)", f"{h.block_coefficient_cb:.4f}"),
            ("Immersed Volume (nabla)", f"{h.volume_m3:.2f} m3", "Midship Section Coefficient (Cm)", f"{h.midship_coefficient_cm:.4f}"),
            ("Displacement (Fresh Water)", f"{h.displacement_tonnes:.2f} Tonnes", "Prismatic Coefficient (Cp)", f"{h.prismatic_coefficient_cp:.4f}"),
            ("Waterplane Area (Awp)", f"{h.waterplane_area_m2:.2f} m2", "Waterplane Area Coefficient (Cwp)", f"{h.waterplane_coefficient_cwp:.4f}"),
            ("Longitudinal Center of Buoyancy (LCB)", f"{h.lcb_from_ap_m:.2f} m from AP ({h.lcb_percent_lbp:.2f}% LBP)", "Transverse KM (KM_T)", f"{h.kmt_m:.2f} m"),
            ("Longitudinal Center of Floatation (LCF)", f"{h.lcf_from_ap_m:.2f} m from AP", "Wetted Surface Area (S)", f"{h.wetted_surface_m2:.2f} m2")
        ]

        for r in hydro_rows:
            ws.cell(row=current_row, column=1, value=r[0]).font = bold_cell_font
            ws.cell(row=current_row, column=2, value=r[1]).font = cell_font
            ws.cell(row=current_row, column=4, value=r[2]).font = bold_cell_font
            ws.cell(row=current_row, column=5, value=r[3]).font = cell_font
            for c_i in [1, 2, 4, 5]:
                ws.cell(row=current_row, column=c_i).border = border
            current_row += 1

        # Auto-fit column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(11, min(32, max_len + 3))

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()
