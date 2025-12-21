# ================= STUDENT VIEW MODULE =================
# ALOKA DASTAR – Arts Fest
# Features: Stable Tables + Fast Speed + Clean UI (Nuclear Fix for Toolbar)

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
    
    # --- 1. CLEAN MODE CSS (NUCLEAR OPTION) ---
    st.markdown("""
    <style>
    /* Hide Streamlit Cloud floating buttons (mobile & desktop) */
    [data-testid="stToolbar"] {
        display: none;
    }
    [data-testid="stDecoration"] {
        display: none;
    }
    [data-testid="stStatusWidget"] {
        display: none;
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
    # (Stable Logic)
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

        # Using Pandas to generate HTML (Stable method)
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
    # (Compact View + Stacked Group Names)
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

            # 1. Build rows manually 
            table_rows_html = ""
            for _, row in event_display_df.iterrows():
                is_first = str(row['Position']).strip().lower() == "first"
                row_style = 'style="background-color: rgba(255, 215, 0, 0.25); font-weight: 600;"' if is_first else ""
                
                # --- Stacked Group Name ---
                g_id = row['Group']
                g_name = GROUP_NAMES_ML.get(g_id, "")
                group_html = f"<span>{g_id}</span><br><span style='font-size:0.85em; opacity:0.75;'>{g_name}</span>"

                table_rows_html += f"""
                <tr {row_style}>
                    <td>{row['Position']}</td>
                    <td>{row['Name']}</td>
                    <td>{row['Class']}</td>
                    <td>{group_html}</td>
                </tr>
                """

            import streamlit.components.v1 as components

            # 2. Render with COMPACT CSS
            components.html(
                f"""
                <div style="overflow-x: auto; border-radius: 10px; border: 1px solid rgba(128,128,128,0.2);">
                    <style>
                        :root {{
                            --bg: #ffffff;
                            --text: #1a1a1a;
                            --header-bg: #f8f9fa;
                        }}
                        
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
                            padding: 10px;
                            font-weight: bold;
                            border-bottom: 2px solid rgba(128,128,128,0.3);
                            font-size: 14px;
                        }}
                        td {{
                            padding: 10px 6px;
                            text-align: center;
                            border-bottom: 1px solid rgba(128,128,128,0.1);
                            font-size: 14px;
                            line-height: 1.4;
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