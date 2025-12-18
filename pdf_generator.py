from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import HRFlowable
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from datetime import datetime
import os

def add_watermark(canvas, doc):
    """
    Draws a light watermark logo at the center of each page
    """
    try:
        logo_path = "logo.png"  # make sure this file exists in project root
        canvas.saveState()

        # Set transparency (light watermark)
        canvas.setFillAlpha(0.08)

        # Load image
        logo = ImageReader(logo_path)

        # Page size
        width, height = A4

        # Desired watermark size
        img_width = 300
        img_height = 300

        # Center position
        x = (width - img_width) / 2
        y = (height - img_height) / 2

        canvas.drawImage(
            logo,
            x,
            y,
            width=img_width,
            height=img_height,
            mask="auto"
        )

        canvas.restoreState()
    except Exception:
        pass  # fail silently (never break PDF)


def generate_event_pdf(event_name, final_df):
    """
    Generates RESULT SHEET PDF for a finalized event.
    Returns generated PDF file path.
    """

    # File name
    safe_event = event_name.replace(" ", "_").replace("/", "_")
    file_name = f"{safe_event}_RESULT.pdf"

    doc = SimpleDocTemplate(
        file_name,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    elements = []

    # ----------- TITLE STYLES -----------
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=10,
    )

    sub_title_style = ParagraphStyle(
        "SubTitle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=10,
    )

    normal_center = ParagraphStyle(
        "NormalCenter",
        parent=styles["Heading3"],
        alignment=TA_CENTER,
        fontSize=14,
        spaceAfter=8,
    )

    # ----------- HEADER -----------
    elements.append(Paragraph("ASSABAH ARTS & SCIENCE COLLEGE", title_style))
    #elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("DASTAK ARTS FESTIVAL 2025", sub_title_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            "<u><b>RESULT SHEET</b></u>",
            normal_center
        )
    )
    elements.append(Spacer(1, 16))

    elements.append(Spacer(1, 12))

    # ----------- EVENT NAME -----------
    event_style = ParagraphStyle(
    "EventStyle",
    parent=styles["Normal"],
    fontSize=12,
    spaceAfter=12
)   

    elements.append(
    Paragraph(f"<b>Event :</b> <b>{event_name}</b>", event_style)
    )

    elements.append(Spacer(1, 12))

    # ----------- RESULT TABLE -----------
    table_data = [["Position", "Name", "Class", "Group"]]

    for _, row in final_df.iterrows():
        table_data.append([
            row["Position"],
            row["Name"],
            row["Class"],
            row["Group"]
        ])

    table = Table(table_data, colWidths=[80, 150, 120, 120])

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 80))

    # ----------- SIGNATURE SECTION -----------
    elements.append(Paragraph("Arts Festival Convenor", styles["Normal"]))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Signature", styles["Normal"]))

    # ----------- FOOTER DATE -----------
    elements.append(Spacer(1, 40))
    elements.append(
        Paragraph(
            f"Date : {datetime.now().strftime('%d-%m-%Y')}",
            styles["Normal"]
        )
    )

    # Build PDF
    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)

    return os.path.abspath(file_name)