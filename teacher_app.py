# ================= ALOKA DASTAR – ARTS FEST RESULT & POINT TABLE APP =================
# FULL VERSION: Preserves all features + Fixes PDF Bug + Adds Debug Tool

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time  # Added for sync delay
from config import (
    TEACHER_USERNAME,
    TEACHER_PASSWORD,
    POINTS,
    GROUPS,
    OFF_STAGE_EVENTS,
    ON_STAGE_EVENTS
)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from pdf_generator import generate_event_pdf
from reportlab.lib import colors
# from student_view import render_student_view
from sheet_utils import read_results, write_results, add_notification
from header import render_header


GROUP_NAMES_ML = {
    "Group 1": "കോച്ചേരി",
    "Group 2": "പാണ്ടിപ്പട",
    "Group 3": "അഞ്ഞൂറ്റി",
    "Group 4": "വടക്കൻ വീട്ടിൽ",
    "Group 5": "അറക്കൽ"
}

GROUP_DISPLAY = {
    g: f"{g} – {GROUP_NAMES_ML[g]}"
    for g in GROUP_NAMES_ML
}

TEACHER_USER = "teacher"
TEACHER_PASS = "teacher123"

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

if "role" not in st.session_state:
    st.session_state.role = None

if "just_finalized" not in st.session_state:
    st.session_state.just_finalized = False

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="DASTAK Arts Festival 2025 – Admin", layout="wide")
if st.session_state.role is None:
    render_header(compact=True)
else:
    render_header()

# ---------------- CONSTANTS ----------------
DATA_FILE = "results.csv"

# ---------------- DATA INIT ----------------
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "Timestamp", "Event", "Position", "Name",
        "Semester", "Class", "Group", "Points", "Status"
    ]).to_csv(DATA_FILE, index=False)

# ---------------- NAVIGATION ----------------
st.sidebar.markdown("### 👨‍🏫 Teacher Panel")

if st.sidebar.button("🚪 Logout"):
    st.session_state.role = None
    st.rerun()

