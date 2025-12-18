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
    OFF_STAGE_EVENTS
)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from student_view import render_student_view
from header import render_header
render_header()

GROUP_NAMES_ML = {
    "Group 1": "കോച്ചേരി",
    "Group 2": "പാണ്ടിപ്പട",
    "Group 3": "അഞ്ഞൂറ്റി",
    "Group 4": "വടക്കൻ വീട്ടിൽ",
    "Group 5": "അറക്കൽ"
}

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="ALOKA DASTAR – Arts Fest", layout="wide")

# ---------------- CONSTANTS ----------------
DATA_FILE = "results.csv"

# ---------------- DATA INIT ----------------
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "Timestamp", "Event", "Position", "Name",
        "Semester", "Class", "Group", "Points", "Status"
    ]).to_csv(DATA_FILE, index=False)

def generate_event_pdf(event_name, df):
    file_name = f"{event_name.replace(' ', '_')}_Final_Results.pdf"

    doc = SimpleDocTemplate(
        file_name,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    elements = []

    # ---------- COLLEGE NAME ----------
    elements.append(
        Paragraph(
            "<b>ASSABAH ARTS AND SCIENCE COLLEGE, VALAYAMKULAM</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            "<b>DASTAK ARTS FESTIVAL 2025</b>",
            styles["Heading2"]
        )
    )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    # ---------- EVENT NAME ----------
    elements.append(
        Paragraph(
            f"<b>Event :</b> {event_name}",
            styles["Heading3"]
        )
    )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    # ---------- RESULT TABLE ----------
    table_data = [list(df.columns)] + df.values.tolist()

    table = Table(table_data, hAlign="CENTER")

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
    ]))

    elements.append(table)

    doc.build(elements)

    return file_name

# ---------------- NAVIGATION ----------------
menu = st.sidebar.radio("Navigation", ["🎓 Student View", "🧑‍🏫 Teacher Panel"])

# ================= STUDENT VIEW =================
if menu == "🎓 Student View":
    render_student_view()
# ================= TEACHER PANEL =================
else:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("🔐 Teacher Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u == TEACHER_USERNAME and p == TEACHER_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        st.success("Welcome, Arts Festival Coordinator 🎭")

        tab1, tab2 = st.tabs(["📝 Result Entry", "📊 Overall Point Table"])

        # -------- RESULT ENTRY --------
        with tab1:
            event_name = st.selectbox("Off-stage Event", OFF_STAGE_EVENTS)

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
                    c1, c2, c3, c4 = st.columns(4)
                    w["Name"] = c1.text_input("Name", key=f"{pos}_n_{i}")
                    w["Semester"] = c2.text_input("Semester", key=f"{pos}_s_{i}")
                    w["Class"] = c3.text_input("Class", key=f"{pos}_c_{i}")
                    w["Group"] = c4.selectbox("Group", list(GROUPS.keys()), key=f"{pos}_g_{i}")

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

                        pdf_file = generate_event_pdf(event_name, final_df)

                        with open(pdf_file, "rb") as f:
                            st.download_button(
                                "⬇️ Download Final Results (PDF)",
                                f,
                                file_name=pdf_file,
                                mime="application/pdf"
                            )

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
            
        with tab2:
            df = pd.read_csv(DATA_FILE)
            final_df = df[df["Status"] == "Final"]

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


