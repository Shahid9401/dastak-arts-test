import pandas as pd
import gspread
import streamlit as st
import concurrent.futures  # <--- NEW: For parallel processing
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import SHEET_ID, RESULTS_SHEET, NOTIFICATIONS_SHEET

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    creds = Credentials.from_service_account_file(
        "service_account.json", scopes=SCOPES
    )
    return gspread.authorize(creds)

# Initialize global client
client = get_client()

# ================= TEACHER APP FUNCTIONS (PRESERVED) =================

@st.cache_data(ttl=30)
def read_results():
    # Use local client inside function for thread safety in Streamlit
    local_client = get_client()
    try:
        sheet = local_client.open_by_key(SHEET_ID).worksheet(RESULTS_SHEET)
        data = sheet.get_all_records()
    except Exception as e:
        # Fail silently or log error, return empty DF to avoid crash
        return pd.DataFrame()

    if not data:
        return pd.DataFrame(columns=[
            "Event", "Position", "Name", "Semester",
            "Class", "Group", "Points", "Status", "Timestamp"
        ])

    df = pd.DataFrame(data)

    EXPECTED_COLUMNS = [
        "Event", "Position", "Name", "Semester",
        "Class", "Group", "Points", "Status", "Timestamp"
    ]

    # Force column structure and handle missing columns
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df.reindex(columns=EXPECTED_COLUMNS)
    
    # safe string conversion
    df["Status"] = df["Status"].astype(str).str.strip().str.lower()
    df["Event"] = df["Event"].astype(str).str.strip()
    
    return df

def write_results(df):
    local_client = get_client()
    sheet = local_client.open_by_key(SHEET_ID).worksheet(RESULTS_SHEET)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.fillna("").values.tolist())

def clear_results():
    local_client = get_client()
    sheet = local_client.open_by_key(SHEET_ID).worksheet(RESULTS_SHEET)
    sheet.clear()
    sheet.append_row(
        ["Event", "Position", "Name", "Semester", "Class", "Group", "Points", "Status", "Timestamp"]
    )

def add_notification(type_str, message, event):
    """
    Adds a notification row. Creates the sheet if it doesn't exist.
    """
    local_client = get_client()
    spreadsheet = local_client.open_by_key(SHEET_ID)
    
    try:
        # Try to open the existing sheet
        sheet = spreadsheet.worksheet(NOTIFICATIONS_SHEET)
    except gspread.exceptions.WorksheetNotFound:
        # If not found, create it!
        sheet = spreadsheet.add_worksheet(title=NOTIFICATIONS_SHEET, rows=1000, cols=5)
        # Add header row
        sheet.append_row(["Type", "Message", "Event", "Timestamp", "Read"])
        
    sheet.append_row([
        type_str,
        message,
        event,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "FALSE"     
    ])

# ================= OLD STUDENT FUNCTIONS (PRESERVED) =================
# kept for compatibility

@st.cache_data(ttl=10)
def read_notifications_student():
    client = get_client()
    try:
        sheet = client.open_by_key(SHEET_ID).worksheet(NOTIFICATIONS_SHEET)
        data = sheet.get_all_records()
    except:
        return pd.DataFrame()

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.sort_values("Timestamp", ascending=False)
    return df

@st.cache_data(ttl=10)
def read_results_student():
    client = get_client()
    try:
        sheet = client.open_by_key(SHEET_ID).worksheet(RESULTS_SHEET)
        data = sheet.get_all_records()
    except:
        return pd.DataFrame()

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    if "Status" in df.columns:
        df["Status"] = df["Status"].astype(str).str.strip().str.lower()

    return df

# ================= NEW FAST FUNCTION (PARALLEL) =================

def _fetch_results_raw():
    """Internal helper: Non-cached fetch for parallel execution"""
    client = get_client()
    try:
        sheet = client.open_by_key(SHEET_ID).worksheet(RESULTS_SHEET)
        data = sheet.get_all_records()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def _fetch_notifications_raw():
    """Internal helper: Non-cached fetch for parallel execution"""
    client = get_client()
    try:
        sheet = client.open_by_key(SHEET_ID).worksheet(NOTIFICATIONS_SHEET)
        data = sheet.get_all_records()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=15)
def fetch_all_student_data():
    """
    Fetches Results AND Notifications at the same time (Parallel).
    Drastically reduces load time.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Launch both tasks simultaneously
        future_results = executor.submit(_fetch_results_raw)
        future_notifs = executor.submit(_fetch_notifications_raw)
        
        # Wait for both to finish
        df_results = future_results.result()
        df_notifs = future_notifs.result()

    # --- PROCESS RESULTS ---
    if df_results.empty:
        df_results = pd.DataFrame(columns=[
            "Event", "Position", "Name", "Semester",
            "Class", "Group", "Points", "Status", "Timestamp"
        ])
    else:
        # Normalize columns
        expected_cols = [
            "Event", "Position", "Name", "Semester",
            "Class", "Group", "Points", "Status", "Timestamp"
        ]
        for col in expected_cols:
            if col not in df_results.columns:
                df_results[col] = ""
        
        df_results = df_results.reindex(columns=expected_cols)
        df_results["Status"] = df_results["Status"].astype(str).str.strip().str.lower()
        df_results["Event"] = df_results["Event"].astype(str).str.strip()

    # --- PROCESS NOTIFICATIONS ---
    if not df_notifs.empty:
        df_notifs["Timestamp"] = pd.to_datetime(df_notifs["Timestamp"], errors="coerce")
        df_notifs = df_notifs.sort_values("Timestamp", ascending=False)

    return df_results, df_notifs