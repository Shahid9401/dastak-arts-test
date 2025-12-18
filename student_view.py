# ================= STUDENT VIEW MODULE =================
# ALOKA DASTAR – Arts Fest
# Polished, read-only student interface

import streamlit as st
import pandas as pd

DATA_FILE = "results.csv"
GROUP_NAMES_ML = {
    "Group 1": "കോച്ചേരി",
    "Group 2": "പാണ്ടിപ്പട",
    "Group 3": "അഞ്ഞൂറ്റി",
    "Group 4": "വടക്കൻ വീട്ടിൽ",
    "Group 5": "അറക്കൽ"
}




def render_student_view():
    import pandas as pd
    from config import DATA_FILE
    df = pd.read_csv(DATA_FILE)
    df_final = df[df["Status"] == "Final"]
    st.markdown(
    """
    <style>
    .fixed-table {
        max-width: 900px;   /* ≈ 24 cm */
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
    )
    st.markdown("""
    <style>
    .marquee {
        background: #fff3cd;
        color: #664d03;
        padding: 10px;
        font-weight: bold;
        overflow: hidden;
        white-space: nowrap;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    .marquee span {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 15s linear infinite;
    }
    @keyframes marquee {
        0%   { transform: translateX(0); }
        100% { transform: translateX(-100%); }
    }
    </style>

    <div class="marquee">
    <span>
        🎭 DASTAK Arts Fest 2025 — Live Results Updating |
        🏆 Overall Points Table Refreshing |
        📢 Stay Tuned for Final Results!
    </span>
    </div>
    """, unsafe_allow_html=True)

    # ---- rest of student view UI below ----
    # ---------- OVERALL POINT TABLE ----------
# ---------- OVERALL POINT TABLE ----------
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
                    /* First place highlight – mode safe */
                    tr:nth-child(1) {{
                        background:rgba(255,215,0,0.15);
                        font-weight:700
                        border-left:6px solid #f5b301;
                    }}
                    /* Row Borders for clarity*/
                    tr{{border-bottom:1px solid rgba(255,215,0,0.15)}}
                </style>
                {html_table}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    
    # ---------- EVENT-WISE RESULTS ----------
    if not df_final.empty:

        st.markdown("---")
        st.subheader("🎭 Event-wise Results")

        event_filter = st.selectbox(
            "Select an event to view results",
            options=["-- Select Event --"] + sorted(df_final["Event"].unique().tolist())
        )

        if event_filter != "-- Select Event --":
            event_df = df_final[df_final["Event"] == event_filter]
            event_display_df = event_df[["Position", "Name", "Class", "Group"]]

            # 1. Build rows manually to avoid the 'Double Header' issue
            table_rows_html = ""
            for _, row in event_display_df.iterrows():
                # Highlight First Place with a subtle gold
                is_first = str(row['Position']).strip().lower() == "first"
                row_style = 'style="background-color: rgba(255, 215, 0, 0.25); font-weight: 600;"' if is_first else ""
                
                table_rows_html += f"""
                <tr {row_style}>
                    <td>{row['Position']}</td>
                    <td>{row['Name']}</td>
                    <td>{row['Class']}</td>
                    <td>{row['Group']}</td>
                </tr>
                """

            import streamlit.components.v1 as components

            # 2. Render with THEME-AWARE CSS
            components.html(
                f"""
                <div style="overflow-x: auto; border-radius: 10px; border: 1px solid rgba(128,128,128,0.2);">
                    <style>
                        :root {{
                            --bg: #ffffff;
                            --text: #1a1a1a;
                            --header-bg: #f8f9fa;
                        }}
                        
                        /* This detects if the user's phone is in Dark Mode */
                        @media (prefers-color-scheme: dark) {{
                            :root {{
                                --bg: #0e1117;
                                --text: #fafafa;
                                --header-bg: #1d2129;
                            }}
                        }}

                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            font-family: -apple-system, system-ui, sans-serif;
                            background-color: var(--bg);
                            color: var(--text);
                        }}
                        th {{
                            background-color: var(--header-bg);
                            color: var(--text);
                            padding: 12px;
                            font-weight: bold;
                            border-bottom: 2px solid rgba(128,128,128,0.3);
                        }}
                        td {{
                            padding: 12px 8px;
                            text-align: center;
                            border-bottom: 1px solid rgba(128,128,128,0.1);
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
                        <tbody>
                            {table_rows_html}
                        </tbody>
                    </table>
                </div>
                """,
                height=350,
            )