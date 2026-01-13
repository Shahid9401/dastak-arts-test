import pandas as pd
import os

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER

# -------------------------
# CONFIG
# -------------------------
TEMPLATE_IMG = "certificate_template.jpg"
DATA_FILE = "results.csv"
LOGO_WATERMARK = "logo.png"

THEME_BLUE = Color(0/255, 33/255, 71/255)

def draw_watermark_logo(c, width, height, logo_path):
    """Draw logo as a light watermark in the center."""
    if not os.path.exists(logo_path):
        return

    logo_w = 250   # change size if needed
    logo_h = 250

    x = (width - logo_w) / 2
    y = (height - logo_h) / 2 - 20

    c.saveState()

    # ✅ transparency (works on most viewers)
    try:
        c.setFillAlpha(0.08)   # 0 = invisible, 1 = solid
    except:
        pass

    c.drawImage(
        logo_path,
        x, y,
        width=logo_w,
        height=logo_h,
        mask="auto"
    )
    
    c.restoreState()


def generate_certificates_for_event(event_name, source_df=None):

    # 1. LOAD DATA
    if source_df is not None:
        df = source_df.copy()
    else:
        if not os.path.exists(DATA_FILE):
            return f"❌ Error: '{DATA_FILE}' not found."
        df = pd.read_csv(DATA_FILE)

    df["Event"] = df["Event"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str).str.strip().str.lower()

    event_df = df[(df["Event"] == event_name) & (df["Status"] == "final")]

    if event_df.empty:
        return f"⚠️ No finalized results found for event: {event_name}"

    # 2. PDF SETUP
    safe_event = event_name.replace(" ", "_").replace("/", "-")
    output_filename = f"Certificates_{safe_event}.pdf"

    c = canvas.Canvas(output_filename, pagesize=landscape(A4))
    width, height = landscape(A4)

    # 3. TEXT STYLE
    cert_style = ParagraphStyle(
        "cert_style",
        fontName="Times-Roman",
        fontSize=18,
        leading=30,
        alignment=TA_CENTER,
        textColor=THEME_BLUE
    )

    # 4. GENERATE CERTIFICATES
    for _, row in event_df.iterrows():

        if os.path.exists(TEMPLATE_IMG):
            c.drawImage(TEMPLATE_IMG, 0, 0, width=width, height=height)

        draw_watermark_logo(c, width, height, "logo.png")

        name = str(row.get("Name", "")).strip()
        stu_class = str(row.get("Class", "")).strip()
        group = str(row.get("Group", "")).strip()
        position = str(row.get("Position", "")).strip()

        class_text = f"{stu_class} ({group})" if group else stu_class

        # ✅ FIXED PARAGRAPH (proper spacing + line breaks)
        #HTML Formatted Text
        GOLD ="#B08D57"
        certificate_text = f"""
        <para>
        This certificate is proudly presented to<br/>
        <b><font size="28">{name}</font></b><br/>
        <b>of {class_text}</b> for securing <b><color="rgb(176,141,87)">{position} Place</b> in <b>{event_name}</b><br/>
        at the <b>Dastak Arts Festival 2026</b>, held on January 14–15, 2026.
        </para>
        """.strip()

        para = Paragraph(certificate_text, cert_style)

        max_width = width - 150
        w, h = para.wrap(max_width, 500)

        # Position nicely below ribbon
        y_position = (height / 2) - h - 50

        para.drawOn(c, (width - max_width) / 2, y_position)

        c.showPage()

    c.save()
    return f"✅ Success: {output_filename}"


# -------------------------
# TEST RUN
# -------------------------
if __name__ == "__main__":
    test_event = "Pencil Drawing"
    print(generate_certificates_for_event(test_event))