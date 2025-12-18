import pandas as pd
from pdf_generator import generate_event_pdf

df = pd.DataFrame([
    {"Position": "First", "Name": "Anandhu", "Class": "BSc Physics", "Group": "Group 1"},
    {"Position": "Second", "Name": "Rahul", "Class": "BCom", "Group": "Group 2"},
    {"Position": "Third", "Name": "Ameen", "Class": "BA English", "Group": "Group 3"},
])

generate_event_pdf("Painting – Water Colour", df)
