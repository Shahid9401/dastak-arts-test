# ================= STUDENT VIEW MODULE =================
# ALOKA DASTAR – Arts Fest
# Ultimate Mobile View: Merged Columns for Clean Layout

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
    
    # 1. FETCH DATA
    df, notif_df = fetch_all_student_data()

    # 2. RENDER NOTIFICATIONS
    if not notif_df.empty:
        latest_msgs = notif_df.head(5)["Message"].astype(str).tolist()
        running_text = "  🔸  ".join(latest_msgs)

        st.markdown(
            f"""
            <div style="
                background:#fff3cd;
                padding:12px 0;
                border-radius:8px;
                margin-bottom:18px;
                font-size:18px;
                font-weight:600;
                color:#7a5c00;
                overflow:hidden;
                white-space:nowrap;
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
    # 🏆 OVERALL POINT TABLE
    # ==========================
    st.subheader("🏆 Overall Point Table")

    if df_final.empty:
        st.info("🎭 Results will appear here once events are finalized. Please check back soon.")
    else:
        # Calculate scores
        leaderboard = (
            df_final.groupby("Group")["Points"]
            .sum()
            .reset_index()
            .sort_values(by="Points", ascending=False)
        )
        leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))

        # Build HTML Rows
        table_rows_html = ""
        for _, row in leaderboard.iterrows():
            rank = row["Rank"]
            group_key = row["Group"]
            points = row["Points"]
            
            group_display = f"{group_key} – {GROUP_NAMES_ML.get(group_key, '')}"

            if rank == 1: rank_display = "🥇 1st"
            elif rank == 2: rank_display = "🥈 2nd"
            elif rank == 3: rank_display = "🥉 3rd"
            else: rank_display = f"{rank}th"

            # Style for Top 3
            row_style = ""
            if rank == 1:
                row_style = 'style="background-color: rgba(255, 215, 0, 0.2); font-weight: bold; border-left: 5px solid #ffc107;"'
            
            table_rows_html += f"""
            <tr {row_style}>
                <td class="col-rank">{rank_display}</td>
                <td class="col-group">{group_display}</td>
                <td class="col-points">{points}</td>
            </tr>
            """

        # Render Table
        components.html(
            f"""
            <div style="overflow-x: hidden; border-radius: 10px; border: 1px solid rgba(128,128,128,0.2);">
                <style>
                    :root {{ --bg: #ffffff; --text: #1a1a1a; --header-bg: #f8f9fa; }}
                    @media (prefers-color-scheme: dark) {{ :root {{ --bg: #0e1117; --text: #fafafa; --header-bg: #1d2129; }} }}
                    
                    body {{ margin: 0; padding: 0; font-family: sans-serif; }}
                    
                    table {{ 
                        width: 100%; 
                        table-layout: fixed; 
                        border-collapse: collapse; 
                        background-color: var(--bg); 
                        color: var(--text); 
                    }}
                    
                    th {{ 
                        background-color: var(--header-bg); 
                        color: var(--text); 
                        padding: 12px 5px;
                        font-weight: bold; 
                        border-bottom: 2px solid rgba(128,128,128,0.3);
                        font-size: 13px;
                        text-transform: uppercase;
                        text-align: center;
                    }}
                    
                    td {{ 
                        padding: 10px 5px; 
                        border-bottom: 1px solid rgba(128,128,128,0.1); 
                        font-size: 13px;
                        white-space: normal; 
                        word-wrap: break-word;
                        vertical-align: middle;
                        text-align: center;
                    }}

                    /* COLUMN WIDTHS */
                    .col-rank {{ width: 15%; }}
                    .col-group {{ width: 65%; text-align: left; padding-left: 10px; }}
                    .col-points {{ width: 20%; font-weight: bold; }}
                    
                </style>
                <table>
                    <thead>
                        <tr>
                            <th class="col-rank">Rank</th>
                            <th class="col-group">Group</th>
                            <th class="col-points">Pts</th>
                        </tr>
                    </thead>
                    <tbody>{table_rows_html}</tbody>
                </table>
            </div>
            """,
            height=320,
        )

    st.markdown("---")
    
    # ==========================
    # 🎭 EVENT-WISE RESULTS (MERGED COLUMNS)
    # ==========================
    if not df_final.empty:
        st.subheader("🎭 Event-wise Results")

        event_filter = st.selectbox(
            "Select an event to view results",
            options=["-- Select Event --"] + sorted(df_final["Event"].unique().tolist())
        )

        if event_filter != "-- Select Event --":
            event_df = df_final[df_final["Event"] == event_filter]
            event_display_df = event_df[["Position", "Name", "Class", "Group"]]

            table_rows_html = ""
            for _, row in event_display_df.iterrows():
                is_first = str(row['Position']).strip().lower() == "first"
                row_style = 'style="background-color: rgba(255, 215, 0, 0.25); font-weight: bold;"' if is_first else ""
                
                # --- MERGE LOGIC ---
                # We combine Class and Group into one cell
                # Format: "BCom CA <br> Group 5"
                details_html = f"""
                <span style="font-weight:600; font-size:13px;">{row['Class']}</span><br>
                <span style="font-size:11px; opacity:0.8;">{row['Group']}</span>
                """

                table_rows_html += f"""
                <tr {row_style}>
                    <td class="col-pos">{row['Position']}</td>
                    <td class="col-name">{row['Name']}</td>
                    <td class="col-details">{details_html}</td>
                </tr>
                """

            components.html(
                f"""
                <div style="overflow-x: hidden; border-radius: 10px; border: 1px solid rgba(128,128,128,0.2);">
                    <style>
                        :root {{ --bg: #ffffff; --text: #1a1a1a; --header-bg: #f8f9fa; }}
                        @media (prefers-color-scheme: dark) {{ :root {{ --bg: #0e1117; --text: #fafafa; --header-bg: #1d2129; }} }}
                        body {{ margin: 0; padding: 0; font-family: sans-serif; }}
                        
                        table {{ 
                            width: 100%; 
                            table-layout: fixed; 
                            border-collapse: collapse; 
                            background-color: var(--bg); 
                            color: var(--text);
                        }}
                        
                        th {{ 
                            background-color: var(--header-bg); 
                            padding: 10px 4px; 
                            font-weight: bold; 
                            border-bottom: 2px solid rgba(128,128,128,0.3); 
                            font-size: 12px; 
                            text-align: center;
                        }}
                        
                        td {{ 
                            padding: 8px 6px; 
                            text-align: center; 
                            border-bottom: 1px solid rgba(128,128,128,0.1); 
                            font-size: 13px; 
                            white-space: normal;
                            word-wrap: break-word;
                            vertical-align: middle;
                        }}
                        
                        /* === OPTIMIZED 3-COLUMN LAYOUT === */
                        .col-pos {{ width: 15%; font-weight:bold; }}
                        
                        /* Name gets 50% width! Huge space improvement */
                        .col-name {{ width: 50%; text-align: left; padding-left: 10px; font-size: 14px; }} 
                        
                        .col-details {{ width: 35%; line-height: 1.2; }}
                        
                        /* Header Alignment matches Data */
                        th:nth-child(2) {{ text-align: left; padding-left: 10px; }}
                        
                    </style>
                    <table>
                        <thead>
                            <tr>
                                <th>Pos</th>
                                <th>Name</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>{table_rows_html}</tbody>
                    </table>
                </div>
                """,
                height=350,
            )