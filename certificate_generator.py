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
TEMPLATE_IMG = "certificate_template.jpg"   # Your certificate background
DATA_FILE = "results.csv"                   # Your results file

THEME_BLUE = Color(0/255, 33/255, 71/255)


def generate_certificates_for_event(event_name, source_df=None):
    # 1. GET DATA
    # If the app passed the data directly, use it!
    if source_df is not None:
        df = source_df.copy()
    else:
        # Fallback to reading the file (for manual testing)
        if not os.path.exists(DATA_FILE):
            return f"❌ Error: '{DATA_FILE}' not found."
        df = pd.read_csv(DATA_FILE)

    # Clean columns (Just in case)
    df["Event"] = df["Event"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str).str.strip().str.lower()

    # Filter only FINAL for that event
    event_df = df[(df["Event"] == event_name) & (df["Status"] == "final")]

    if event_df.empty:
        return f"⚠️ No finalized results found for event: {event_name}"
    # -------------------------
    # Read & validate CSV
    # -------------------------
    if not os.path.exists(DATA_FILE):
        return f"❌ Error: '{DATA_FILE}' not found."

    df = pd.read_csv(DATA_FILE)

    # Clean columns
    df["Event"] = df["Event"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str).str.strip().str.lower()

    # Filter only FINAL for that event
    event_df = df[(df["Event"] == event_name) & (df["Status"] == "final")]

    if event_df.empty:
        return f"⚠️ No finalized results found for event: {event_name}"

    # Output PDF
    safe_event = event_name.replace(" ", "_").replace("/", "-")
    output_filename = f"Certificates_{safe_event}.pdf"

    # Create PDF canvas
    c = canvas.Canvas(output_filename, pagesize=landscape(A4))
    width, height = landscape(A4)

    # -------------------------
    # Paragraph Style
    # -------------------------
    cert_style = ParagraphStyle(
        "cert_style",
        fontName="Times-Roman",
        fontSize=20,        # ✅ bigger font
        leading=30,         # ✅ spacing between wrapped lines
        alignment=TA_CENTER,
        textColor=THEME_BLUE
    )

    # -------------------------
    # Generate pages
    # -------------------------
    for _, row in event_df.iterrows():

        # Draw background template
        if os.path.exists(TEMPLATE_IMG):
            c.drawImage(TEMPLATE_IMG, 0, 0, width=width, height=height)
        else:
            print(f"⚠️ Template image not found: {TEMPLATE_IMG}")

        # Read fields safely
        name = str(row.get("Name", "")).strip()
        stu_class = f"{row.get('Class','')}".strip()
        group = f"{row.get('Group','')}".strip()
        position = str(row.get("Position", "")).strip()

        # Format class text
        if group:
            class_text = f"{stu_class} ({group})"
        else:
            class_text = stu_class

        # Format position
        # If your CSV already contains "First", "Second" etc, keep it:
        position_text = f"{position} Place"

        # -------------------------
        # ✅ Single Paragraph Text (Bold Highlights)
        # -------------------------
        certificate_text = f"""
        This certificate is proudly presented to <b>{name}</b>, of <b>{class_text}</b>,
        for securing <b>{position_text}</b> in <b>{event_name}</b>
        at the Arts Festival 2026, held on January 14–15, 2026.
        """

        para = Paragraph(certificate_text, cert_style)

        # Layout values
        max_width = width - 280   # ✅ left/right margins
        w, h = para.wrap(max_width, 400)

        x = (width - max_width) / 2

        # ✅ Adjust this if needed (vertical position)
        y = 160   # try 240 / 250 / 260

        para.drawOn(c, x, y)

        c.showPage()

    c.save()
    return f"✅ Done! Generated: {output_filename}"


# -------------------------
# RUN TEST
# -------------------------
if __name__ == "__main__":
    test_event = "Pencil Drawing"   # Change this to your event name exactly
    print(generate_certificates_for_event(test_event))