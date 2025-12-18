# ================= ALOKA DASTAR – ARTS FEST RESULT & POINT TABLE APP =================
# Clean, stable, error-free version
# Teacher Result Entry (Off-stage) + Student View + Leaderboard

import streamlit as st
import pandas as pd
from datetime import datetime
import os
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
from student_view import render_student_view
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
#menu = st.sidebar.radio("Navigation", ["🎓 Student View", "🧑‍🏫 Teacher Panel"])
st.sidebar.markdown("### 👨‍🏫 Teacher Panel")

# ================= STUDENT VIEW =================
#if menu == "🎓 Student View":
    #render_student_view()
if st.sidebar.button("🚪 Logout"):
    st.session_state.role = None
    st.rerun()
# ================= TEACHER PANEL =================
#else:
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
        # existing result entry
        # finalize
        # PDF download
        
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
            event_name = st.selectbox("Off-stage Event", event_options)

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


            def save_results(status):
                status = status.strip().title()
                df = pd.read_csv(DATA_FILE)

                # ---------- FINALIZE LOGIC ----------
                if status == "Final":
                    # Block duplicate finalization
                    already_final = df[
                        (df["Event"] == event_name) &
                        (df["Status"].str.strip() == "Final")
                    ]
                    if not already_final.empty:
                        st.error("This event has already been finalized.")
                        return

                    # Convert existing Draft → Final
                    draft_mask = (
                        (df["Event"] == event_name) &
                        (df["Status"].str.strip() == "Draft")
                    )
                    if draft_mask.any():
                        df.loc[draft_mask, "Status"] = "Final"
                        df.to_csv(DATA_FILE, index=False)

                        st.success("Draft results finalized successfully")

                        final_df = df[
                            (df["Event"] == event_name) &
                            (df["Status"] == "Final")
                        ][["Position", "Name", "Class", "Group"]]

                        #pdf_file = generate_event_pdf(event_name, final_df)

                        #with open(pdf_file, "rb") as f:
                            #st.download_button(
                                #"⬇️ Download Final Results (PDF)",
                                #f,
                                #file_name=pdf_file,
                                #mime="application/pdf"
                            #)

                        st.session_state.winners = {"First": [], "Second": [], "Third": []}
                        return


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
                            "Semester": w["Semester"],
                            "Class": w["Class"],
                            "Group": w["Group"],
                            "Points": POINTS[pos],
                            "Status": status,
                        })

                if rows:
                    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    st.session_state.winners = {"First": [], "Second": [], "Third": []}
                    st.success(f"Results {status.lower()} successfully")
            
            c1, c2 = st.columns(2)
            if c1.button("💾 Save Draft"):
                save_results("Draft")
            if c2.button("🔒 Finalize"):
                save_results("Final")
                st.session_state.just_finalized = True
                st.success("Event finalized successfully")
                st.rerun()

            # check if event is finalized
            df = pd.read_csv(DATA_FILE)
            is_final = (
                (df["Event"] == event_name) &
                (df["Status"] == "Final")
            ).any()
            
            if is_final and not st.session_state.just_finalized:
                st.error("🚫 This event has already been finalized. Editing is not allowed.")
                st.stop()

            if is_final and st.session_state.just_finalized:
                final_df = df[
                (df["Event"] == event_name) &
                (df["Status"] == "Final")
                ][["Position", "Name", "Class", "Group"]]

                pdf_file = generate_event_pdf(event_name, final_df)

                with open(pdf_file, "rb") as f:
                    st.download_button(
                        "📄 Download Final Result (PDF)",
                        f,
                        file_name=pdf_file.split("\\")[-1],
                        mime="application/pdf"
                    )


        with tab2:
            df = pd.read_csv(DATA_FILE)
            df["Status"] = df["Status"].str.strip().str.lower()
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
                                background:#f2f2f2;
                                font-weight:bold;
                                text-align:center !important;
                                padding:10px;
                            }}
                            td {{
                                text-align:center !important;
                                padding:10px;
                            }}
                            tr:nth-child(1) {{
                                background-color:#fff4cc;
                                font-weight:bold;
                            }}
                        </style>
                        {html_table}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    elif st.session_state.role == "admin":
        st.header("🔒 Admin Panel")

        import pandas as pd

        DATA_FILE = "results.csv"
        df = pd.read_csv(DATA_FILE)

        st.subheader("📊 Current Data")
        st.dataframe(df)

        st.subheader("🚨 Reset All Results")
        st.warning(
            "This will permanently delete ALL results.\n"
            "Use only to clear test data."
        )

        confirm = st.checkbox("I understand this action is irreversible")

        if confirm and st.button("🗑️ Clear All Results"):
            df.iloc[0:0].to_csv(DATA_FILE, index=False)
            st.success("All results cleared successfully")
            st.rerun()
