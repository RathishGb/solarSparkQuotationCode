"""Solar Quotation PDF Generator - creates professional solar proposal PDFs."""

import math
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Frame, PageTemplate, BaseDocTemplate, KeepTogether,
    Image as RLImage
)
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Color scheme
PRIMARY = HexColor("#1a3a5c")      # Dark navy blue
SECONDARY = HexColor("#2d6a4f")    # Green accent
ACCENT = HexColor("#f4a261")       # Orange accent
LIGHT_BG = HexColor("#f0f4f8")     # Light background
WHITE = white
BLACK = black
DARK_TEXT = HexColor("#2c3e50")
GRAY_TEXT = HexColor("#7f8c8d")
TABLE_HEADER_BG = HexColor("#1a3a5c")
TABLE_ALT_ROW = HexColor("#eef2f7")
BORDER_COLOR = HexColor("#bdc3c7")

# TNEB Tariff slabs (bi-monthly)
TNEB_TARIFF = [
    (100, 0),       # 0-100 units: Free
    (300, 4.7),     # 101-400: Rs 4.7
    (100, 6.3),     # 401-500: Rs 6.3
    (100, 8.4),     # 501-600: Rs 8.4
    (200, 9.45),    # 601-800: Rs 9.45
    (200, 10.5),    # 801-1000: Rs 10.5
    (float('inf'), 11.55),  # Above 1000: Rs 11.55
]

# PM Surya Ghar subsidy rates
# 1 kW = Rs.30,000 | 2 kW = Rs.60,000 | 3 kW and above = Rs.78,000
def calculate_subsidy(kw):
    if kw <= 1:
        return 30000
    elif kw <= 2:
        return 60000
    else:
        return 78000


def calculate_network_charges(system_size_kw, num_days=365):
    """Calculate TNEB network charges based on official TNERC rules.
    
    Formula: Generated units (CUF) × Network charge rate × charge percentage
    - CUF = 21% as stipulated by TNERC
    - Generated units = PV capacity (kW) × 24 × CUF × No of days
    - Network charge rate = Rs.1.59/unit (from 01.07.2024)
    - Domestic up to 10kW: pay 20% of network charges
    """
    cuf = 0.21  # Capacity Utilization Factor
    network_charge_rate = 1.59  # Rs per unit (from 01.07.2024)
    
    # Generated units as per CUF
    generated_units = system_size_kw * 24 * cuf * num_days
    
    # Base network charges
    base_charges = generated_units * network_charge_rate
    
    # Domestic up to 10kW: pay only 20% of network charges
    if system_size_kw <= 10:
        final_charges = base_charges * 0.20
    else:
        final_charges = base_charges
    
    return round(final_charges, 2)


# Logo path
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png')


def format_inr(amount):
    """Format number in Indian currency style (e.g., 1,22,000)."""
    amount = int(round(amount))
    s = str(abs(amount))
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        rest = s[:-3]
        groups = []
        while rest:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        formatted = ",".join(groups) + "," + last3
    return formatted if amount >= 0 else f"-{formatted}"


def calculate_savings(consumption, generation):
    """Calculate bi-monthly savings based on TNEB tariff slabs."""
    # Calculate bill before solar
    bill_before = calculate_bill(consumption)
    # After solar, consumption reduces
    remaining = max(0, consumption - generation)
    bill_after = calculate_bill(remaining)

    # Build savings breakdown: which slab units are saved
    savings_rows = []
    units_to_save = generation
    current_pos = consumption

    # Walk backward from highest slab consumed
    cumulative = 0
    slab_boundaries = []
    for slab_units, rate in TNEB_TARIFF:
        slab_start = cumulative
        slab_end = cumulative + slab_units
        slab_boundaries.append((slab_start, slab_end, rate))
        cumulative += slab_units
        if cumulative >= consumption:
            break

    # Calculate savings from top slab downward
    for slab_start, slab_end, rate in reversed(slab_boundaries):
        if units_to_save <= 0:
            break
        if consumption <= slab_start:
            continue

        units_in_slab = min(consumption, slab_end) - slab_start
        saved_from_slab = min(units_to_save, units_in_slab)

        if saved_from_slab > 0 and rate > 0:
            saving_amount = int(round(saved_from_slab * rate))
            savings_rows.append({
                'units': saved_from_slab,
                'rate': rate,
                'savings': saving_amount
            })
            units_to_save -= saved_from_slab
            consumption -= saved_from_slab

    total_savings = sum(r['savings'] for r in savings_rows)
    return savings_rows, total_savings


