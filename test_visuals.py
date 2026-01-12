import streamlit as st
import pandas as pd
import sys
from unittest.mock import MagicMock

# ==========================================
# 1. SETUP DUMMY DATA (No Google Sheets needed)
# ==========================================
def get_dummy_data():
    # Fake Notifications
    notif_data = {
        "Message": [
            "Results for 'Pencil Drawing' are out!",
            "Off-stage events starting at 10 AM.",
            "Lunch break from 1:00 PM to 2:00 PM."
        ]
    }
    notif_df = pd.DataFrame(notif_data)

    # Fake Results Data (Matches your real CSV structure)
    data = {
        "Event": [
            "Pencil Drawing", "Pencil Drawing", "Pencil Drawing",
            "Mappilappattu", "Mappilappattu", "Mappilappattu",
            "Oil Painting", "Oil Painting"
        ],
        "Group": [
            "Group 1", "Group 2", "Group 3",
            "Group 5", "Group 1", "Group 4",
            "Group 2", "Group 3"
        ],
        "Position": [
            "First", "Second", "Third",
            "First", "Second", "Third",
            "First", "Second"
        ],
        "Name": [
            "K V Muhammed Safwan", "Fathima Rena", "Jowin Shibu",
            "Shyma K A", "Adithya V", "Raju Bhai",
            "Nandana K", "Arjun Reddy"
        ],
        "Class": [
            "BCom CA", "BCA", "MSc Physics",
            "BCom TT", "BA English", "BBA",
            "BSc CS", "BCom Co-op"
        ],
        "Points": [5, 3, 1, 5, 3, 1, 5, 3],
        "Status": ["final"] * 8  # All are final
    }
    df = pd.DataFrame(data)
    
    return df, notif_df

# ==========================================
# 2. MOCK DEPENDENCIES
# (This tricks Python into thinking 'sheet_utils' exists and works)
# ==========================================
mock_utils = MagicMock()
mock_utils.fetch_all_student_data = get_dummy_data
sys.modules["sheet_utils"] = mock_utils
sys.modules["config"] = MagicMock() # Mock config if needed

# ==========================================
# 3. IMPORT YOUR VIEW
# ==========================================
try:
    # Now we import your ACTUAL file. It will use our fake data above.
    from student_view import render_student_view
except ImportError as e:
    st.error(f"❌ Error importing student_view.py: {e}")
    st.stop()

# ==========================================
# 4. RENDER THE TEST PAGE
# ==========================================
st.set_page_config(layout="wide", page_title="🎨 Visual Test Lab")

st.markdown("""
<div style="background:#e6f3ff; padding:15px; border-radius:10px; border:1px solid #0068c9; margin-bottom:20px;">
    <strong>🛠️ DESIGN MODE</strong><br>
    You are viewing <code>student_view.py</code> with <strong>DUMMY DATA</strong>.<br>
    Edit your <code>student_view.py</code> file, save it, and this page will auto-refresh!
</div>
""", unsafe_allow_html=True)

# Run the function from your file
render_student_view()