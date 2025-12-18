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

            html_event_table = event_display_df.to_html(
                index=False,
                header=False,
                escape=False
            )

            import streamlit.components.v1 as components

            components.html(
                f"""
                <div style="overflow-x: auto; max-width: 100%; border-radius: 8px;">
                    <style>
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            table-layout: auto; /* Changed to auto for better mobile fitting */
                            font-family: sans-serif;
                            color: var(--text-color, #31333F); /* Fallback to Streamlit default dark text */
                            background-color: var(--background-color, #ffffff);
                        }}
                        th {{
                            background-color: rgba(128, 128, 128, 0.15); /* Subtle grey that works in both modes */
                            color: var(--text-color);
                            font-weight: bold;
                            text-align: center;
                            padding: 12px 8px;
                            border-bottom: 2px solid rgba(128, 128, 128, 0.3);
                        }}
                        td {{
                            text-align: center;
                            padding: 10px 8px;
                            color: var(--text-color);
                            border-bottom: 1px solid rgba(128, 128, 128, 0.1);
                        }}
                        
                        /* First place highlight - Gold with low opacity */
                        tbody tr:nth-child(1) {{
                            background-color: rgba(255, 215, 0, 0.2); 
                            font-weight: 600;
                        }}
                        /* Ensuring text stays visible in Dark Mode */
                        @media (prefers-color-scheme: dark) {{
                            table {{
                                color: #fafafa;
                            }}
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
                            {html_event_table} 
                        </tbody>
                    </table>
                </div>
                """,
                height=400, # Adjust height based on your needs
            )
