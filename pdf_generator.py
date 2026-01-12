from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from datetime import datetime
import os

# --- CONFIGURATION ---
HEADER_IMG = "dastak1.jpg"
FOOTER_IMG = "footer.jpg"
LOGO_IMG = "logo.png" 

# Use English names for PDF to avoid font rendering issues
GROUP_DISPLAY_NAMES = {
    "Group 1": "Group 1 (Kocheri)",
    "Group 2": "Group 2 (Pandippada)",
    "Group 3": "Group 3 (Anjootti)",
    "Group 4": "Group 4 (Vadakkan Veettil)",
    "Group 5": "Group 5 (Arakkal)"
}

def draw_header_footer_watermark(canvas, doc):
    canvas.saveState()
    page_width, page_height = A4
    
    # 1. WATERMARK
    try:
        if os.path.exists(LOGO_IMG):
            canvas.setFillAlpha(0.08)
            img_size = 350
            canvas.drawImage(LOGO_IMG, (page_width - img_size) / 2, (page_height - img_size) / 2, 
                             width=img_size, height=img_size, mask='auto')
            canvas.setFillAlpha(1.0)
    except Exception: pass

    # 2. HEADER
    try:
        if os.path.exists(HEADER_IMG):
            h_height = 120
            canvas.drawImage(HEADER_IMG, 0, page_height - h_height, width=page_width, height=h_height, mask='auto')
    except Exception: pass

    # 3. FOOTER
    try:
        if os.path.exists(FOOTER_IMG):
            f_height = 100   
            canvas.drawImage(FOOTER_IMG, 0, 0, width=page_width, height=f_height, mask='auto')
    except Exception: pass

    canvas.restoreState()

def generate_event_pdf(event_name, final_df):
    safe_event = event_name.replace(" ", "_").replace("/", "_")
    file_name = f"{safe_event}_RESULT.pdf"

    doc = SimpleDocTemplate(
        file_name,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=130,   
        bottomMargin=110, 
    )

    styles = getSampleStyleSheet()
    elements = []

    # ----------- FORCED WRAPPING STYLE -----------
    # We create a custom style and explicitly set wordWrap
    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=12,
        alignment=TA_CENTER,
        leading=10,
        wordWrap='CJK', # This forces wrapping even for long strings without spaces
    )

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        fontSize=14,
        spaceAfter=20
    )

    elements.append(Paragraph(f"<b>RESULT SHEET: {event_name}</b>", title_style))
    elements.append(Spacer(1, 10))

    # ----------- RESULT TABLE -----------
    # We must ensure EVERY cell that might be long is a Paragraph
    table_data = [["Position", "Name", "Semester", "Class", "Group"]]

    for _, row in final_df.iterrows():
        g_key = str(row["Group"]).strip()
        g_display = GROUP_DISPLAY_NAMES.get(g_key, g_key)

        table_data.append([
            str(row["Position"]),
            Paragraph(str(row["Name"]), cell_style),
            str(row.get("Semester", "-")),
            Paragraph(str(row.get("Class", "-")), cell_style),
            Paragraph(g_display, cell_style),
        ])

    # Adjusted widths to ensure 'Class' has enough room to wrap effectively
    table = Table(table_data, colWidths=[50, 140, 60, 140, 125], repeatRows=1)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, 1), colors.Color(1, 0.84, 0, alpha=0.15)),
    ]))

    elements.append(table)
    
    # ----------- SIGNATURE SECTION -----------
    elements.append(Spacer(1, 50)) 
    sig_data = [
        [f"Date: {datetime.now().strftime('%d-%m-%Y')}", "", "Arts Festival Convenor"],
        ["", "", "(Signature)"]
    ]
    sig_table = Table(sig_data, colWidths=[200, 100, 200])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, 1), 'CENTER'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
    ]))
    
    elements.append(sig_table)

    # Use the build method with header/footer
    doc.build(elements, onFirstPage=draw_header_footer_watermark, onLaterPages=draw_header_footer_watermark)
    return os.path.abspath(file_name)