# ================= TEACHER PANEL =================
if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    st.subheader("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == TEACHER_USER and p == TEACHER_PASS:
            st.session_state.role = "teacher"
            st.success("Teacher login successful")
            st.rerun()

        elif u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.role = "admin"
            st.success("Admin login successful")
            st.rerun()

        else:
            st.error("Invalid credentials")

    st.stop()

else:
    if st.session_state.role == "teacher":
        st.header("👨‍🏫 Teacher Panel")
        
        st.success("Welcome, Arts Festival Coordinator 🎭")

        event_type = st.radio(
            "Select Event Type",
            ["Off-stage", "On-stage"],
            horizontal=True
        )
        tab1, tab2 = st.tabs(["📝 Result Entry", "📊 Overall Point Table"])
        

        # -------- RESULT ENTRY --------
        GROUP_DISPLAY = {
        g: f"{g} – {GROUP_NAMES_ML[g]}"
        for g in GROUP_NAMES_ML
        }
        with tab1:
            if event_type == "Off-stage":
                event_list = OFF_STAGE_EVENTS
                label = "Off-stage Event"
            else:
                event_list = ON_STAGE_EVENTS
                label = "On-stage Event"

            if not event_list:
                st.info("ℹ️ On-stage events will be added later.")
                st.stop()
            event_options = ["--Select Event--"] + OFF_STAGE_EVENTS
            if (event_type=="Off-stage"):
                event_name = st.selectbox("Off-stage Event", event_options)
            else:
                event_name = st.selectbox("On-stage Event", ["--Select Event--"] + ON_STAGE_EVENTS)
                onstage_category = st.radio(
                "Select On-stage Event Category",
                ["Individual", "Group"],
                horizontal=True
                )
                # Reset winners if on-stage category changes
                if "last_onstage_category" not in st.session_state:
                    st.session_state.last_onstage_category = onstage_category

                if st.session_state.last_onstage_category != onstage_category:
                    st.session_state.winners = {
                        "First": [],
                        "Second": [],
                        "Third": []
                    }
                    st.session_state.last_onstage_category = onstage_category

            if event_name == "-- Select Event --":
                st.info("ℹ️ Please select an event to enter results.")
                st.stop()

            # ------------------ Track event change ------------------
            if "just_finalized" not in st.session_state:
                st.session_state.just_finalized = False

            if "last_event" not in st.session_state:
                st.session_state.last_event = event_name

            if st.session_state.last_event != event_name:
                st.session_state.just_finalized = False
                st.session_state.last_event = event_name
            # -------------------------------------------------------


            if "winners" not in st.session_state:
                st.session_state.winners = {"First": [], "Second": [], "Third": []}

            def add_winner(pos):
                st.session_state.winners[pos].append({
                    "Name": "",
                    "Semester": "",
                    "Class": "",
                    "Group": list(GROUPS.keys())[0]
                })

            for pos in ["First", "Second", "Third"]:
                st.markdown(f"### {pos} Place")
                if st.button(f"➕ Add {pos}", key=f"add_{pos}"):
                    add_winner(pos)

                if (event_type == "On-stage" and onstage_category == "Individual") or (event_type=="Off-stage"):
                    for i, w in enumerate(st.session_state.winners[pos]):
                        c1, c2, c3, c4, c5 = st.columns([3,2,2,3,1])
                        w["Name"] = c1.text_input("Name", key=f"{pos}_n_{i}")
                        w["Semester"] = c2.text_input("Semester", key=f"{pos}_s_{i}")
                        w["Class"] = c3.text_input("Class", key=f"{pos}_c_{i}")
                        group_display = c4.selectbox(
                        "Group",
                        list(GROUP_DISPLAY.values()),
                        key=f"{pos}_g_{i}"
                        )

                        w["Group"] = [k for k, v in GROUP_DISPLAY.items() if v == group_display][0]
                        if c5.button("❌", key=f"del_{pos}_{i}"):
                            st.session_state.winners[pos].pop(i)
                            st.rerun()

                elif event_type == "On-stage" and onstage_category == "Group":
                        for i, w in enumerate(st.session_state.winners[pos]):
                            c1, c2 = st.columns(2)

                            w["Name"] = c1.text_input(
                                "Team / Group Name",
                                key=f"{pos}_team_{i}",
                                placeholder="e.g. Shahid & Party"
                            )

                            w["Group"] = c2.selectbox(
                                "Group",
                                list(GROUP_DISPLAY.keys()),
                                format_func=lambda g: GROUP_DISPLAY[g],
                                key=f"{pos}_g_{i}"
                            )

                            # Maintain schema consistency
                            w["Class"] = "-"
                            w["Semester"] = "-"


            def save_results(status):
                # Ensure status is lowercase for consistency
                status = status.strip().lower()
                from sheet_utils import read_results, write_results, clear_results
                df = read_results()

                df["Event"] = df["Event"].astype(str).str.strip()
                df["Status"] = df["Status"].astype(str).str.strip().str.lower()

                # ---------- SAVE NEW ROWS (Draft or Final) ----------
                rows = []
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for pos, winners in st.session_state.winners.items():
                    for w in winners:
                        if w["Name"].strip() == "":
                            continue
                        rows.append({
                            "Timestamp": ts,
                            "Event": event_name,
                            "Position": pos,
                            "Name": w["Name"],
                            "Semester": w.get("Semester", ""),
                            "Class": w.get("Class", ""),
                            "Group": w["Group"],
                            "Points": POINTS[pos],
                            "Status": status,
                        })

                if rows:
                    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
                    write_results(df)
                    st.session_state.winners = {"First": [], "Second": [], "Third": []}
                    st.success(f"Results saved as {status} successfully")
                    st.cache_data.clear()
            
            if event_name == "--Select Event--":
                st.error("❌ Please select a valid event before saving.")
                st.stop()

            c1, c2 = st.columns(2)
            if c1.button("💾 Save Draft"):
                if event_type == "On-stage" and onstage_category == "Group":
                    # Check if name is entered for the first winner (basic validation)
                    pass 
                save_results("draft")
            
            if c2.button("🔒 Finalize"):
                df = read_results()

                # Normalize columns
                df["Status"] = df["Status"].astype(str).str.strip().str.lower()
                df["Event"] = df["Event"].astype(str).str.strip()
                
                mask = df["Event"] == event_name

                if df[mask].empty:
                    st.error("❌ No rows found for this event. Please Save Draft first.")
                    st.stop()

                if (df.loc[mask, "Status"] == "final").any():
                    st.error("🚫 This event is already finalized")
                    st.stop()

                # 🔥 UPDATE STATUS TO 'final' (lowercase)
                df.loc[mask, "Status"] = "final"

                # 🔥 GENERATE PDF NOW (Before writing to sheet to ensure data exists)
                final_df_for_pdf = df[mask].copy()
                try:
                    pdf_file = generate_event_pdf(event_name, final_df_for_pdf)
                    st.session_state['generated_pdf'] = pdf_file
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")

                write_results(df)
                
                st.session_state.just_finalized = True
                st.cache_data.clear()
                
                st.success("✅ Finalized and written to Google Sheets")
                
                # 🕒 WAIT FOR GOOGLE SHEETS PROPAGATION
                with st.spinner("Syncing with cloud..."):
                    time.sleep(2) 

                add_notification(
                "FINAL",
                f"Results finalized for {event_name}",
                event_name
                )
  
                st.rerun()

            # --------- CHECK STATUS & SHOW PDF ---------
            from sheet_utils import read_results
            df = read_results()
            df["Status"] = df["Status"].astype(str).str.strip().str.lower()
            df["Event"] = df["Event"].astype(str).str.strip()

            event_rows = df[df["Event"] == event_name]

            is_final = (
                not event_rows.empty and
                (event_rows["Status"] == "final").all()
            )

            if "last_event" not in st.session_state:
                st.session_state.last_event = None

            if st.session_state.last_event != event_name:
                st.session_state.just_finalized = False
                st.session_state.last_event = event_name

            if is_final:
                # FIX: Match the lowercase 'final' used in sheet_utils
                final_df = df[
                    (df["Event"] == event_name) &
                    (df["Status"] == "final") 
                ]
                
                # --- DEBUG SECTION ---
                with st.expander("🔍 Debug PDF Data (Open if PDF is blank)"):
                    st.write(f"**Event Selected:** '{event_name}'")
                    st.write(f"**Total Rows:** {len(event_rows)}")
                    st.write("**Finalized Rows:**", len(final_df))
                    st.dataframe(final_df) 
                # ---------------------

                # If dataframe is empty but is_final is true (rare race condition),
                # fallback to the one we generated during the button click
                if final_df.empty and 'generated_pdf' in st.session_state:
                     pdf_file = st.session_state['generated_pdf']
                else:
                    pdf_file = generate_event_pdf(event_name, final_df)

                with open(pdf_file, "rb") as f:
                    st.download_button(
                        "📄 Download Final Result (PDF)",
                        f,
                        file_name=pdf_file.split(os.sep)[-1],
                        mime="application/pdf"
                    )
            elif not is_final and st.session_state.just_finalized:
                 # Fallback if finalized but sheet sync is slow
                 st.warning("⚠️ Syncing results... Refresh page if PDF button doesn't appear.")

        with tab2:
            from sheet_utils import read_results
            df = read_results()

            df["Status"] = df["Status"].astype(str).str.strip().str.lower()
            final_df = df[df["Status"] == "final"]

            if final_df.empty:
                st.info("No finalized results yet")
            else:
                leaderboard = (
                    final_df.groupby("Group")["Points"]
                    .sum()
                    .reset_index()
                    .sort_values(by="Points", ascending=False)
                )

                leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))

                def rank_label(r):
                    if r == 1:
                        return "🥇 1st"
                    elif r == 2:
                        return "🥈 2nd"
                    elif r == 3:
                        return "🥉 3rd"
                    else:
                        return f"{r}th"

                leaderboard["Rank"] = leaderboard["Rank"].apply(rank_label)


                leaderboard["Group"] = leaderboard["Group"].apply(
                    lambda g: f"{g} – {GROUP_NAMES_ML.get(g, '')}"
                )

                display_leaderboard = leaderboard[["Rank", "Group", "Points"]]
                html_table = display_leaderboard.to_html(index=False, escape=False)

                st.markdown(
                f"""
                <div style="max-width:900px; margin:auto;">
                    <style>
                        table {{ width:100%; border-collapse:collapse; }}
                        th {{
                            background:#2f2f2f;
                            color:#ffffff;
                            font-weight:bold;
                            text-align:center !important;
                            padding:10px;
                        }}
                        td {{
                            text-align:center !important;
                            padding:10px;
                            color:inherit;
                        }}
                        tr:nth-child(1) {{
                            background:rgba(255,215,0,0.15);
                            font-weight:700
                            border-left:6px solid #f5b301;
                        }}
                        tr{{border-bottom:1px solid rgba(255,215,0,0.15)}}
                    </style>
                    {html_table}
                </div>
                """,
                unsafe_allow_html=True
            )
    elif st.session_state.role == "admin":
        st.header("🔒 Admin Panel")
        
        # Reset Logic
        from sheet_utils import read_results, write_results, clear_results
        df = read_results()

        st.subheader("📊 Current Data")
        st.dataframe(df)

        st.subheader("🚨 Reset All Results")
        st.warning(
            "This will permanently delete ALL results.\n"
            "Use only to clear test data."
        )

        confirm = st.checkbox("I understand this action is irreversible")

        if confirm and st.button("🗑️ Clear All Results"):
            clear_results()
            st.success("All results cleared successfully")
            st.rerun()