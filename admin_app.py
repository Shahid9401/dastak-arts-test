import streamlit as st
import pandas as pd
from header import render_header
from config import DATA_FILE

st.set_page_config(
    page_title="DASTAK Arts Fest – Admin",
    layout="wide"
)

render_header()

# ---------- ADMIN LOGIN ----------
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"   # change before deployment

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.subheader("🔐 Admin Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.admin_logged_in = True
            st.success("Admin login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

st.header("⚙️ Admin Controls")

df = pd.read_csv(DATA_FILE)

st.subheader("📊 Current Data Overview")
st.dataframe(df)

st.subheader("🚨 Reset All Results")

st.warning(
    "This will permanently delete ALL results.\n"
    "Use only before the actual fest."
)

confirm = st.checkbox("I understand this action cannot be undone")

if confirm:
    if st.button("🗑️ Clear All Results"):
        df.iloc[0:0].to_csv(DATA_FILE, index=False)
        st.success("All results cleared successfully")
        st.rerun()
