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

# Navy Blue matches your certificate border
THEME_BLUE = Color(0/255, 33/255, 71/255) 

def generate_certificates_for_event(event_name, source_df=None):
    # 1. GET DATA
    # If the app passed the data directly, use it!
    if source_df is not None:
        df = source_df.copy()
    else:
        # Fallback to reading the file (only for manual testing)
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

    # 2. SETUP PDF
    safe_event = event_name.replace(" ", "_").replace("/", "-")
    output_filename = f"Certificates_{safe_event}.pdf"

    # Create PDF canvas
    c = canvas.Canvas(output_filename, pagesize=landscape(A4))
    width, height = landscape(A4)

    # 3. STYLE
    cert_style = ParagraphStyle(
        "cert_style",
        fontName="Times-Roman",
        fontSize=18,        
        leading=30,         
        alignment=TA_CENTER,
        textColor=THEME_BLUE
    )

    # 4. GENERATE PAGES
    for _, row in event_df.iterrows():
        # Draw background template
        if os.path.exists(TEMPLATE_IMG):
            c.drawImage(TEMPLATE_IMG, 0, 0, width=width, height=height)
        
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

        # HTML Formatted Text
        certificate_text = f"""
        This certificate is proudly presented to<br/>
        <b><font size=28>{name}</font></b><br/><br/>
        of {class_text} for securing<b><font size=24>{position} Place</font></b> in <b>{event_name}</b>at the Arts Festival 2026, held on January 14–15, 2026.
        """

        para = Paragraph(certificate_text, cert_style)
        
        # ALIGNMENT LOGIC (Start 50px below center to clear the ribbon)
        max_width = width - 150
        w, h = para.wrap(max_width, 400)
        
        y_position = (height / 2) - h - 50
        
        para.drawOn(c, (width - max_width) / 2, y_position)

        c.showPage()

    c.save()
    
    # Return JUST the filename so the App can find it easily
    return output_filename

# -------------------------
# RUN TEST
# -------------------------
if __name__ == "__main__":
    test_event = "Pencil Drawing" 
    print(generate_certificates_for_event(test_event))