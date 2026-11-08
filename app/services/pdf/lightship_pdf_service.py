import os
import io
from typing import Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether,
    Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from app.services.pdf.detail_calc_pdf_service import (
    FONT_REGULAR, FONT_BOLD, resolve_seal_image_bytes
)

class LightshipCleanCanvas(canvas.Canvas):
    """
    Clean canvas for Lightship calculation booklet.
    Draws the 2X enlarged Designer Seal (116x116 pt) in the bottom-right corner of Page 2.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.designer_seal_bytes: Optional[bytes] = None

    def showPage(self):
        # Draw 2X enlarged Designer Seal on Page 2 (all pages except Cover Page 1)
        if self._pageNumber > 1 and self.designer_seal_bytes:
            try:
                seal_w = 116.0  # 2X enlarged (was 58.0 pt)
                seal_h = 116.0  # 2X enlarged (was 58.0 pt)
                x = 595.27 - 26.0 - seal_w  # Right aligned to 26 pt page margin
                y = 12.0                     # Positioned cleanly in bottom margin
                reader = ImageReader(io.BytesIO(self.designer_seal_bytes))
                self.drawImage(reader, x, y, width=seal_w, height=seal_h, mask='auto', preserveAspectRatio=True)
            except Exception as e:
                print(f"[Lightship PDF Canvas] Error drawing 2X corner seal: {e}")

        super().showPage()

    def save(self):
        super().save()

def generate_lightship_booklet_pdf(state: Dict[str, Any]) -> bytes:
    """
    Generates the official Lightship Weight Estimation Engineering Booklet PDF:
    - Page 1: Cover Page with vessel particulars and review stamps (NO signature/date lines)
    - Page 2: Complete Calculation Page (Table 1 Plating + Table 2 Stiffeners + Table 3 56% Synthesis)
              All fitted onto ONE single page!
    - Corner Designer Seal (116x116 pt, 2X enlarged) on Page 2
    """
    inputs = state.get('dashboard_inputs', {}) or {}
    plates = state.get('lightship_plates', []) or []
    angles = state.get('lightship_angles', []) or []
    ls = state.get('lightship_summary', {}) or {}

    vessel_name = inputs.get('vessel_name', 'M.V. Cargo Vessel')
    vessel_type = inputs.get('vessel_type', 'Steel Body Cargo Vessel')
    hull_type = inputs.get('hull_type', 'Double Bottom')
    route = inputs.get('proposed_route', inputs.get('route', 'Inland & Bay Crossing'))
    plying_time = inputs.get('plying_time', 'Day & Night')

    loa = float(inputs.get('loa', 76.21) or 76.21)
    lbp = float(inputs.get('lbp', 69.85) or 69.85)
    b_mld = float(inputs.get('breadth', 13.41) or 13.41)
    d_mld = float(inputs.get('depth', 5.18) or 5.18)
    draft = float(inputs.get('draft', 4.00) or 4.00)
    cb = float(inputs.get('block_coeff', inputs.get('cb', 0.721)) or 0.721)
    spacing = float(inputs.get('frame_spacing', 550.0) or 550.0)
    kt = float(inputs.get('effective_kt', 1.20) or 1.20)
    kz = float(inputs.get('effective_kz', 1.25) or 1.25)

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
    # Tight top/bottom margins (18 pt) to ensure all calculations fit on Page 2
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=26,
        rightMargin=26,
        topMargin=18,
        bottomMargin=18
    )

    # Base Styles
    base_styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=base_styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        'CoverSubTitle',
        parent=base_styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0284C7"),
        alignment=1
    )

    sec_header = ParagraphStyle(
        'SecHeader',
        parent=base_styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9.0,
        leading=11.0,
        textColor=colors.HexColor("#0F172A")
    )

    sub_style = ParagraphStyle(
        'SecSub',
        parent=base_styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=6.2,
        leading=7.8,
        textColor=colors.HexColor("#475569")
    )

    body_style = ParagraphStyle(
        'BodyTxt',
        parent=base_styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=5.2,
        leading=6.5,
        textColor=colors.HexColor("#1E293B")
    )

    mono_style = ParagraphStyle(
        'MonoTxt',
        parent=base_styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=5.0,
        leading=6.2,
        textColor=colors.HexColor("#0F172A")
    )

    mono_bold = ParagraphStyle(
        'MonoBoldTxt',
        parent=base_styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=5.2,
        leading=6.5,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE (Identical Aesthetic, NO Signature/Date Lines)
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("LIGHTSHIP WEIGHT ESTIMATION BOOKLET", title_style))
    story.append(Spacer(1, 30))

    # Particulars Table
    part_data = [
        [
            Paragraph("<b>Vessel Name:</b>", ParagraphStyle('P1', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(str(vessel_name), ParagraphStyle('P2', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph("<b>Operating Route:</b>", ParagraphStyle('P3', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(str(route), ParagraphStyle('P4', parent=body_style, fontSize=7.0, leading=9.0))
        ],
        [
            Paragraph("<b>Vessel Type:</b>", ParagraphStyle('P5', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(str(vessel_type), ParagraphStyle('P6', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph("<b>Plying Time:</b>", ParagraphStyle('P7', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(str(plying_time), ParagraphStyle('P8', parent=body_style, fontSize=7.0, leading=9.0))
        ],
        [
            Paragraph("<b>Hull Construction:</b>", ParagraphStyle('P9', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(f"<b>{hull_type}</b>", ParagraphStyle('P10', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph("<b>Statutory Factor kt / kz:</b>", ParagraphStyle('P11', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(f"{kt:.2f} / {kz:.2f}", ParagraphStyle('P12', parent=body_style, fontSize=7.0, leading=9.0))
        ],
        [
            Paragraph("<b>Length Over All (LOA):</b>", ParagraphStyle('P13', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(f"{loa:.2f} m", ParagraphStyle('P14', parent=mono_style, fontSize=7.0, leading=9.0)),
            Paragraph("<b>Breadth Moulded (B):</b>", ParagraphStyle('P15', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(f"{b_mld:.2f} m", ParagraphStyle('P16', parent=mono_style, fontSize=7.0, leading=9.0))
        ],
        [
            Paragraph("<b>Length BP (LBP):</b>", ParagraphStyle('P17', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(f"{lbp:.2f} m", ParagraphStyle('P18', parent=mono_style, fontSize=7.0, leading=9.0)),
            Paragraph("<b>Depth Moulded (D):</b>", ParagraphStyle('P19', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(f"{d_mld:.2f} m", ParagraphStyle('P20', parent=mono_style, fontSize=7.0, leading=9.0))
        ],
        [
            Paragraph("<b>Design Draft (d):</b>", ParagraphStyle('P21', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(f"{draft:.2f} m", ParagraphStyle('P22', parent=mono_style, fontSize=7.0, leading=9.0)),
            Paragraph("<b>Block Coeff (Cb):</b>", ParagraphStyle('P23', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(f"{cb:.3f}", ParagraphStyle('P24', parent=mono_style, fontSize=7.0, leading=9.0))
        ],
        [
            Paragraph("<b>Transverse Frame Spacing:</b>", ParagraphStyle('P25', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph(f"{spacing:.0f} mm", ParagraphStyle('P26', parent=mono_style, fontSize=7.0, leading=9.0)),
            Paragraph("<b>Structural Steel Density:</b>", ParagraphStyle('P27', parent=body_style, fontSize=7.0, leading=9.0)),
            Paragraph("7,850 kg/m³", ParagraphStyle('P28', parent=mono_style, fontSize=7.0, leading=9.0))
        ]
    ]

    part_table = Table(part_data, colWidths=[132, 140, 132, 139])
    part_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor("#1E293B")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#F8FAFC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(part_table)
    story.append(Spacer(1, 45))

    # Engineering Sign-Off Table with Embedded Seals (NO signature or date lines!)
    des_cell = []
    if designer_seal_bytes:
        des_img = RLImage(io.BytesIO(designer_seal_bytes), width=115, height=72)
        des_cell = [Spacer(1, 4), des_img, Spacer(1, 4)]
    else:
        des_cell = [Spacer(1, 25), Paragraph("<b>[ OFFICIAL DESIGNER STAMP ]</b>", ParagraphStyle('D1', parent=body_style, alignment=1, fontSize=8.0)), Spacer(1, 25)]

    chk_cell = []
    if checker_seal_bytes:
        chk_img = RLImage(io.BytesIO(checker_seal_bytes), width=115, height=72)
        chk_cell = [Spacer(1, 4), chk_img, Spacer(1, 4)]
    else:
        chk_cell = [Spacer(1, 25), Paragraph("<b>[ OFFICIAL CHECKER STAMP ]</b>", ParagraphStyle('D2', parent=body_style, alignment=1, fontSize=8.0)), Spacer(1, 25)]

    # Clean review box without the crossed-out Signature / Date lines
    sign_data = [
        [
            Paragraph("<b>NAVAL ARCHITECTURE DESIGNER</b>", ParagraphStyle('S1', parent=body_style, alignment=1, fontName=FONT_BOLD, fontSize=8.0)),
            Paragraph("<b>INSPECTION &amp; APPROVAL AUTHORITY</b>", ParagraphStyle('S2', parent=body_style, alignment=1, fontName=FONT_BOLD, fontSize=8.0))
        ],
        [des_cell, chk_cell]
    ]

    sign_table = Table(sign_data, colWidths=[271, 272])
    sign_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#64748B")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('ALIGN', (0,1), (-1,1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(sign_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: COMPLETE CALCULATION PAGE (Table 1 + Table 2 + Table 3 in 1 Page)
    # =========================================================================
    # 1. STEEL PLATING TABLE
    story.append(Paragraph("1. STEEL PLATING WEIGHT ESTIMATION", sec_header))
    story.append(Spacer(1, 1))
    story.append(Paragraph("Scantlings Plating Volume and Weight Evaluation | Mild Steel Density: <b>7,850 kg/m³</b>", sub_style))
    story.append(Spacer(1, 3))

    plate_cols = [24, 169, 45, 42, 30, 48, 38, 26, 45, 45]
    plate_rows = [
        [
            Paragraph("<b>S/N</b>", ParagraphStyle('PH1', parent=body_style, fontName=FONT_BOLD, alignment=1, fontSize=6.2)),
            Paragraph("<b>ELEMENT (Clean Plate Name)</b>", ParagraphStyle('PH2', parent=body_style, fontName=FONT_BOLD, fontSize=6.2)),
            Paragraph("<b>L (mm)</b>", ParagraphStyle('PH3', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.2)),
            Paragraph("<b>B (mm)</b>", ParagraphStyle('PH4', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.2)),
            Paragraph("<b>t (mm)</b>", ParagraphStyle('PH5', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.2)),
            Paragraph("<b>Vol (m³)</b>", ParagraphStyle('PH6', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.2)),
            Paragraph("<b>Density</b>", ParagraphStyle('PH7', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.2)),
            Paragraph("<b>Qty</b>", ParagraphStyle('PH8', parent=body_style, fontName=FONT_BOLD, alignment=1, fontSize=6.2)),
            Paragraph("<b>Weight (kg)</b>", ParagraphStyle('PH9', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.2)),
            Paragraph("<b>Weight (t)</b>", ParagraphStyle('PH10', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.2)),
        ]
    ]

    for p in plates:
        clean_name = p.get('name', '').split('(')[0].strip() if '(' in p.get('name', '') and not p.get('name', '').startswith('Superstructure') else p.get('name', '')
        vol_str = f"{float(p.get('vol', 0)):.4f}"
        kg_str = f"{float(p.get('weight_kg', 0)):,.0f}"
        t_str = f"{float(p.get('weight_tonne', 0)):.3f}"

        plate_rows.append([
            Paragraph(str(p.get('sn', '')), ParagraphStyle('PD1', parent=mono_style, alignment=1, fontSize=5.8)),
            Paragraph(clean_name, ParagraphStyle('PD2', parent=body_style, fontSize=5.8)),
            Paragraph(f"{float(p.get('l', p.get('l_dim', 0))):,.0f}", ParagraphStyle('PD3', parent=mono_style, alignment=2, fontSize=5.8)),
            Paragraph(f"{float(p.get('b', p.get('b_dim', 0))):,.0f}", ParagraphStyle('PD4', parent=mono_style, alignment=2, fontSize=5.8)),
            Paragraph(f"<b>{float(p.get('t', 0)):.1f}</b>", ParagraphStyle('PD5', parent=mono_bold, alignment=2, fontSize=5.8, textColor=colors.HexColor('#1D4ED8'))),
            Paragraph(vol_str, ParagraphStyle('PD6', parent=mono_style, alignment=2, fontSize=5.4)),
            Paragraph(str(p.get('density', 7850)), ParagraphStyle('PD7', parent=mono_style, alignment=2, fontSize=5.4)),
            Paragraph(str(p.get('qty', 1)), ParagraphStyle('PD8', parent=mono_style, alignment=1, fontSize=5.8)),
            Paragraph(kg_str, ParagraphStyle('PD9', parent=mono_style, alignment=2, fontSize=5.8)),
            Paragraph(f"<b>{t_str}</b>", ParagraphStyle('PD10', parent=mono_bold, alignment=2, fontSize=5.8)),
        ])

    tot_p_kg = float(ls.get('total_plate_tonne', 0)) * 1000.0
    tot_p_t = float(ls.get('total_plate_tonne', 0))

    plate_rows.append([
        Paragraph("", body_style),
        Paragraph("<b>TOTAL STEEL PLATING WEIGHT:</b>", ParagraphStyle('PT1', parent=body_style, fontName=FONT_BOLD, fontSize=6.5)),
        Paragraph("", body_style), Paragraph("", body_style), Paragraph("", body_style), Paragraph("", body_style), Paragraph("", body_style), Paragraph("", body_style),
        Paragraph(f"<b>{tot_p_kg:,.0f} kg</b>", ParagraphStyle('PT2', parent=mono_bold, alignment=2, fontSize=6.5)),
        Paragraph(f"<b>{tot_p_t:.3f} t</b>", ParagraphStyle('PT3', parent=mono_bold, alignment=2, fontSize=6.5, textColor=colors.HexColor('#1D4ED8'))),
    ])

    pt_table = Table(plate_rows, colWidths=plate_cols)
    pt_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")),
        ('INNERGRID', (0,0), (-1,-2), 0.25, colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
        ('LINEABOVE', (0,-1), (-1,-1), 0.6, colors.HexColor("#475569")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 1.5),
        ('RIGHTPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.4),
    ]))
    story.append(pt_table)
    story.append(Spacer(1, 8))

    # 2. STEEL STIFFENERS TABLE
    story.append(Paragraph("2. STEEL STIFFENERS &amp; STRUCTURAL ANGLES WEIGHT ESTIMATION", sec_header))
    story.append(Spacer(1, 1))
    story.append(Paragraph("Stiffener Scantlings Geometry &amp; Unsupported Span Evaluation (Length linked to attached plate)", sub_style))
    story.append(Spacer(1, 3))

    angle_cols = [24, 158, 32, 32, 26, 42, 40, 42, 30, 24, 40, 40]
    angle_rows = [
        [
            Paragraph("<b>S/N</b>", ParagraphStyle('AH1', parent=body_style, fontName=FONT_BOLD, alignment=1, fontSize=5.8)),
            Paragraph("<b>ELEMENT (Structural Profile)</b>", ParagraphStyle('AH2', parent=body_style, fontName=FONT_BOLD, fontSize=5.8)),
            Paragraph("<b>L (mm)</b>", ParagraphStyle('AH3', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=5.8)),
            Paragraph("<b>B (mm)</b>", ParagraphStyle('AH4', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=5.8)),
            Paragraph("<b>t (mm)</b>", ParagraphStyle('AH5', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=5.8)),
            Paragraph("<b>Area (mm²)</b>", ParagraphStyle('AH6', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=5.8)),
            Paragraph("<b>Length</b>", ParagraphStyle('AH7', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=5.8)),
            Paragraph("<b>Vol (m³)</b>", ParagraphStyle('AH8', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=5.8)),
            Paragraph("<b>Density</b>", ParagraphStyle('AH9', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=5.8)),
            Paragraph("<b>Qty</b>", ParagraphStyle('AH10', parent=body_style, fontName=FONT_BOLD, alignment=1, fontSize=5.8)),
            Paragraph("<b>Weight (kg)</b>", ParagraphStyle('AH11', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=5.8)),
            Paragraph("<b>Weight (t)</b>", ParagraphStyle('AH12', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=5.8)),
        ]
    ]

    for a in angles:
        clean_name = a.get('name', '').split('(')[0].strip() if '(' in a.get('name', '') and not a.get('name', '').startswith('Superstructure') and not a.get('name', '').startswith('BHD') and not a.get('name', '').startswith('Deck Beam') else a.get('name', '')
        vol_str = f"{float(a.get('vol', 0)):.4f}"
        kg_str = f"{float(a.get('weight_kg', 0)):,.0f}"
        t_str = f"{float(a.get('weight_tonne', 0)):.3f}"

        angle_rows.append([
            Paragraph(str(a.get('sn', '')), ParagraphStyle('AD1', parent=mono_style, alignment=1, fontSize=5.4)),
            Paragraph(clean_name, ParagraphStyle('AD2', parent=body_style, fontSize=5.4)),
            Paragraph(f"{float(a.get('l_dim', 0)):,.0f}", ParagraphStyle('AD3', parent=mono_style, alignment=2, fontSize=5.4)),
            Paragraph(f"{float(a.get('b_dim', 0)):,.0f}", ParagraphStyle('AD4', parent=mono_style, alignment=2, fontSize=5.4)),
            Paragraph(f"{float(a.get('t', 0)):.1f}", ParagraphStyle('AD5', parent=mono_style, alignment=2, fontSize=5.4)),
            Paragraph(f"{float(a.get('area', 0)):,.0f}", ParagraphStyle('AD6', parent=mono_style, alignment=2, fontSize=5.4)),
            Paragraph(f"{float(a.get('length', 0)):,.0f}", ParagraphStyle('AD7', parent=mono_style, alignment=2, fontSize=5.4)),
            Paragraph(vol_str, ParagraphStyle('AD8', parent=mono_style, alignment=2, fontSize=5.0)),
            Paragraph(str(a.get('density', 7850)), ParagraphStyle('AD9', parent=mono_style, alignment=2, fontSize=5.0)),
            Paragraph(str(a.get('qty', 1)), ParagraphStyle('AD10', parent=mono_style, alignment=1, fontSize=5.4)),
            Paragraph(kg_str, ParagraphStyle('AD11', parent=mono_style, alignment=2, fontSize=5.4)),
            Paragraph(f"<b>{t_str}</b>", ParagraphStyle('AD12', parent=mono_bold, alignment=2, fontSize=5.4)),
        ])

    tot_a_kg = float(ls.get('total_angle_tonne', 0)) * 1000.0
    tot_a_t = float(ls.get('total_angle_tonne', 0))

    angle_rows.append([
        Paragraph("", body_style),
        Paragraph("<b>TOTAL STEEL STIFFENERS WEIGHT:</b>", ParagraphStyle('AT1', parent=body_style, fontName=FONT_BOLD, fontSize=6.0)),
        Paragraph("", body_style), Paragraph("", body_style), Paragraph("", body_style), Paragraph("", body_style), Paragraph("", body_style), Paragraph("", body_style), Paragraph("", body_style), Paragraph("", body_style),
        Paragraph(f"<b>{tot_a_kg:,.0f} kg</b>", ParagraphStyle('AT2', parent=mono_bold, alignment=2, fontSize=6.0)),
        Paragraph(f"<b>{tot_a_t:.3f} t</b>", ParagraphStyle('AT3', parent=mono_bold, alignment=2, fontSize=6.0, textColor=colors.HexColor('#1D4ED8'))),
    ])

    at_table = Table(angle_rows, colWidths=angle_cols)
    at_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")),
        ('INNERGRID', (0,0), (-1,-2), 0.25, colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
        ('LINEABOVE', (0,-1), (-1,-1), 0.6, colors.HexColor("#475569")),
        ('LEFTPADDING', (0,0), (-1,-1), 1.5),
        ('RIGHTPADDING', (0,0), (-1,-1), 1.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.4),
    ]))
    story.append(at_table)
    story.append(Spacer(1, 6))

    # 3. STATUTORY LIGHTSHIP SYNTHESIS TABLE (Fits cleanly on Page 2!)
    story.append(Paragraph("3. STATUTORY LIGHTSHIP SYNTHESIS &amp; TOTAL WEIGHT ESTIMATION", sec_header))
    story.append(Spacer(1, 1))

    tot_steel = float(ls.get('total_steel_tonne', 0))
    allow_t = float(ls.get('allowance_tonne', 0))
    outfit_t = float(ls.get('outfit_tonne', 0))
    piping_t = float(ls.get('piping_tonne', 0))
    elec_t = float(ls.get('electrical_tonne', 0))
    accom_t = float(ls.get('accom_tonne', 0))
    misc_t = float(ls.get('misc_tonne', 0))
    tot_ls = float(ls.get('total_lightship_tonne', 0))

    synth_rows = [
        [
            Paragraph("<b>Weight Item / Statutory Allowance Category</b>", ParagraphStyle('SH1', parent=body_style, fontName=FONT_BOLD, fontSize=6.5)),
            Paragraph("<b>Basis Formula</b>", ParagraphStyle('SH2', parent=body_style, fontName=FONT_BOLD, fontSize=6.5)),
            Paragraph("<b>Weight (Tonne)</b>", ParagraphStyle('SH3', parent=body_style, fontName=FONT_BOLD, alignment=2, fontSize=6.5))
        ],
        [
            Paragraph("<b>Total Net Structural Steel (Plates + Angles)</b>", ParagraphStyle('SB1', parent=body_style, fontName=FONT_BOLD, fontSize=6.5)),
            Paragraph("W_plates + W_angles", ParagraphStyle('SM1', parent=mono_style, fontSize=6.0)),
            Paragraph(f"<b>{tot_steel:.3f} t</b>", ParagraphStyle('SV1', parent=mono_bold, alignment=2, fontSize=6.5))
        ],
        [
            Paragraph("Hull Allowance / Rolling &amp; Welding Margin (20%)", ParagraphStyle('SBD1', parent=body_style, fontSize=6.2)),
            Paragraph("Net Steel × 20%", ParagraphStyle('SM2', parent=mono_style, fontSize=6.0)),
            Paragraph(f"{allow_t:.3f} t", ParagraphStyle('SV2', parent=mono_style, alignment=2, fontSize=6.2))
        ],
        [
            Paragraph("Outfit &amp; Deck Equipment (15%)", ParagraphStyle('SBD2', parent=body_style, fontSize=6.2)),
            Paragraph("Net Steel × 15%", ParagraphStyle('SM3', parent=mono_style, fontSize=6.0)),
            Paragraph(f"{outfit_t:.3f} t", ParagraphStyle('SV3', parent=mono_style, alignment=2, fontSize=6.2))
        ],
        [
            Paragraph("Piping, Valves &amp; Fittings (10%)", ParagraphStyle('SBD3', parent=body_style, fontSize=6.2)),
            Paragraph("Net Steel × 10%", ParagraphStyle('SM4', parent=mono_style, fontSize=6.0)),
            Paragraph(f"{piping_t:.3f} t", ParagraphStyle('SV4', parent=mono_style, alignment=2, fontSize=6.2))
        ],
        [
            Paragraph("Electrical &amp; Instrumentation (3% formula / 5% rule base)", ParagraphStyle('SBD4', parent=body_style, fontSize=6.2)),
            Paragraph("Net Steel × 3%", ParagraphStyle('SM5', parent=mono_style, fontSize=6.0)),
            Paragraph(f"{elec_t:.3f} t", ParagraphStyle('SV5', parent=mono_style, alignment=2, fontSize=6.2))
        ],
        [
            Paragraph("Accommodation Fittings &amp; Furniture (1%)", ParagraphStyle('SBD5', parent=body_style, fontSize=6.2)),
            Paragraph("Net Steel × 1%", ParagraphStyle('SM6', parent=mono_style, fontSize=6.0)),
            Paragraph(f"{accom_t:.3f} t", ParagraphStyle('SV6', parent=mono_style, alignment=2, fontSize=6.2))
        ],
        [
            Paragraph("Miscellaneous Statutory Items (7%)", ParagraphStyle('SBD6', parent=body_style, fontSize=6.2)),
            Paragraph("Net Steel × 7%", ParagraphStyle('SM7', parent=mono_style, fontSize=6.0)),
            Paragraph(f"{misc_t:.3f} t", ParagraphStyle('SV7', parent=mono_style, alignment=2, fontSize=6.2))
        ],
        [
            Paragraph("<b>TOTAL LIGHTSHIP WEIGHT (LIGHTWEIGHT DISPLACEMENT) :</b>", ParagraphStyle('ST1', parent=body_style, fontName=FONT_BOLD, fontSize=7.2, textColor=colors.HexColor('#0F172A'))),
            Paragraph("<b>Net Steel × 1.56 (56% Outfitting)</b>", ParagraphStyle('ST2', parent=mono_bold, fontSize=6.8, textColor=colors.HexColor('#0284C7'))),
            Paragraph(f"<b>{tot_ls:.3f} Tonne</b>", ParagraphStyle('ST3', parent=mono_bold, alignment=2, fontSize=8.0, textColor=colors.HexColor('#1D4ED8')))
        ]
    ]

    synth_table = Table(synth_rows, colWidths=[245, 155, 130])
    synth_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#0284C7")),
        ('INNERGRID', (0,0), (-1,-2), 0.25, colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E0F2FE")),
        ('LINEABOVE', (0,-1), (-1,-1), 0.8, colors.HexColor("#0284C7")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
    ]))
    story.append(KeepTogether([synth_table]))

    # Build Document with CleanCanvas & Designer Corner Seal
    def canvas_maker(*args, **kwargs):
        c = LightshipCleanCanvas(*args, **kwargs)
        c.designer_seal_bytes = designer_seal_bytes
        return c

    doc.build(story, canvasmaker=canvas_maker)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# Alias for backwards compatibility
generate_lightship_pdf = generate_lightship_booklet_pdf