def calculate_bill(units):
    """Calculate TNEB bill for given units."""
    remaining = units
    total = 0
    for slab_units, rate in TNEB_TARIFF:
        charged = min(remaining, slab_units)
        total += charged * rate
        remaining -= charged
        if remaining <= 0:
            break
    return total


def generate_solar_pdf(data):
    """Generate solar quotation PDF and return bytes."""
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=25*mm, rightMargin=25*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        'MainTitle', parent=styles['Title'],
        fontSize=28, textColor=PRIMARY, spaceAfter=5*mm,
        fontName='Helvetica-Bold', alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'SubTitle', parent=styles['Normal'],
        fontSize=14, textColor=ACCENT, spaceAfter=3*mm,
        fontName='Helvetica', alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'],
        fontSize=16, textColor=PRIMARY, spaceBefore=6*mm,
        spaceAfter=4*mm, fontName='Helvetica-Bold',
        borderWidth=0, borderPadding=0,
    ))
    styles.add(ParagraphStyle(
        'SubSection', parent=styles['Heading3'],
        fontSize=12, textColor=SECONDARY, spaceBefore=4*mm,
        spaceAfter=2*mm, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'BodyText2', parent=styles['Normal'],
        fontSize=10, textColor=DARK_TEXT, spaceAfter=2*mm,
        fontName='Helvetica', leading=14, alignment=TA_JUSTIFY
    ))
    styles.add(ParagraphStyle(
        'SmallText', parent=styles['Normal'],
        fontSize=9, textColor=GRAY_TEXT,
        fontName='Helvetica', leading=12
    ))
    styles.add(ParagraphStyle(
        'BigPrice', parent=styles['Normal'],
        fontSize=18, textColor=SECONDARY, fontName='Helvetica-Bold',
        alignment=TA_CENTER, spaceAfter=3*mm
    ))
    styles.add(ParagraphStyle(
        'CenterBold', parent=styles['Normal'],
        fontSize=11, textColor=DARK_TEXT, fontName='Helvetica-Bold',
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'BulletText', parent=styles['Normal'],
        fontSize=10, textColor=DARK_TEXT, fontName='Helvetica',
        leftIndent=15, bulletIndent=5, leading=14
    ))
    
    elements = []
    
    consumer_name = data['consumer_name']
    consumer_address = data['consumer_address']
    proposal_date = data['proposal_date']
    connections = data['connections']
    
    # Calculate combined system info
    total_kw = sum(c['kw'] for c in connections)
    total_price = sum(c['price'] for c in connections)
    
    if len(connections) > 1:
        kw_str = "+".join([f"{c['kw']}kW" for c in connections])
        system_desc = f"({kw_str}) {total_kw}kW"
    else:
        system_desc = f"{total_kw}kW"
    
    # Extract name parts for salutation
    name_parts = consumer_name.strip().split()
    last_name = name_parts[-1] if name_parts else consumer_name
    salutation = f"Mr./Ms. {consumer_name}"
    
    # ===================== PAGE 1: PROPOSAL LETTER =====================
    elements.append(Spacer(1, 8*mm))
    
    # Logo
    if os.path.exists(LOGO_PATH):
        logo = RLImage(LOGO_PATH, width=60*mm, height=45*mm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 3*mm))
    
    # Title block
    elements.append(Paragraph("SOLAR", styles['MainTitle']))
    elements.append(Paragraph("Proposal", styles['SubTitle']))
    elements.append(Spacer(1, 5*mm))
    
    # Prepared for/by
    prep_data = [
        [Paragraph(f"<b>Prepared for:</b> {consumer_name}", styles['BodyText2']),
         Paragraph(f"<b>Prepared by:</b> Rathish GB", styles['BodyText2'])]
    ]
    prep_table = Table(prep_data, colWidths=[240, 240])
    prep_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(prep_table)
    elements.append(Spacer(1, 5*mm))
    
    # Horizontal line
    line_data = [["" ]]
    line_table = Table(line_data, colWidths=[480])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, PRIMARY),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 4*mm))
    
    elements.append(Paragraph(
        f"<b>PROPOSAL LETTER</b>", styles['SectionHeader']
    ))
    
    elements.append(Paragraph(f"To,", styles['BodyText2']))
    elements.append(Paragraph(f"{salutation}", styles['BodyText2']))
    elements.append(Paragraph(f"{consumer_address}", styles['BodyText2']))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(f"<b>Date:</b> {proposal_date}", styles['BodyText2']))
    elements.append(Paragraph(
        f"<b>Subject:</b> Rooftop Solar Proposal for your residence",
        styles['BodyText2']
    ))
    elements.append(Spacer(1, 3*mm))
    
    elements.append(Paragraph(
        f"Dear {salutation},", styles['BodyText2']
    ))
    elements.append(Spacer(1, 2*mm))
    elements.append(Paragraph(
        "We sincerely thank you for showing interest in installing a Solar Power Plant. "
        "We are hereby enclosing our proposal for this project.", styles['BodyText2']
    ))
    elements.append(Paragraph(
        f"Based on the total average usage, we propose a <b>{system_desc} Solar Plant</b> "
        "with Bifacial panels. This will ensure higher efficiency, effectively saving "
        "electricity bills &amp; reducing carbon emissions with a life span of 25 years.",
        styles['BodyText2']
    ))
    elements.append(Paragraph(
        "We assure you that all products used will be Industry's best and genuine only. "
        "Our experienced and specialized team will carry out all installations.",
        styles['BodyText2']
    ))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph("We look forward to working with you.", styles['BodyText2']))
    elements.append(Paragraph("Sincerely,", styles['BodyText2']))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph("<b>Rathish GB</b>", styles['BodyText2']))
    elements.append(Paragraph("Solar Sparks Innovation", styles['SmallText']))
    
    # ===================== PER-CONNECTION PAGES =====================
    for idx, conn in enumerate(connections):
        kw = conn['kw']
        price = conn['price']
        eb_number = conn['eb_number']
        yearly_consumption = conn['consumption']  # annual consumption
        consumption = int(round(yearly_consumption / 6))  # bi-monthly
        phase = conn.get('phase', '1Phase')
        
        # Calculate derived values strictly from input data
        panel_watt = conn.get('panel_watt')
        panel_brand = conn.get('panel_brand')
        panel_type = conn.get('panel_type')
        inverter = conn.get('inverter')
        inverter_kw = conn.get('inverter_kw')
        # Fallbacks only if missing in input (show as 'N/A' if not provided)
        panel_watt = float(panel_watt) if panel_watt is not None else 'N/A'
        panel_brand = str(panel_brand) if panel_brand is not None else 'N/A'
        panel_type = str(panel_type) if panel_type is not None else 'N/A'
        inverter = str(inverter) if inverter is not None else 'N/A'
        inverter_kw = float(inverter_kw) if inverter_kw is not None else 'N/A'
        # num_panels and actual_wp only if panel_watt is valid
        if isinstance(panel_watt, float) and panel_watt > 0:
            num_panels = int(conn.get('num_panels', math.ceil((kw * 1000) / panel_watt)))
            actual_wp = num_panels * panel_watt
        else:
            num_panels = 'N/A'
            actual_wp = 'N/A'
        actual_kw = float(conn.get('kw', kw))  # Use input kW directly
        
        # GST calculation: 70% at 5%, 30% at 18%
        base_cost = price - 30000  # Exclude miscellaneous for GST
        gst_70 = 0.7 * base_cost * 0.05
        gst_30 = 0.3 * base_cost * 0.18
        gst_amount = gst_70 + gst_30
        cost_before_gst = base_cost
        misc_expenses = 30000
        subsidy = calculate_subsidy(kw)
        net_price = price - subsidy
        
        daily_gen = round(kw * 4.5, 1)
        bimonthly_gen = int(daily_gen * 60)
        annual_gen = int(daily_gen * 365)
        
        savings_rows, bimonthly_savings = calculate_savings(consumption, bimonthly_gen)
        annual_savings = bimonthly_savings * 6
        network_charges = calculate_network_charges(kw)  # annual (365 days)
        net_yearly_savings = annual_savings - network_charges
        
        if net_yearly_savings > 0:
            payback_years = round(net_price / net_yearly_savings, 1)
        else:
            payback_years = 0
        
        # ===== PAGE: PROPOSED SOLAR PLANT =====
        elements.append(PageBreak())
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph("PROPOSED SOLAR PLANT", styles['MainTitle']))
        
        if len(connections) > 1:
            elements.append(Paragraph(
                f"Connection {idx + 1} of {len(connections)}", styles['SubTitle']
            ))
        
        elements.append(Spacer(1, 8*mm))
        
        # EB number and capacity box (always use input kW, not recalculated)
        center_style = ParagraphStyle('boxCenter', parent=styles['Normal'], alignment=TA_CENTER)
        box_data = [
            [Paragraph(f"<b>Proposed SPV Capacity for ({eb_number})</b>", 
                       ParagraphStyle('b1', parent=center_style, fontSize=11, textColor=WHITE))],
            [Paragraph(f"<b>{kw}kW</b>",
                       ParagraphStyle('b2', parent=center_style, fontSize=24, textColor=ACCENT, fontName='Helvetica-Bold'))],
            [Paragraph(f"Total Price for {kw}kW",
                       ParagraphStyle('b3', parent=center_style, fontSize=11, textColor=WHITE))],
            [Paragraph(f"<b>Rs. {format_inr(price)} /-</b>",
                       ParagraphStyle('b4', parent=center_style, fontSize=18, textColor=ACCENT, fontName='Helvetica-Bold'))],
        ]
        box_table = Table(box_data, colWidths=[380], hAlign='CENTER')
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        elements.append(box_table)
        
        elements.append(Spacer(1, 8*mm))
        
        # Sizing Specifications (all fields from input data)
        elements.append(Paragraph("SIZING – Specifications", styles['SectionHeader']))
        specs = [
            f"<bullet>&bull;</bullet> Panels - {panel_brand} {panel_type} {panel_watt} Wp x {num_panels} = {actual_wp} Wp",
            f"<bullet>&bull;</bullet> Inverter – {inverter} – {inverter_kw} kW – {phase}",
            "<bullet>&bull;</bullet> Rest of the system as per standard",
        ]
        for spec in specs:
            elements.append(Paragraph(spec, styles['BulletText']))
        
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph(
            "The quotation is for design, supply, commissioning, civil works &amp; warranty.",
            styles['BodyText2']
        ))
        
        # ===== PAGE: PRICE SUMMARY =====
        elements.append(PageBreak())
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph("PRICE SUMMARY", styles['MainTitle']))
        
        if len(connections) > 1:
            elements.append(Paragraph(
                f"EB Number: {eb_number}", styles['SubTitle']
            ))
        
        elements.append(Spacer(1, 5*mm))
        
        # Price summary table
        price_data = [
            [Paragraph(f"<b>Total Cost of the {kw} kW Solar Plant (Excl. Misc.)</b>", styles['BodyText2']),
             Paragraph(f"<b>Rs. {format_inr(cost_before_gst)}</b>", 
                       ParagraphStyle('', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold'))],
            [Paragraph(f"GST (70% at 5%, 30% at 18%)", styles['BodyText2']),
             Paragraph(f"Rs. {format_inr(gst_amount)}", 
                       ParagraphStyle('', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT))],
            [Paragraph(f"Miscellaneous Expenses (Delivery, Civil, EB Metering, etc.)", styles['BodyText2']),
             Paragraph(f"Rs. {format_inr(misc_expenses)}", 
                       ParagraphStyle('', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT, textColor=ACCENT))],
            [Paragraph(f"<b>Total price of solar plant</b>", styles['BodyText2']),
             Paragraph(f"<b>Rs. {format_inr(price)}/-</b>", 
                       ParagraphStyle('', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=PRIMARY))],
            [Paragraph(f"Central Government subsidy to the client directly", styles['BodyText2']),
             Paragraph(f"Rs. {format_inr(subsidy)}", 
                       ParagraphStyle('', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT, textColor=SECONDARY))],
            [Paragraph(f"<b>Net Price of the ({kw}kW) Solar plant after subsidy</b>", styles['BodyText2']),
             Paragraph(f"<b>Rs. {format_inr(net_price)}/-</b>", 
                       ParagraphStyle('', parent=styles['Normal'], fontSize=12, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=SECONDARY))],
        ]
        
        price_table = Table(price_data, colWidths=[310, 150])
        price_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_COLOR),
            ('LINEBELOW', (0, -1), (-1, -1), 1.5, PRIMARY),
            ('BACKGROUND', (0, -1), (-1, -1), LIGHT_BG),
            ('BACKGROUND', (0, 2), (-1, 2), LIGHT_BG),
        ]))
        elements.append(price_table)
        
        elements.append(Spacer(1, 8*mm))
        
        # System Components
        elements.append(Paragraph("SYSTEM COMPONENTS", styles['SectionHeader']))
        
        components = [
            f"<b>Solar Panels:</b> {panel_brand} {panel_type} – {panel_watt} Wp x {num_panels} = {actual_wp} Wp – 10-12 years product warranty / 25 years performance warranty.",
            f"<b>Module Mounting Structure:</b> Pre Galvanised mounting structure with needed bolts and nuts",
            f"<b>Grid Tied Inverter:</b> {inverter} – {inverter_kw} kW – {phase}",
            "<b>Remote Monitoring System with Sensors:</b> Inbuilt – PCU Make",
            "<b>DC Distribution Box:</b> IP65 – with Fuses/DC SPD/Switches - MC4 Compatible make - Nordic",
            f"<b>AC Distribution Board:</b> IP65 – PC Closure – with MCB type-2 – MC4 Compatible - SPD at grid side output. Make - Nordic",
            "<b>Earthing System:</b> Copper – Chemical",
            "<b>System Cables:</b> Polycab (both AC, DC &amp; Earthing) - Copper",
        ]
        for comp in components:
            elements.append(Paragraph(comp, styles['BodyText2']))
            elements.append(Spacer(1, 1*mm))
        
        # ===== PAGE: TERMS & CONDITIONS =====
        elements.append(PageBreak())
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph("TERMS &amp; CONDITIONS", styles['MainTitle']))
        elements.append(Spacer(1, 5*mm))
        
        terms = [
            "The above bill of material &amp; system design is subject to change with any change in the project site, site layout and soil condition, and evacuation scheme. Such changes will have commercial implications.",
            "Charges for net-metering and liaison with TNEB and other concerned officials have been added in the above quote.",
            "The quote is valid for 10 days from the date of quotation.",
            "Any civil works other than the foundation for the module mounting structure is the customer's scope. The foundation civil works cost has been added to the quote.",
            "After delivery of materials to the customer's site in good condition, the customer shall be responsible for the safety &amp; security of the materials till handing over of the same to our designated personnel for installation.",
            f"Solar panel product warranty is for 10 years and output warranty is for 25 years. The inverter warranty is for 7 years. Free on-site service will be provided for a period of 5 years from the date of installation.",
            "The material will be supplied within 1 week after confirmed P.O. and advance. Installation will be completed within 1 week after material receipt and site readiness.",
            "We are hopeful to work on the project with you and look forward to hearing from you.",
        ]
        for term in terms:
            elements.append(Paragraph(f"<bullet>&bull;</bullet> {term}", styles['BulletText']))
            elements.append(Spacer(1, 2*mm))
        
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph("Thanks &amp; Regards,", styles['BodyText2']))
        elements.append(Paragraph("<b>Rathish GB</b>", styles['BodyText2']))
        
        elements.append(Spacer(1, 8*mm))
        
        # Payment Terms
        elements.append(Paragraph("PAYMENT TERMS", styles['SectionHeader']))
        payment_terms = [
            "50% advance with confirmed P.O.",
            "40% against material readiness prior to dispatch",
            "10% after installation",
        ]
        for pt in payment_terms:
            elements.append(Paragraph(f"<bullet>&bull;</bullet> {pt}", styles['BulletText']))
        
        elements.append(Spacer(1, 8*mm))
        
        # Payback section
        elements.append(Paragraph("PAYBACK", styles['SectionHeader']))
        
        payback_data = [
            [Paragraph("<b>Total Cost</b>", styles['BodyText2']), ""],
            [Paragraph(f"Total cost of the plant:", styles['BodyText2']),
             Paragraph(f"Rs. {format_inr(price)}/-", styles['BodyText2'])],
            [Paragraph(f"Less Government Subsidy:", styles['BodyText2']),
             Paragraph(f"Rs. {format_inr(subsidy)}/-", styles['BodyText2'])],
            [Paragraph(f"<b>Net cost after subsidy:</b>", styles['BodyText2']),
             Paragraph(f"<b>Rs. {format_inr(net_price)}/-</b>", styles['BodyText2'])],
        ]
        payback_table = Table(payback_data, colWidths=[280, 180])
        payback_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('SPAN', (0, 0), (1, 0)),
            ('LINEBELOW', (0, -1), (-1, -1), 1, PRIMARY),
        ]))
        elements.append(payback_table)
        
        # ===== PAGE: POWER GENERATION & SAVINGS =====
        elements.append(PageBreak())
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph("POWER GENERATION &amp; SAVINGS", styles['MainTitle']))
        
        if len(connections) > 1:
            elements.append(Paragraph(
                f"EB Number: {eb_number}", styles['SubTitle']
            ))
        
        elements.append(Spacer(1, 5*mm))
        
        # Power generation details
        elements.append(Paragraph("Power Generation Details", styles['SubSection']))
        gen_details = [
            f"Estimated average generation per kW: <b>4.5 units/kW</b>",
            f"Average net generation per day: 4.5 x {kw} = <b>{daily_gen} units</b>",
            f"Average Bi-monthly generation: {daily_gen} x 60 = <b>{bimonthly_gen} units</b>",
            f"Estimated annual net generation: {daily_gen} x 365 days = <b>{format_inr(annual_gen)} units</b>",
        ]
        for gd in gen_details:
            elements.append(Paragraph(gd, styles['BodyText2']))
        
        elements.append(Spacer(1, 5*mm))
        
        # EB Tariff
        elements.append(Paragraph("EB Tariff Details", styles['SubSection']))
        tariff_text = [
            "Unit 0 to 100 – Nil",
            "Units 101 to 400 – Rs. 4.7/unit",
            "Units 401 to 500 – Rs. 6.3/unit",
            "Units 501 to 600 – Rs. 8.4/unit",
            "Units 601 to 800 – Rs. 9.45/unit",
            "Units 801 to 1000 – Rs. 10.5/unit",
            "Units above 1000 – Rs. 11.55/unit",
        ]
        for tt in tariff_text:
            elements.append(Paragraph(tt, styles['BodyText2']))
        
        elements.append(Spacer(1, 5*mm))
        
        # EB Savings
        elements.append(Paragraph("EB Savings from the Plant", styles['SubSection']))
        elements.append(Paragraph(
            f"The average bimonthly consumption is estimated to be around "
            f"<b>{format_inr(consumption)} units</b> for EB number (<b>{eb_number}</b>).",
            styles['BodyText2']
        ))
        elements.append(Paragraph(
            f"The solar plant is going to produce <b>{bimonthly_gen} units</b> bi-monthly approximately.",
            styles['BodyText2']
        ))
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph("The bi-monthly savings are as follows:", styles['BodyText2']))
        elements.append(Spacer(1, 3*mm))
        
        # Savings table
        savings_header = [
            Paragraph("<b>Units</b>", ParagraphStyle('', parent=styles['Normal'], fontSize=10, textColor=WHITE, alignment=TA_CENTER)),
            Paragraph("<b>Rate per Unit</b>", ParagraphStyle('', parent=styles['Normal'], fontSize=10, textColor=WHITE, alignment=TA_CENTER)),
            Paragraph("<b>Savings</b>", ParagraphStyle('', parent=styles['Normal'], fontSize=10, textColor=WHITE, alignment=TA_CENTER)),
        ]
        savings_data = [savings_header]
        
        for row in savings_rows:
            savings_data.append([
                Paragraph(str(row['units']), ParagraphStyle('', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)),
                Paragraph(str(row['rate']), ParagraphStyle('', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)),
                Paragraph(f"{format_inr(row['savings'])}/-", ParagraphStyle('', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)),
            ])
        
        # Total row
        savings_data.append([
            Paragraph("<b>TOTAL SAVINGS BI-MONTHLY:</b>", ParagraphStyle('', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            "",
            Paragraph(f"<b>Rs. {format_inr(bimonthly_savings)}/-</b>", ParagraphStyle('', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=SECONDARY, alignment=TA_CENTER)),
        ])
        
        savings_table = Table(savings_data, colWidths=[130, 130, 130])
        savings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -2), 0.5, BORDER_COLOR),
            ('LINEBELOW', (0, -1), (-1, -1), 1.5, PRIMARY),
            ('SPAN', (0, -1), (1, -1)),
            ('BACKGROUND', (0, -1), (-1, -1), LIGHT_BG),
        ]))
        # Alternate row colors
        for i in range(1, len(savings_data) - 1):
            if i % 2 == 0:
                savings_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), TABLE_ALT_ROW),
                ]))
        
        elements.append(savings_table)
        elements.append(Spacer(1, 5*mm))
        
        elements.append(Paragraph(
            f"Total savings per annum: {format_inr(bimonthly_savings)} x 6 = <b>Rs. {format_inr(annual_savings)}/-</b>",
            styles['BodyText2']
        ))
        elements.append(Paragraph(
            f"Network charges per annum: <b>Rs. {format_inr(network_charges)}/-</b>",
            styles['BodyText2']
        ))
        elements.append(Paragraph(
            f"<b>Net yearly savings: Rs. {format_inr(net_yearly_savings)}/-</b>",
            styles['BodyText2']
        ))
        
        elements.append(Spacer(1, 8*mm))
        
        # Summary box
        elements.append(Paragraph("Summary", styles['SectionHeader']))
        
        summary_data = [
            [Paragraph("Total cost of the plant after subsidy:", styles['BodyText2']),
             Paragraph(f"<b>Rs. {format_inr(net_price)}/-</b>", styles['BodyText2'])],
            [Paragraph("Net yearly savings:", styles['BodyText2']),
             Paragraph(f"<b>Rs. {format_inr(net_yearly_savings)}/-</b>", styles['BodyText2'])],
        ]
        if payback_years > 0:
            payback_savings = int(round(net_yearly_savings * payback_years))
            summary_data.append([
                Paragraph(f"Net savings after {payback_years} years:", styles['BodyText2']),
                Paragraph(f"<b>Rs. {format_inr(payback_savings)}/-</b>", styles['BodyText2']),
            ])
            summary_data.append([
                Paragraph(f"<b>Payback Period:</b>", styles['BodyText2']),
                Paragraph(f"<b>~{payback_years} years</b>",
                          ParagraphStyle('', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold', textColor=SECONDARY)),
            ])
        
        summary_table = Table(summary_data, colWidths=[280, 180])
        summary_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_COLOR),
            ('LINEBELOW', (0, -1), (-1, -1), 1.5, PRIMARY),
            ('BACKGROUND', (0, -1), (-1, -1), LIGHT_BG),
        ]))
        elements.append(summary_table)
    
    # Build the PDF
    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def _header_footer(canvas_obj, doc):
    """Add header and footer to each page."""
    canvas_obj.saveState()
    width, height = A4
    
    # Header - logo on left, text on right
    if os.path.exists(LOGO_PATH):
        canvas_obj.drawImage(
            LOGO_PATH, 25*mm, height - 18*mm, width=12*mm, height=9*mm,
            preserveAspectRatio=True, mask='auto'
        )
    
    # Header line
    canvas_obj.setStrokeColor(PRIMARY)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(25*mm, height - 19*mm, width - 25*mm, height - 19*mm)
    
    # Header text (right of logo)
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.setFillColor(PRIMARY)
    canvas_obj.drawString(40*mm, height - 13*mm, "Solar Sparks Innovation")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(GRAY_TEXT)
    canvas_obj.drawRightString(width - 25*mm, height - 13*mm, "Solar Proposal")
    
    # Footer
    canvas_obj.setStrokeColor(PRIMARY)
    canvas_obj.setLineWidth(1)
    canvas_obj.line(25*mm, 15*mm, width - 25*mm, 15*mm)
    
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.setFillColor(GRAY_TEXT)
    canvas_obj.drawString(25*mm, 10*mm, "Solar Sparks Innovation | Rathish GB")
    canvas_obj.drawRightString(width - 25*mm, 10*mm, f"Page {doc.page}")
    
    canvas_obj.restoreState()
