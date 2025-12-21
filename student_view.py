# ================= STUDENT VIEW MODULE =================
# ALOKA DASTAR – Arts Fest
# Features: Stable Old Logic (st.markdown) + Smart Expander + DARK MODE FIX

import streamlit as st
import pandas as pd
from config import DATA_FILE
from sheet_utils import fetch_all_student_data

GROUP_NAMES_ML = {
    "Group 1": "കോച്ചേരി",
    "Group 2": "പാണ്ടിപ്പട",
    "Group 3": "അഞ്ഞൂറ്റി",
    "Group 4": "വടക്കൻ വീട്ടിൽ",
    "Group 5": "അറക്കൽ"
}

def render_student_view():
    
    # --- 1. CLEAN MODE CSS & GLOBAL STYLES ---
    st.markdown("""
        <style>
            /* Hide Streamlit UI */
            #MainMenu {visibility: hidden; display: none;}
            header {visibility: hidden; display: none;}
            [data-testid="stHeader"] {visibility: hidden; display: none;}
            footer {visibility: hidden; display: none;}
            [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
            
            /* Custom Expander Styling */
            .streamlit-expanderHeader {
                background-color: #f0f2f6;
                color: #31333F;
                border-radius: 8px;
                font-weight: 600;
            }
            
            /* --- NUCLEAR CONTRAST FIX --- */
            /* Force the first row (Winner) to be Yellow */
            table tr:nth-child(1) {
                background-color: #fff9db !important;
                font-weight: bold;
            }
            
            /* FORCE TEXT BLACK in the first row (Fixes Dark Mode) */
            table tr:nth-child(1) td {
                color: #000000 !important;
            }
            table tr:nth-child(1) span {
                color: #000000 !important;
            }
            table tr:nth-child(1) b {
                color: #000000 !important;
            }
            
            /* Headers */
            th {
                background-color: #2f2f2f;
                color: white !important;
                text-align: center;
                padding: 10px;
            }
            td {
                text-align: center;
                vertical-align: middle;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- 2. DATA FETCH ---
    df, notif_df = fetch_all_student_data()

    # --- 3. NOTIFICATIONS ---
    if not notif_df.empty:
        latest_msgs = notif_df.head(5)["Message"].astype(str).tolist()
        running_text = "  🔸  ".join(latest_msgs)
        st.markdown(
            f"""
            <div style="background:#fff3cd; padding:10px; border-radius:8px; margin-bottom:15px; color:#856404; font-weight:bold; overflow:hidden; white-space:nowrap;">
                <marquee behavior="scroll" direction="left">{running_text}</marquee>
            </div>
            """, unsafe_allow_html=True
        )

    if df.empty:
        st.info("Results will appear here once events are finalized.")
        return

    df_final = df[df["Status"] == "final"]

    # ==========================
    # 🏆 OVERALL POINT TABLE (OLD LOGIC: st.markdown)
    # ==========================
    st.subheader("🏆 Overall Point Table")

    if df_final.empty:
        st.info("Results pending.")
    else:
        # Prepare Data
        leaderboard = (
            df_final.groupby("Group")["Points"]
            .sum()
            .reset_index()
            .sort_values(by="Points", ascending=False)
        )
        leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))

        # Format Columns
        leaderboard["Rank"] = leaderboard["Rank"].apply(lambda r: f"🥇 1st" if r==1 else (f"🥈 2nd" if r==2 else (f"🥉 3rd" if r==3 else f"{r}th")))
        leaderboard["Group"] = leaderboard["Group"].apply(lambda g: f"{g} – {GROUP_NAMES_ML.get(g, '')}")

        # Convert to HTML
        html_table = leaderboard[["Rank", "Group", "Points"]].to_html(index=False, escape=False)

        # Render (CSS is already handled globally above)
        st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("---")
    
    # ==========================
    # 🎭 EVENT-WISE RESULTS (OLD LOGIC: st.markdown)
    # ==========================
    if not df_final.empty:
        st.subheader("🎭 Event-wise Results")

        # Smart Expander (Logic only)
        event_list = ["-- Select Event --"] + sorted(df_final["Event"].unique().tolist())
        
        if "selected_event_key" not in st.session_state:
            st.session_state.selected_event_key = "-- Select Event --"
            
        label = "📂 Tap to Select Event" if st.session_state.selected_event_key == "-- Select Event --" else f"📂 Selected: {st.session_state.selected_event_key}"

        with st.expander(label, expanded=False):
            event_filter = st.radio("Choose:", event_list, key="selected_event_key", label_visibility="collapsed")

        if event_filter != "-- Select Event --":
            event_df = df_final[df_final["Event"] == event_filter].copy()
            
            # Formatting (Stacked Group Name)
            # Note: We use simple <span> tags so our Global CSS can target them
            def format_group(g):
                name = GROUP_NAMES_ML.get(g, "")
                return f"<b>{g}</b><br><span style='font-size:0.8em;'>{name}</span>"
            
            event_df["Group"] = event_df["Group"].apply(format_group)
            
            # Select Columns
            display_df = event_df[["Position", "Name", "Class", "Group"]]
            
            # Convert to HTML
            html_event = display_df.to_html(index=False, escape=False)
            
            # Render
            st.markdown(html_event, unsafe_allow_html=True)