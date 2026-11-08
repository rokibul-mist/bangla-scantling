import io
import os
import base64
import math
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image as RLImage
)
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from app.domain.catalog.app_form_mappings import get_stiffener_app_form_info


def _register_arial_fonts():
    """
    Registers true Microsoft Arial TrueType fonts from the Windows system directory.
    Falls back gracefully to Helvetica if not running on Windows.
    """
    arial_path = "C:/Windows/Fonts/arial.ttf"
    arial_bold_path = "C:/Windows/Fonts/arialbd.ttf"
    if os.path.exists(arial_path) and "Arial" not in pdfmetrics.getRegisteredFontNames():
        try:
            pdfmetrics.registerFont(TTFont("Arial", arial_path))
        except Exception as e:
            print(f"[PDF Fonts] Could not register Arial: {e}")
    if os.path.exists(arial_bold_path) and "Arial-Bold" not in pdfmetrics.getRegisteredFontNames():
        try:
            pdfmetrics.registerFont(TTFont("Arial-Bold", arial_bold_path))
        except Exception as e:
            print(f"[PDF Fonts] Could not register Arial-Bold: {e}")

_register_arial_fonts()
HAS_ARIAL = "Arial" in pdfmetrics.getRegisteredFontNames()
FONT_REGULAR = "Arial" if HAS_ARIAL else "Helvetica"
FONT_BOLD = "Arial-Bold" if HAS_ARIAL else "Helvetica-Bold"


def resolve_seal_image_bytes(seal_source: Optional[str], default_filename: str) -> Optional[bytes]:
    """
    Resolves raw image bytes from:
    1. Base64 data URI ('data:image/...;base64,...')
    2. Static file path or web path (/static/...)
    3. Fallback to default local file
    """
    if seal_source and isinstance(seal_source, str) and seal_source.strip():
        source = seal_source.strip()
        if source.startswith('data:image') and ';base64,' in source:
            try:
                _, b64_data = source.split(';base64,', 1)
                return base64.b64decode(b64_data)
            except Exception as e:
                print(f"[PDF] Failed to decode base64 seal: {e}")
        else:
            clean_path = source.lstrip('/')
            candidates = [
                source,
                clean_path,
                os.path.join("app", clean_path),
                os.path.join("app", "static", os.path.basename(source)),
                os.path.join("app", "static", "images", os.path.basename(source))
            ]
            for c in candidates:
                if os.path.exists(c) and os.path.isfile(c):
                    try:
                        with open(c, 'rb') as f:
                            return f.read()
                    except Exception:
                        pass

    default_candidates = [
        os.path.join("app", "static", default_filename),
        os.path.join("app", "static", "images", default_filename),
    ]
    for dc in default_candidates:
        if os.path.exists(dc) and os.path.isfile(dc):
            try:
                with open(dc, 'rb') as f:
                    return f.read()
            except Exception:
                pass
    return None


