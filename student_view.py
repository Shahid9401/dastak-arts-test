# ================= STUDENT VIEW MODULE =================
# ALOKA DASTAR – Arts Fest
# Features: Pure HTML Table (No Iframe) + Dark Mode Contrast Fix + Stable Layout

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
    
    # --- 1. GLOBAL STYLES (CSS) ---
    # We put styles here separately so they don't break the table structure
    st.markdown("""
        <style>
            /* Hide Streamlit UI */
            #MainMenu {visibility: hidden; display: none;}
            header {visibility: hidden; display: none;}
            [data-testid="stHeader"] {visibility: hidden; display: none;}
            footer {visibility: hidden; display: none;}
            [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
            
            /* Import Font */
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
            html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

            /* TABLE STYLES */
            .custom-table {
                width: 100%;
                border-collapse: collapse;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                border: 1px solid #eee;
            }
            .custom-table th {
                background: linear-gradient(180deg, #2f2f2f 0%, #1a1a1a 100%);
                color: #ffffff !important;
                padding: 12px;
                text-align: center;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 14px;
            }
            .custom-table td {
                padding: 12px 8px;
                text-align: center;
                border-bottom: 1px solid #eee;
                font-size: 15px;
                vertical-align: middle;
            }
            
            /* --- DARK MODE FIX --- */
            /* If a row has the class 'winner-row', make text BLACK */
            .winner-row {
                background-color: #fff9db !important;
                font-weight: bold;
            }
            .winner-row td {
                color: #000000 !important; /* Forces Name/Points to be Black */
            }
            .winner-row span {
                color: #000000 !important; /* Forces Group Name to be Black */
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
            <div style="background: linear-gradient(90deg, #fff3cd 0%, #ffecb3 100%); padding: 10px; border-radius: 10px; margin-bottom: 20px; color: #856404; font-weight: 600; overflow: hidden; white-space: nowrap; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <marquee behavior="scroll" direction="left">{running_text}</marquee>
            </div>
            """, unsafe_allow_html=True
        )

    if df.empty:
        st.info("Results will appear here once events are finalized.")
        return

    df_final = df[df["Status"] == "final"]

    # ==========================
    # 🏆 OVERALL POINT TABLE (Pure HTML Construction)
    # ==========================
    st.subheader("🏆 Overall Point Table")

    if df_final.empty:
        st.info("Results pending.")
    else:
        leaderboard = (
            df_final.groupby("Group")["Points"]
            .sum()
            .reset_index()
            .sort_values(by="Points", ascending=False)
        )
        leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))

        # Build Table HTML Manually (Safest Way)
        table_html = '<table class="custom-table">'
        table_html += '<thead><tr><th>Rank</th><th>Group</th><th>Points</th></tr></thead><tbody>'
        
        for _, row in leaderboard.iterrows():
            rank = row['Rank']
            points = row['Points']
            group_id = row['Group']
            group_name = GROUP_NAMES_ML.get(group_id, "")
            
            # Icons
            if rank == 1: rank_disp = "🥇 1st"
            elif rank == 2: rank_disp = "🥈 2nd"
            elif rank == 3: rank_disp = "🥉 3rd"
            else: rank_disp = f"{rank}th"
            
            # Dark Mode Fix Class
            row_class = "winner-row" if rank == 1 else ""
            
            table_html += f'''
            <tr class="{row_class}">
                <td>{rank_disp}</td>
                <td>
                    <span>{group_id}</span><br>
                    <span style="font-size:0.85em; opacity:0.8">{group_name}</span>
                </td>
                <td>{points}</td>
            </tr>
            '''
            
        table_html += '</tbody></table>'
        st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("---")
    
    # ==========================
    # 🎭 EVENT-WISE RESULTS
    # ==========================
    if not df_final.empty:
        st.subheader("🎭 Event-wise Results")

        # Smart Expander Logic
        event_list = ["-- Select Event --"] + sorted(df_final["Event"].unique().tolist())
        
        if "selected_event_key" not in st.session_state:
            st.session_state.selected_event_key = "-- Select Event --"
            
        label = "📂 Tap to Select Event" if st.session_state.selected_event_key == "-- Select Event --" else f"📂 Selected: {st.session_state.selected_event_key}"

        with st.expander(label, expanded=False):
            event_filter = st.radio("Choose:", event_list, key="selected_event_key", label_visibility="collapsed")

        if event_filter != "-- Select Event --":
            event_df = df_final[df_final["Event"] == event_filter]
            event_display_df = event_df[["Position", "Name", "Class", "Group"]]

            # Build Table HTML Manually
            table_html = '<table class="custom-table">'
            table_html += '<thead><tr><th>Pos</th><th>Name</th><th>Class</th><th>Group</th></tr></thead><tbody>'
            
            for _, row in event_display_df.iterrows():
                pos = row['Position']
                name = row['Name']
                cls = row['Class']
                gid = row['Group']
                gname = GROUP_NAMES_ML.get(gid, "")
                
                is_first = str(pos).strip().lower() == "first"
                row_class = "winner-row" if is_first else ""
                
                table_html += f'''
                <tr class="{row_class}">
                    <td>{pos}</td>
                    <td>{name}</td>
                    <td>{cls}</td>
                    <td>
                        <span>{gid}</span><br>
                        <span style="font-size:0.85em; opacity:0.8">{gname}</span>
                    </td>
                </tr>
                '''
            
            table_html += '</tbody></table>'
            st.markdown(table_html, unsafe_allow_html=True)