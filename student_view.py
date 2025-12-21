# ================= STUDENT VIEW MODULE =================
# ALOKA DASTAR – Arts Fest
# Features: Stable Tables + Fast Speed + Clean UI + Smart Expander + PRO VISUALS (Classic Table)

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
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
    
    # --- 1. CLEAN MODE CSS & GLOBAL FONTS ---
    st.markdown("""
        <style>
            /* IMPORT GOOGLE FONT 'POPPINS' */
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

            /* APPLY FONT GLOBALLY */
            html, body, [class*="css"] {
                font-family: 'Poppins', sans-serif;
            }

            /* HIDE STREAMLIT UI ELEMENTS */
            #MainMenu {visibility: hidden; display: none;}
            header {visibility: hidden; display: none;}
            [data-testid="stHeader"] {visibility: hidden; display: none;}
            footer {visibility: hidden; display: none;}
            [data-testid="stToolbar"] {visibility: hidden !important; display: none !important; height: 0px !important;}
            .stDeployButton {display: none !important;}
            
            /* CUSTOM EXPANDER STYLING */
            .streamlit-expanderHeader {
                background-color: #f8f9fa;
                border-radius: 8px;
                font-weight: 600;
                color: #333;
                border: 1px solid #eee;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- 2. FAST DATA FETCH ---
    df, notif_df = fetch_all_student_data()

    # --- 3. NOTIFICATIONS (Marquee) ---
    if not notif_df.empty:
        latest_msgs = notif_df.head(5)["Message"].astype(str).tolist()
        running_text = "  🔸  ".join(latest_msgs)

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(90deg, #fff3cd 0%, #ffecb3 100%);
                padding: 12px 0;
                border-radius: 12px;
                margin-bottom: 20px;
                font-size: 16px;
                font-weight: 600;
                color: #856404;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                overflow: hidden;
                white-space: nowrap;
            ">
                <marquee behavior="scroll" direction="left" scrollamount="6">
                    📢 {running_text}
                </marquee>
            </div>
            """,
            unsafe_allow_html=True
        )

    if df.empty:
        st.info("Results will appear here once events are finalized.")
        return

    # Filter for Final results
    df_final = df[df["Status"] == "final"]

    # ==========================
    # 🏆 OVERALL POINT TABLE (Restored to Classic Look)
    # ==========================
    st.subheader("🏆 Overall Point Table")

    if df_final.empty:
        st.info("🎭 Results will appear here once events are finalized. Please check back soon.")
    else:
        leaderboard = (
            df_final.groupby("Group")["Points"]
            .sum()
            .reset_index()
            .sort_values(by="Points", ascending=False)
        )
        leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))

        def rank_label(r):
            if r == 1: return "🥇 1st"
            elif r == 2: return "🥈 2nd"
            elif r == 3: return "🥉 3rd"
            else: return f"{r}th"

        leaderboard["Rank"] = leaderboard["Rank"].apply(rank_label)
        leaderboard["Group"] = leaderboard["Group"].apply(
            lambda g: f"{g} – {GROUP_NAMES_ML.get(g, '')}"
        )

        html_table = leaderboard[["Rank", "Group", "Points"]].to_html(index=False, escape=False)

        # RENDER TABLE WITH SHADOWS & ROUNDED CORNERS (But Classic Numbers)
        st.markdown(
            f"""
            <div style="
                max-width:900px; 
                margin:auto; 
                overflow:hidden; 
                border-radius:12px;           
                box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
                border: 1px solid #eee;
            ">
                <style>
                    table {{ width:100%; border-collapse:collapse; font-family: 'Poppins', sans-serif; }}
                    th {{
                        background: linear-gradient(180deg, #2f2f2f 0%, #1a1a1a 100%); 
                        color: #ffffff;
                        font-weight: 600;
                        text-align: center !important;
                        padding: 14px;
                        font-size: 14px;
                        letter-spacing: 0.5px;
                        text-transform: uppercase;
                    }}
                    td {{
                        text-align: center !important;
                        padding: 12px;
                        color: inherit;
                        border-bottom: 1px solid #eee;
                        font-size: 15px;
                    }}
                    tr:nth-child(1) {{
                        background: #fff9db; 
                        font-weight: 700;
                        border-left: 6px solid #f5b301;
                    }}
                </style>
                {html_table}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    
    # ==========================
    # 🎭 EVENT-WISE RESULTS (Pro Visuals + Smart Expander)
    # ==========================
    if not df_final.empty:
        st.subheader("🎭 Event-wise Results")

        event_list = ["-- Select Event --"] + sorted(df_final["Event"].unique().tolist())
        
        # Smart Label Logic
        if "selected_event_key" not in st.session_state:
            st.session_state.selected_event_key = "-- Select Event --"

        current_selection = st.session_state.selected_event_key
        expander_label = "📂 Tap here to Select Event" if current_selection == "-- Select Event --" else f"📂 Selected: {current_selection}"

        with st.expander(expander_label, expanded=False):
            event_filter = st.radio(
                "Choose an event:",
                options=event_list,
                key="selected_event_key",
                label_visibility="collapsed"
            )

        if event_filter != "-- Select Event --":
            event_df = df_final[df_final["Event"] == event_filter]
            event_display_df = event_df[["Position", "Name", "Class", "Group"]]

            table_rows_html = ""
            for _, row in event_display_df.iterrows():
                is_first = str(row['Position']).strip().lower() == "first"
                row_style = 'style="background-color: rgba(255, 215, 0, 0.15); font-weight: 600;"' if is_first else ""
                
                g_id = row['Group']
                g_name = GROUP_NAMES_ML.get(g_id, "")
                group_html = f"<span style='color:#333; font-weight:600;'>{g_id}</span><br><span style='font-size:0.85em; opacity:0.6;'>{g_name}</span>"

                table_rows_html += f"""
                <tr {row_style}>
                    <td>{row['Position']}</td>
                    <td>{row['Name']}</td>
                    <td>{row['Class']}</td>
                    <td>{group_html}</td>
                </tr>
                """

            import streamlit.components.v1 as components

            # RENDER EVENT TABLE
            components.html(
                f"""
                <div style="
                    overflow-x: auto; 
                    border-radius: 12px;              
                    box-shadow: 0 4px 10px rgba(0,0,0,0.08); 
                    border: 1px solid #eee;
                ">
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
                        
                        :root {{ --bg: #ffffff; --text: #1a1a1a; --header-bg: #f8f9fa; }}
                        @media (prefers-color-scheme: dark) {{ :root {{ --bg: #0e1117; --text: #fafafa; --header-bg: #1d2129; }} }}
                        
                        body {{ margin: 0; padding: 0; }}
                        
                        table {{ 
                            width: 100%; border-collapse: collapse; 
                            font-family: 'Poppins', sans-serif; 
                            background-color: var(--bg); color: var(--text); 
                        }}
                        th {{ 
                            background: linear-gradient(180deg, var(--header-bg) 0%, #e9ecef 100%); 
                            color: var(--text); 
                            padding: 12px; font-weight: 600; 
                            border-bottom: 2px solid rgba(0,0,0,0.1); 
                            font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;
                        }}
                        td {{ 
                            padding: 12px 8px; text-align: center; 
                            border-bottom: 1px solid rgba(0,0,0,0.05); 
                            font-size: 14px; line-height: 1.5; 
                        }}
                    </style>
                    <table>
                        <thead>
                            <tr>
                                <th>Position</th>
                                <th>Name</th>
                                <th>Class</th>
                                <th>Group</th>
                            </tr>
                        </thead>
                        <tbody>{table_rows_html}</tbody>
                    </table>
                </div>
                """,
                height=350,
            )