class CleanCanvas(canvas.Canvas):
    """
    Clean canvas with NO running headers, footers, or page numbers.
    Draws the enlarged Designer Seal in the bottom-right corner of ALL pages EXCEPT Page 1.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.designer_seal_bytes: Optional[bytes] = None

    def showPage(self):
        # Draw enlarged Designer Seal in bottom right corner on ALL pages EXCEPT Page 1
        if self._pageNumber > 1 and self.designer_seal_bytes:
            try:
                seal_w = 58.0
                seal_h = 58.0
                x = 595.27 - 36.0 - seal_w
                y = 10.0
                reader = ImageReader(io.BytesIO(self.designer_seal_bytes))
                self.drawImage(reader, x, y, width=seal_w, height=seal_h, mask='auto', preserveAspectRatio=True)
            except Exception as e:
                print(f"[PDF Canvas] Error drawing corner seal: {e}")

        super().showPage()

    def save(self):
        super().save()


def draw_stiffener_vector_figure(
    bp: float, tp: float, hw: float, tw: float, bf: float, tf: float,
    yna: float, name: str, z_cm3: float, ptype: str = 'L',
    width: float = 235, height: float = 180
) -> Drawing:
    """
    Generates a high-precision pure vector cross-section diagram of the stiffener and attached plate.
    Proportioned at height=180 to fill the page cleanly with 3 sheets per page.
    """
    d = Drawing(width, height)
    
    # Outer Border Box
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#334155"), strokeWidth=0.8))

    prof_type = (ptype or 'L').upper().strip()
    is_fb = (prof_type == 'FB' or bf <= 0 or tf <= 0)
    is_t = (prof_type == 'T' and not is_fb)

    eff_bf = 0.0 if is_fb else float(bf)
    eff_tf = 0.0 if is_fb else float(tf)

    if is_fb:
        prof_str = f"FB {int(round(hw))}x{int(round(tw))} mm"
    elif is_t:
        prof_str = f"T {int(round(hw))}x{int(round(eff_bf))}x{int(round(tw))} mm"
    else:
        prof_str = f"L {int(round(hw))}x{int(round(eff_bf))}x{int(round(tw))} mm"

    # Top Title Block inside the box (Using Arial)
    display_title = name.upper()
    if len(display_title) > 32:
        display_title = display_title[:30] + ".."
    d.add(String(8, height - 14, display_title, fontName=FONT_BOLD, fontSize=8.0, fillColor=colors.HexColor("#0F172A")))
    d.add(String(8, height - 25, f"Profile: {prof_str}", fontName=FONT_REGULAR, fontSize=7.0, fillColor=colors.HexColor("#334155")))
    d.add(String(8, height - 36, f"Section Modulus: Z = {z_cm3:.2f} cm³", fontName=FONT_BOLD, fontSize=7.5, fillColor=colors.HexColor("#1D4ED8")))
    d.add(Line(6, height - 40, width - 6, height - 40, strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=0.5))

    # Geometry Scaling (Ample vertical space at height=180)
    base_y = 22.0
    h_avail = height - 72.0
    total_h_mm = tp + hw + eff_tf
    max_w_mm = max(bp * 0.45, eff_bf, 120.0)

    scale_y = h_avail / max(total_h_mm, 1.0)
    scale_x = (width - 50.0) / max(max_w_mm, 1.0)
    scale = min(scale_x, scale_y, 0.80)

    cx = width / 2.0

    # Attached Plate
    p_w = min(bp * 0.35 * scale, width - 36.0)
    p_h = max(tp * scale, 4.0)
    p_x = cx - p_w / 2.0
    p_y = base_y
    d.add(Rect(p_x, p_y, p_w, p_h, fillColor=colors.HexColor("#E2E8F0"), strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.8))
    d.add(String(cx, base_y - 9, f"Pl. {int(round(bp))}x{int(round(tp))} mm", fontName=FONT_BOLD, fontSize=6.5, fillColor=colors.black, textAnchor="middle"))

    # Web
    w_h = hw * scale
    w_w = max(tw * scale, 3.0)
    w_x = cx - w_w / 2.0
    w_y = p_y + p_h
    d.add(Rect(w_x, w_y, w_w, w_h, fillColor=colors.HexColor("#CBD5E1"), strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.8))
    d.add(String(w_x - 3, w_y + w_h / 2.0 - 2, f"{int(round(hw))}x{int(round(tw))}", fontName=FONT_BOLD, fontSize=6.5, fillColor=colors.black, textAnchor="end"))

    # Flange
    if not is_fb and eff_bf > 0:
        f_w = eff_bf * scale
        f_h = max(eff_tf * scale, 3.0)
        f_x = (cx - f_w / 2.0) if is_t else w_x
        f_y = w_y + w_h
        d.add(Rect(f_x, f_y, f_w, f_h, fillColor=colors.HexColor("#CBD5E1"), strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.8))
        d.add(String(f_x + f_w / 2.0, f_y + f_h + 2.5, f"{int(round(eff_bf))}x{int(round(eff_tf))}", fontName=FONT_BOLD, fontSize=6.5, fillColor=colors.black, textAnchor="middle"))

    # Neutral Axis Dashed Line
    na_y = base_y + (yna * scale)
    if base_y <= na_y <= height - 44:
        d.add(Line(10, na_y, width - 10, na_y, strokeColor=colors.HexColor("#DC2626"), strokeWidth=0.7, strokeDashArray=[3, 2]))
        d.add(String(width - 8, na_y - 2.5, "N-A", fontName=FONT_BOLD, fontSize=7.0, fillColor=colors.HexColor("#DC2626"), textAnchor="start"))
        d.add(String(10, na_y + 2.5, f"y_na = {yna:.1f} mm", fontName=FONT_REGULAR, fontSize=6.0, fillColor=colors.HexColor("#DC2626")))

    # Bottom caption
    d.add(Line(0, 11, width, 11, strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=0.5))
    d.add(String(width / 2.0, 3, "TRANSVERSE CROSS-SECTION SCHEMATIC", fontName=FONT_BOLD, fontSize=6.0, fillColor=colors.HexColor("#64748B"), textAnchor="middle"))

    return d


def create_stiffener_sheet_block(
    item: Dict[str, Any], spacing: float, kz: float,
    body_style: ParagraphStyle, mono_style: ParagraphStyle, mono_bold: ParagraphStyle
) -> List[Any]:
    """
    Builds a single stiffener calculation sheet block:
    - Header Bar (Sheet ID, member name, profile, status)
    - Two-column layout: Math derivations (left) and Vector technical drawing (right)
    - Proportioned at height ~200 pt to fill the page cleanly with 3 sheets per A4 page.
    """
    sheet_no = item.get('id', 1)
    name = item.get('name', 'Stiffener')
    table_ref = item.get('table_ref', 'Rule 25')
    ptype = (item.get('profile_type') or 'L').upper()
    is_fb = (ptype == 'FB' or item.get('flange_width', 0) <= 0)

    bp = float(item.get('plate_width', spacing))
    tp = float(item.get('plate_thk', 12.0))
    hw = float(item.get('web_height', 150))
    tw = float(item.get('web_thk', 10))
    bf = float(0.0 if is_fb else item.get('flange_width', 100))
    tf = float(0.0 if is_fb else item.get('flange_thk', 10))

    ap = float(item.get('ap', bp * tp))
    aw = float(item.get('aw', hw * tw))
    af = float(item.get('af', bf * tf if not is_fb else 0.0))
    atot = float(item.get('atot', ap + aw + af))

    yna = float(item.get('yna', 35.0))
    ip = float(item.get('ip', 0.0))
    iw = float(item.get('iw', 0.0))
    iff = float(item.get('if', 0.0))
    ina = float(item.get('ina', 0.0))
    z_mm3 = float(item.get('z_mm3', 0.0))
    z_cm3 = float(item.get('z_cm3', 0.0))
    rreq = float(item.get('rreq', 0.0))
    margin = float(item.get('margin', z_cm3 - rreq))
    is_comp = margin >= 0

    prof_str = f"FB {int(round(hw))}x{int(round(tw))} mm" if is_fb else f"{ptype} {int(round(hw))}x{int(round(bf))}x{int(round(tf))} mm"

    # Resolve Application Form item point
    app_info = get_stiffener_app_form_info(item.get('member_id', ''), name, table_ref)
    app_item_no = app_info.get('item_no', '—')
    app_rule = app_info.get('rule', 'Statutory Rule')
    app_title = app_info.get('title', name)
    app_page = app_info.get('page', '—')

    # Header Bar: Explicit Application Form point in place of status compliance flag
    sheet_header_data = [
        [
            Paragraph(f"<b>SHEET {sheet_no < 10 and '0' or ''}{sheet_no} : {name.upper()} &nbsp;|&nbsp; {prof_str}</b>", 
                      ParagraphStyle('SH1', parent=body_style, fontName=FONT_BOLD, fontSize=8.0, textColor=colors.HexColor('#0F172A'))),
            Paragraph(f"<b>APPLICATION FORM: ITEM {app_item_no} ({app_rule})</b>", 
                      ParagraphStyle('SH2', parent=body_style, fontName=FONT_BOLD, fontSize=7.0, alignment=2, textColor=colors.HexColor('#1E293B')))
        ]
    ]
    sheet_header_table = Table(sheet_header_data, colWidths=[338, 185])
    sheet_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#334155")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))

    # Left Column: Mathematical Derivation Tables (Arial font, comfortable padding)
    left_flowables = []

    # Table 1: Dimensions and Areas
    calc_rows = [
        [
            Paragraph("<b>Item / Element</b>", body_style),
            Paragraph("<b>Width b [mm]</b>", ParagraphStyle('C1', parent=body_style, alignment=2, fontSize=7.0)),
            Paragraph("<b>Thk t [mm]</b>", ParagraphStyle('C2', parent=body_style, alignment=2, fontSize=7.0)),
            Paragraph("<b>Area a [mm²]</b>", ParagraphStyle('C3', parent=body_style, alignment=2, fontSize=7.0))
        ],
        [
            Paragraph("Attached Plate", body_style),
            Paragraph(f"{bp:.1f}", ParagraphStyle('M1', parent=mono_style, alignment=2, fontSize=7.0)),
            Paragraph(f"{tp:.1f}", ParagraphStyle('M2', parent=mono_style, alignment=2, fontSize=7.0)),
            Paragraph(f"{ap:.1f}", ParagraphStyle('M3', parent=mono_style, alignment=2, fontSize=7.0))
        ],
        [
            Paragraph("Stiffener Web", body_style),
            Paragraph(f"{hw:.1f}", ParagraphStyle('M4', parent=mono_style, alignment=2, fontSize=7.0)),
            Paragraph(f"{tw:.1f}", ParagraphStyle('M5', parent=mono_style, alignment=2, fontSize=7.0)),
            Paragraph(f"{aw:.1f}", ParagraphStyle('M6', parent=mono_style, alignment=2, fontSize=7.0))
        ],
        [
            Paragraph("Stiffener Flange" if not is_fb else "Flange (Flat Bar)", body_style),
            Paragraph(f"{bf:.1f}" if not is_fb else "—", ParagraphStyle('M7', parent=mono_style, alignment=2, fontSize=7.0)),
            Paragraph(f"{tf:.1f}" if not is_fb else "—", ParagraphStyle('M8', parent=mono_style, alignment=2, fontSize=7.0)),
            Paragraph(f"{af:.1f}", ParagraphStyle('M9', parent=mono_style, alignment=2, fontSize=7.0))
        ],
        [
            Paragraph("<b>Total Section Area</b>", body_style),
            Paragraph("", body_style),
            Paragraph("", body_style),
            Paragraph(f"<b>{atot:.1f}</b>", ParagraphStyle('MT', parent=mono_bold, alignment=2, fontSize=7.0))
        ]
    ]

    left_tab = Table(calc_rows, colWidths=[108, 58, 48, 65])
    left_tab.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.7, colors.HexColor("#64748B")),
        ('INNERGRID', (0,0), (-1,-1), 0.35, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#F1F5F9")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
    ]))
    left_flowables.append(left_tab)
    left_flowables.append(Spacer(1, 3))

    # Table 2: Neutral Axis & Moments of Inertia
    prop_rows = [
        [Paragraph("<b>Centroid & Moments of Inertia</b>", ParagraphStyle('P1', parent=body_style, fontName=FONT_BOLD, fontSize=7.0)), 
         Paragraph("<b>Value & Unit</b>", ParagraphStyle('P2', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=7.0))],
        [Paragraph("Neutral Axis Height from Plate Base (y_na):", body_style), Paragraph(f"<b>{yna:.3f} mm</b>", ParagraphStyle('MV1', parent=mono_style, alignment=2, fontSize=7.0))],
        [Paragraph("Plate Parallel-Axis Inertia (Ip):", body_style), Paragraph(f"{ip:.2f} mm⁴", ParagraphStyle('MV2', parent=mono_style, alignment=2, fontSize=7.0))],
        [Paragraph("Web Parallel-Axis Inertia (Iw):", body_style), Paragraph(f"{iw:.2f} mm⁴", ParagraphStyle('MV3', parent=mono_style, alignment=2, fontSize=7.0))],
        [Paragraph("Flange Parallel-Axis Inertia (If):", body_style), Paragraph(f"{iff:.2f} mm⁴", ParagraphStyle('MV4', parent=mono_style, alignment=2, fontSize=7.0))],
        [Paragraph("<b>Combined Section Inertia (I_NA):</b>", body_style), Paragraph(f"<b>{ina:.2f} mm⁴</b>", ParagraphStyle('MV5', parent=mono_bold, alignment=2, fontSize=7.0))]
    ]
    prop_tab = Table(prop_rows, colWidths=[175, 104])
    prop_tab.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.7, colors.HexColor("#64748B")),
        ('INNERGRID', (0,0), (-1,-1), 0.35, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
    ]))
    left_flowables.append(prop_tab)
    left_flowables.append(Spacer(1, 3))

    # Table 3: Section Modulus & Application Form Reference (clean, statutory layout)
    z_rows = [
        [
            Paragraph("<b>CALCULATED SECTION MODULUS</b>", ParagraphStyle('Z1', parent=body_style, fontName=FONT_BOLD, fontSize=7.0, textColor=colors.HexColor('#0F172A'))), 
            Paragraph("", body_style)
        ],
        [
            Paragraph("Section Modulus, Z:", body_style), 
            Paragraph(f"<b>{z_cm3:.2f} cm³</b> ({z_mm3:.0f} mm³)", ParagraphStyle('ZV1', parent=mono_bold, alignment=2, fontSize=7.0, textColor=colors.HexColor('#1D4ED8')))
        ],
        [
            Paragraph("Application Form Reference:", body_style), 
            Paragraph(f"<b>Item {app_item_no}: {app_title}</b>", ParagraphStyle('ZV2', parent=body_style, alignment=2, fontSize=6.5, textColor=colors.HexColor('#0F172A')))
        ],
        [
            Paragraph("Statutory Rule & Form Page:", body_style), 
            Paragraph(f"<b>{app_rule} ({table_ref}) &nbsp;|&nbsp; Page {app_page} of 24</b>", ParagraphStyle('ZV3', parent=body_style, alignment=2, fontSize=6.5, textColor=colors.HexColor('#475569')))
        ]
    ]
    z_tab = Table(z_rows, colWidths=[120, 159])
    z_tab.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('BOX', (0,0), (-1,-1), 0.7, colors.HexColor("#64748B")),
        ('INNERGRID', (0,0), (-1,-1), 0.35, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
    ]))
    left_flowables.append(z_tab)

    # Right Column: Pure Vector Technical Cross-Section Figure (Height = 180 pt)
    fig_drawing = draw_stiffener_vector_figure(
        bp=bp, tp=tp, hw=hw, tw=tw, bf=bf, tf=tf,
        yna=yna, name=name, z_cm3=z_cm3, ptype=ptype,
        width=235, height=180
    )

    # Combine Left & Right in Master Two-Column Table
    two_col_table = Table([[left_flowables, fig_drawing]], colWidths=[283, 240])
    two_col_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))

    return [sheet_header_table, Spacer(1, 3), two_col_table]


def generate_detail_calculation_booklet_pdf(state: Dict[str, Any]) -> bytes:
    """
    Main generator for the complete engineering booklet:
    1. Arial TrueType Typography across all elements
    2. Formal Clean Cover Page with Designer & Checker Seals placed in review boxes (NO corner seal on Page 1)
    3. Executive Dashboard (12 Groups, complete tables, KeepTogether - NO break in middle)
    4. Detail Calculation Sheets (Well-proportioned 3 sheets per page filling vertical space, height=180 drawings)
    5. Enlarged 58x58 pt Designer Seal on ALL pages EXCEPT Page 1.
    """
    _register_arial_fonts()

    inputs = state.get('dashboard_inputs', {}) or {}
    results = state.get('sheet2_results', []) or []
    summary_stats = state.get('summary_stats', {}) or {}
    brain_items = state.get('calculation_brain', []) or []

    vessel_name = inputs.get('vessel_name', 'Cargo Vessel')
    vessel_type = inputs.get('vessel_type', 'Steel Body Cargo Vessel')
    hull_type = inputs.get('hull_type', 'Double Bottom')
    route = inputs.get('proposed_route', inputs.get('route', 'Inland & Bay Crossing'))
    plying_time = inputs.get('plying_time', 'Day & Night')

    # Resolve Seal Image Bytes
    designer_seal_bytes = resolve_seal_image_bytes(
        state.get('designer_seal_png'), 
        "designer_seal_default.png"
    )
    checker_seal_bytes = resolve_seal_image_bytes(
        state.get('checker_seal_png'), 
        "checker_seal_default.png"
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=26,
        bottomMargin=26
    )

    # Base Styles (Configured with Arial)
    base_styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=base_styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=18,
        leading=22,
        alignment=1, # Center
        textColor=colors.HexColor("#0F172A")
    )

    sec_header = ParagraphStyle(
        'SecHeader',
        parent=base_styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0F172A")
    )

    sub_style = ParagraphStyle(
        'CoverSubtitle',
        parent=base_styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=8.0,
        leading=10.5,
        textColor=colors.HexColor("#475569")
    )

    body_style = ParagraphStyle(
        'BodyTxt',
        parent=base_styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=7.0,
        leading=9.0,
        textColor=colors.HexColor("#1E293B")
    )

    mono_style = ParagraphStyle(
        'MonoTxt',
        parent=base_styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor("#0F172A")
    )

    mono_bold = ParagraphStyle(
        'MonoBoldTxt',
        parent=base_styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=7.0,
        leading=9.0,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE (Arial Font, Seals in Review Boxes, NO Corner Seal)
    # =========================================================================
    story.append(Spacer(1, 28))
    story.append(Paragraph("DETAIL CALCULATION BOOKLET", title_style))
    story.append(Spacer(1, 22))

    # Particulars Table
    loa = inputs.get('loa', 76.21)
    lbp = inputs.get('lbp', 69.85)
    b_mld = inputs.get('breadth', 13.41)
    d_mld = inputs.get('depth', 5.18)
    draft = inputs.get('draft', 4.00)
    cb = inputs.get('block_coeff', inputs.get('cb', 0.721))
    spacing = inputs.get('frame_spacing', 550.0)
    kt = inputs.get('effective_kt', 1.20)
    kz = inputs.get('effective_kz', 1.25)

    part_data = [
        [
            Paragraph("<b>Vessel Name:</b>", body_style), Paragraph(str(vessel_name), body_style),
            Paragraph("<b>Operating Route:</b>", body_style), Paragraph(str(route), body_style)
        ],
        [
            Paragraph("<b>Vessel Type:</b>", body_style), Paragraph(str(vessel_type), body_style),
            Paragraph("<b>Plying Time:</b>", body_style), Paragraph(str(plying_time), body_style)
        ],
        [
            Paragraph("<b>Hull Construction:</b>", body_style), Paragraph(f"<b>{hull_type}</b>", body_style),
            Paragraph("<b>Statutory Factor kt / kz:</b>", body_style), Paragraph(f"{kt:.2f} / {kz:.2f}", body_style)
        ],
        [
            Paragraph("<b>Length Over All (LOA):</b>", body_style), Paragraph(f"{loa} m", mono_style),
            Paragraph("<b>Breadth Moulded (B):</b>", body_style), Paragraph(f"{b_mld} m", mono_style)
        ],
        [
            Paragraph("<b>Length BP (LBP):</b>", body_style), Paragraph(f"{lbp} m", mono_style),
            Paragraph("<b>Depth Moulded (D):</b>", body_style), Paragraph(f"{d_mld} m", mono_style)
        ],
        [
            Paragraph("<b>Design Draft (d):</b>", body_style), Paragraph(f"{draft} m", mono_style),
            Paragraph("<b>Block Coeff (Cb):</b>", body_style), Paragraph(f"{cb}", mono_style)
        ],
        [
            Paragraph("<b>Transverse Frame Spacing:</b>", body_style), Paragraph(f"{spacing} mm", mono_style),
            Paragraph("", body_style), Paragraph("", body_style)
        ]
    ]

    part_table = Table(part_data, colWidths=[125, 137, 125, 136])
    part_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor("#1E293B")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#F8FAFC")),
        ('SPAN', (1, 6), (3, 6)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(part_table)
    story.append(Spacer(1, 35))

    # Engineering Sign-Off Table with Embedded Seals
    des_cell = []
    if designer_seal_bytes:
        des_img = RLImage(io.BytesIO(designer_seal_bytes), width=105, height=65)
        des_cell = [Spacer(1, 4), des_img, Spacer(1, 4)]
    else:
        des_cell = [Spacer(1, 20), Paragraph("<b>[ OFFICIAL DESIGNER STAMP ]</b>", ParagraphStyle('D1', parent=body_style, alignment=1)), Spacer(1, 20)]

    chk_cell = []
    if checker_seal_bytes:
        chk_img = RLImage(io.BytesIO(checker_seal_bytes), width=105, height=65)
        chk_cell = [Spacer(1, 4), chk_img, Spacer(1, 4)]
    else:
        chk_cell = [Spacer(1, 20), Paragraph("<b>[ OFFICIAL CHECKER STAMP ]</b>", ParagraphStyle('C1', parent=body_style, alignment=1)), Spacer(1, 20)]

    sign_data = [
        [
            Paragraph("<b>PREPARED & DESIGNED BY</b>", ParagraphStyle('S1', parent=body_style, fontName=FONT_BOLD, alignment=1, fontSize=8.5)),
            Paragraph("<b>CHECKED & VERIFIED BY</b>", ParagraphStyle('S2', parent=body_style, fontName=FONT_BOLD, alignment=1, fontSize=8.5))
        ],
        [
            des_cell,
            chk_cell
        ]
    ]

    sign_table = Table(sign_data, colWidths=[261.5, 261.5])
    sign_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#64748B")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,1), (-1,1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(sign_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2+: EXECUTIVE STATUTORY COMPLIANCE DASHBOARD (GROUP-WISE TABLES)
    # Strict Table Integrity: Every group wrapped in KeepTogether (NO break in middle!)
    # =========================================================================
    story.append(Paragraph("EXECUTIVE STATUTORY COMPLIANCE DASHBOARD", sec_header))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"Comprehensive Statutory Scantling Audit organized by 12 Statutory Structural Categories | Construction: <b>{hull_type}</b>", sub_style))
    story.append(Spacer(1, 6))

    # Group brain items by category
    groups_dict = {}
    for b in brain_items:
        clean_g = (b.get('category') or b.get('group') or 'Other').split('(')[0].strip()
        if clean_g not in groups_dict:
            groups_dict[clean_g] = []
        groups_dict[clean_g].append(b)

    for grp_idx, (grp_name, g_items) in enumerate(groups_dict.items()):
        comp_count = len([x for x in g_items if x.get('status') in ['COMPLIANT', 'COMPLIED']])
        is_all_comp = (comp_count == len(g_items))

        # Group Header Bar
        gh_data = [
            [
                Paragraph(f"<b>GROUP {grp_idx + 1}: {grp_name.replace('GROUP ', '').replace(':', '.').upper()}</b> &nbsp;<font color='#64748B'>({len(g_items)} items)</font>", 
                          ParagraphStyle('GH1', parent=body_style, fontName=FONT_BOLD, fontSize=7.5, textColor=colors.HexColor('#0F172A'))),
                Paragraph(f"<b><font color='{'#047857' if is_all_comp else '#D97706'}'>{comp_count} / {len(g_items)} COMPLIED</font></b>", 
                          ParagraphStyle('GH2', parent=body_style, fontName=FONT_BOLD, fontSize=7.0, alignment=2))
            ]
        ]
        gh_table = Table(gh_data, colWidths=[385, 138])
        gh_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
            ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#94A3B8")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 1.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ]))

        # Group Items Table (9 columns matching web dashboard, Arial font)
        rows = [
            [
                Paragraph("<b>No.</b>", ParagraphStyle('H1', parent=body_style, fontName=FONT_BOLD, alignment=1, fontSize=6.0)),
                Paragraph("<b>Scantling Component Description</b>", ParagraphStyle('H2', parent=body_style, fontName=FONT_BOLD, fontSize=6.0)),
                Paragraph("<b>Baseline</b>", ParagraphStyle('H3', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.0)),
                Paragraph("<b>Factor</b>", ParagraphStyle('H4', parent=body_style, fontName=FONT_BOLD, alignment=1, fontSize=6.0)),
                Paragraph("<b>Required</b>", ParagraphStyle('H5', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.0)),
                Paragraph("<b>Provided</b>", ParagraphStyle('H6', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.0)),
                Paragraph("<b>Unit</b>", ParagraphStyle('H7', parent=body_style, fontName=FONT_BOLD, alignment=1, fontSize=6.0)),
                Paragraph("<b>Margin</b>", ParagraphStyle('H8', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.0)),
                Paragraph("<b>Status</b>", ParagraphStyle('H9', parent=body_style, fontName=FONT_BOLD, alignment=1, fontSize=6.0))
            ]
        ]

        for it in g_items:
            no_val = it.get('item', '')
            desc_val = it.get('name') or it.get('desc') or ''
            base_val = it.get('baseline', 0)
            base_str = f"{float(base_val):.2f}" if isinstance(base_val, (int, float)) else str(base_val)
            factor_val = it.get('factor', 1.0)
            fact_str = f"{float(factor_val):.2f}" if isinstance(factor_val, (int, float)) else str(factor_val)
            rreq_val = it.get('rreq', 0)
            rreq_str = f"{float(rreq_val):.2f}" if isinstance(rreq_val, (int, float)) else str(rreq_val)
            dact_val = it.get('dact', 0)
            dact_str = f"{float(dact_val):.2f}" if isinstance(dact_val, (int, float)) else str(dact_val)
            unit_val = it.get('unit', '')
            margin_val = it.get('margin', 0)
            is_c = (float(margin_val) >= 0) if isinstance(margin_val, (int, float)) else (it.get('status') in ['COMPLIANT', 'COMPLIED'])
            marg_str = (f"{'+' if is_c else ''}{float(margin_val):.2f}") if isinstance(margin_val, (int, float)) else str(margin_val)

            rows.append([
                Paragraph(str(no_val), ParagraphStyle('B1', parent=mono_style, alignment=1, fontSize=6.0)),
                Paragraph(desc_val, ParagraphStyle('B2', parent=body_style, fontSize=6.0)),
                Paragraph(base_str, ParagraphStyle('B3', parent=mono_style, alignment=2, fontSize=6.0)),
                Paragraph(fact_str, ParagraphStyle('B4', parent=mono_style, alignment=1, fontSize=6.0)),
                Paragraph(rreq_str, ParagraphStyle('B5', parent=mono_style, alignment=2, fontSize=6.0)),
                Paragraph(f"<b>{dact_str}</b>", ParagraphStyle('B6', parent=mono_bold, alignment=2, fontSize=6.0)),
                Paragraph(unit_val, ParagraphStyle('B7', parent=mono_style, alignment=1, fontSize=5.5)),
                Paragraph(marg_str, ParagraphStyle('B8', parent=mono_style, alignment=2, fontSize=6.0, textColor=colors.HexColor('#047857') if is_c else colors.HexColor('#DC2626'))),
                Paragraph("<font color='#047857'><b>PASS</b></font>" if is_c else "<font color='#DC2626'><b>FAIL</b></font>", ParagraphStyle('B9', parent=body_style, alignment=1, fontSize=6.0))
            ])

        g_table = Table(rows, colWidths=[22, 196, 44, 36, 48, 50, 32, 49, 46])
        g_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor("#E2E8F0")),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 1.2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ]))

        # Enforce Table Integrity: Wrap EVERY group table in KeepTogether so NO table breaks in the middle!
        story.append(KeepTogether([gh_table, g_table]))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # =========================================================================
    # SECTION MODULUS DETAIL CALCULATION SHEETS (3 SHEETS PER PAGE, FILLING PAGE)
    # Proportioned with height=180 drawings and balanced padding to eliminate bottom void!
    # =========================================================================
    for i in range(0, len(results), 3):
        chunk = results[i:i + 3]
        for s_idx, stiff_item in enumerate(chunk):
            sheet_blocks = create_stiffener_sheet_block(stiff_item, spacing, kz, body_style, mono_style, mono_bold)
            story.extend(sheet_blocks)

            if s_idx < len(chunk) - 1:
                story.append(Spacer(1, 6))
                div_tab = Table([['']], colWidths=[523], rowHeights=[0.8])
                div_tab.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#CBD5E1")),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ]))
                story.append(div_tab)
                story.append(Spacer(1, 6))

        story.append(PageBreak())

    # Pass Designer Seal bytes to CleanCanvas for corner stamping on ALL pages EXCEPT Page 1
    def canvas_factory(*args, **kwargs):
        c = CleanCanvas(*args, **kwargs)
        c.designer_seal_bytes = designer_seal_bytes
        return c

    # Build the document
    doc.build(
        story,
        canvasmaker=canvas_factory
    )

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# Alias for backwards compatibility
generate_detail_calculation_pdf = generate_detail_calculation_booklet_pdf
