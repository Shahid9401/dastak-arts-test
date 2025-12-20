# ================= STUDENT VIEW MODULE =================
# ALOKA DASTAR – Arts Fest
# Hybrid: Old Stable Tables + New Fast Speed

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
    
    # 1. FAST DATA FETCH (Keep this for speed!)
    df, notif_df = fetch_all_student_data()

    # 2. NOTIFICATIONS (Marquee)
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
    # (Restored EXACTLY from your 'student_view old.py')
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

        # Using Pandas to generate HTML (Stable method from old file)
        html_table = leaderboard[["Rank", "Group", "Points"]].to_html(index=False, escape=False)

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
                    /* First place highlight */
                    tr:nth-child(1) {{
                        background:rgba(255,215,0,0.15);
                        font-weight:700;
                        border-left:6px solid #f5b301;
                    }}
                    /* Row Borders */
                    tr{{border-bottom:1px solid rgba(255,215,0,0.15)}}
                </style>
                {html_table}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    
    # ==========================
    # 🎭 EVENT-WISE RESULTS
    # (Using the 4-Column CSS you pasted + Pandas logic)
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

            # Generate basic table HTML
            html_event_table = event_display_df.to_html(index=False, escape=False)

            # Inject into your Custom CSS Container
            components.html(
                f"""
                <div style="overflow-x: hidden; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2);">
                    <style>
                        :root {{ --bg: #ffffff; --text: #1a1a1a; --header-bg: #f8f9fa; }}
                        @media (prefers-color-scheme: dark) {{ :root {{ --bg: #0e1117; --text: #fafafa; --header-bg: #1d2129; }} }}
                        
                        body {{ margin: 0; padding: 0; font-family: sans-serif; }}
                        
                        /* YOUR PASTED CSS (Optimized for Mobile) */
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            table-layout: fixed; /* Fixes width to screen */
                            background-color: var(--bg);
                            color: var(--text);
                        }}
                        
                        th {{
                            background-color: var(--header-bg);
                            color: var(--text);
                            font-weight: bold;
                            text-align: center;
                            padding: 12px 5px;
                            border-bottom: 2px solid rgba(128, 128, 128, 0.3);
                            font-size: 13px;
                        }}
                        
                        td {{
                            text-align: center;
                            padding: 10px 5px;
                            border-bottom: 1px solid rgba(128, 128, 128, 0.1);
                            font-size: 13px;
                            
                            /* WRAPPING LOGIC */
                            white-space: normal;
                            word-wrap: break-word;
                        }}
                        
                        /* SPECIFIC WIDTHS (Matches your 4-column request) */
                        th:nth-child(1) {{ width: 15%; }} /* Pos */
                        th:nth-child(2) {{ width: 35%; text-align: left; padding-left:10px; }} /* Name */
                        td:nth-child(2) {{ text-align: left; padding-left:10px; }}
                        th:nth-child(3) {{ width: 20%; }} /* Class */
                        th:nth-child(4) {{ width: 30%; }} /* Group */

                        /* Gold Highlight for First Place */
                        tbody tr:nth-child(1) {{
                            background-color: rgba(255, 215, 0, 0.2); 
                            font-weight: bold;
                        }}
                    </style>
                    
                    {html_event_table}
                    
                </div>
                """,
                height=400, 
            )