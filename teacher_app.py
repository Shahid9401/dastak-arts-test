# ================= ALOKA DASTAK – ARTS FEST RESULT & POINT TABLE APP =================
import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os
import time
from config import (
    TEACHER_USERNAME,
    TEACHER_PASSWORD,
    GROUPS,
    OFF_STAGE_EVENTS,
    ON_STAGE_EVENTS
)
from pdf_generator import generate_event_pdf
from sheet_utils import read_results, write_results, add_notification

# ---------------- 1. PAGE CONFIG ----------------
st.set_page_config(page_title="DASTAK Arts Festival 2026", layout="wide")

# [NEW] CUSTOM CSS TO BOOST FONT SIZES
st.markdown("""
<style>
    /* Make the Expander Header ("Tap to Select...") Larger & Bolder */
    div[data-testid="stExpander"] summary p {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    /* Optional: Make the Radio Button options slightly larger too */
    div[role="radiogroup"] label p {
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- 2. CONFIGURATION ----------------
LOGO_FILE = "arts_logo.jpg" 

POINTS = {"First": 5, "Second": 3, "Third": 1}

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

# ---------------- 3. SESSION STATE ----------------
if "role" not in st.session_state: st.session_state.role = None
if "just_finalized" not in st.session_state: st.session_state.just_finalized = False
if "winners" not in st.session_state: st.session_state.winners = {"First": [], "Second": [], "Third": []}
if "menu_reset_token" not in st.session_state: st.session_state.menu_reset_token = 0

def force_close_menu():
    st.session_state.menu_reset_token += 1

# ---------------- 4. LOGIN SCREEN ----------------
if st.session_state.role is None:
    def get_base64_image(image_path):
        if not os.path.exists(image_path): return ""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    img_b64 = get_base64_image(LOGO_FILE)
    
    col1, col2, col3 = st.columns([1, 6, 1]) 
    with col2:
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 20px;">
                <div style="background-color: white; padding: 15px; border-radius: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-bottom: 20px;">
                    <img src="data:image/png;base64,{img_b64}" style="width: 140px; display: block;">
                </div>
                <h3 style="margin: 0; text-align: center; font-size: 22px;">ASSABAH ARTS & SCIENCE COLLEGE</h3>
                <h5 style="color: #B08D57; margin-top: 8px; font-weight: bold; text-align: center;">✨ DASTAK ARTS FESTIVAL 2026 ✨</h5>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("") 
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; margin: 0;'>🔐 Staff Login</h4>", unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="ID", label_visibility="collapsed")
            p = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
            st.write("") 
            if st.button("Login", type="primary", use_container_width=True):
                if u == TEACHER_USER and p == TEACHER_PASS:
                    st.session_state.role = "teacher"
                    st.rerun()
                elif u == ADMIN_USER and p == ADMIN_PASS:
                    st.session_state.role = "admin"
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials")
    st.stop()

# ---------------- 5. MAIN APP ----------------
DATA_FILE = "results.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Timestamp", "Event", "Position", "Name", "Semester", "Class", "Group", "Points", "Status"]).to_csv(DATA_FILE, index=False)

# --- SIDEBAR ---
if st.session_state.role == "teacher":
    with st.sidebar:
        if os.path.exists(LOGO_FILE):
            # [NEW] Full Width Logo: Removed columns so it fills the sidebar
            st.image(LOGO_FILE, use_container_width=True)
        
        st.markdown("<h3 style='text-align: center; color: #B08D57; margin-bottom:0;'>Teacher Panel</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.expander("📖 Guide: Joint Winners", expanded=False):
            st.markdown("""
            **For Group Items:**
            1. **Start a Team:** Click **➕ Add New Team**.
            2. **Add Members:** Click **Add Member**.
            3. **Joint Winners:** Click **➕ Add New Team** again.
            """)
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.role = None
            st.rerun()

# --- TEACHER PANEL LOGIC ---
if st.session_state.role == "teacher":
    
    # CENTERED HEADER
    st.markdown(
        """
        <div style='text-align: center; padding-bottom: 20px;'>
            <h1 style='color: #002147; margin-bottom: 5px; font-size: 2.5rem;'>✨ DASTAK ARTS FESTIVAL 2026 ✨</h1>
            <h4 style='color: #666; font-weight: normal; margin-top: 0;'>Welcome to the Result Entry Portal</h4>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    event_type = st.radio("Select Event Type", ["Off-stage", "On-stage"], horizontal=True)
    tab1, tab2 = st.tabs(["📝 Result Entry", "📊 Overall Point Table"])
    
    # -------- TAB 1: RESULT ENTRY --------
    with tab1:
        reset_suffix = "\u200b" * st.session_state.menu_reset_token

        if event_type == "Off-stage":
            event_options = ["--Select Event--"] + OFF_STAGE_EVENTS
            with st.expander(f"🔻 Tap to Select Off-stage Event{reset_suffix}", expanded=False):
                event_name = st.radio(
                    "Select Event", 
                    event_options, 
                    label_visibility="collapsed",
                    on_change=force_close_menu
                )
            if event_name != "--Select Event--":
                st.info(f"Selected: **{event_name}**")
            onstage_category = "Individual" 

        else:
            event_options = ["--Select Event--"] + ON_STAGE_EVENTS
            with st.expander(f"🔻 Tap to Select On-stage Event{reset_suffix}", expanded=False):
                event_name = st.radio(
                    "Select Event", 
                    event_options, 
                    label_visibility="collapsed",
                    on_change=force_close_menu
                )
            if event_name != "--Select Event--":
                st.info(f"Selected: **{event_name}**")
            onstage_category = st.radio("Select Category", ["Individual", "Group"], horizontal=True)

        # Reset Logic
        if "last_onstage_category" not in st.session_state:
            st.session_state.last_onstage_category = onstage_category
        if st.session_state.last_onstage_category != onstage_category:
            st.session_state.winners = {"First": [], "Second": [], "Third": []}
            st.session_state.last_onstage_category = onstage_category

        if event_name == "--Select Event--" or event_name == "-- Select Event --":
            st.warning("👆 Please select an event above to start.")
            st.stop()

        # CHECK IF FINALIZED
        df_check = read_results()
        df_check["Status"] = df_check["Status"].astype(str).str.strip().str.lower()
        df_check["Event"] = df_check["Event"].astype(str).str.strip()
        is_locked = not df_check[(df_check["Event"] == event_name) & (df_check["Status"] == "final")].empty

        if is_locked:
            st.warning(f"🔒 Event '{event_name}' is Finalized. Editing is disabled.")
            st.subheader("🖨️ Downloads & Certificates")
            col1, col2 = st.columns(2)
            final_df = df_check[(df_check["Event"] == event_name) & (df_check["Status"] == "final")]
            
            pdf_file = generate_event_pdf(event_name, final_df)
            with open(pdf_file, "rb") as f:
                col1.download_button("📄 Download Result List", f, file_name=os.path.basename(pdf_file), mime="application/pdf")

            if col2.button("🎓 Generate Certificates"):
                from certificate_generator import generate_certificates_for_event
                with st.spinner("Generating..."):
                    result_msg = generate_certificates_for_event(event_name, source_df=df_check)
                    if "✅" in result_msg:
                        st.session_state['last_cert_file'] = result_msg.split(": ")[-1].strip()
                        st.success("Ready!")
                    else:
                        st.error(result_msg)

            if 'last_cert_file' in st.session_state and os.path.exists(st.session_state['last_cert_file']):
                with open(st.session_state['last_cert_file'], "rb") as f:
                    col2.download_button("📥 Download Certificates", f, file_name="Certificates.pdf", mime="application/pdf")
            st.stop() 

        # DATA ENTRY FORM
        def add_winner(pos, is_new_team=False):
            st.session_state.winners[pos].append({
                "Name": "", "Semester": "", "Class": "",
                "Group": list(GROUPS.keys())[0],
                "is_new_team": is_new_team 
            })

        for pos in ["First", "Second", "Third"]:
            st.markdown(f"### {pos} Place <span style='font-size:0.8em; color:grey'>({POINTS[pos]} pts)</span>", unsafe_allow_html=True)
            c_btn1, c_btn2, c_space = st.columns([1.5, 1.5, 3])
            
            if onstage_category == "Group":
                if c_btn1.button(f"➕ Add New Team", key=f"add_team_{pos}"): add_winner(pos, is_new_team=True)
                if len(st.session_state.winners[pos]) > 0:
                    if c_btn2.button(f"➕ Add Member", key=f"add_mem_{pos}"): add_winner(pos, is_new_team=False)
            else:
                if c_btn1.button(f"➕ Add Winner", key=f"add_{pos}"): add_winner(pos, is_new_team=True)

            current_group_context = None 
            for i, w in enumerate(st.session_state.winners[pos]):
                c1, c2, c3, c4, c5 = st.columns([3, 1.5, 2, 3, 1])
                is_leader = (i == 0) or w.get("is_new_team", False)
                label = "Team Leader / Winner" if is_leader else f"Member"
                
                w["Name"] = c1.text_input(label, key=f"{pos}_nm_{i}", placeholder="Name")
                w["Semester"] = c2.text_input("Sem", key=f"{pos}_sm_{i}")
                w["Class"] = c3.text_input("Class", key=f"{pos}_cl_{i}")
                
                if onstage_category == "Group":
                    if is_leader:
                        group_display = c4.selectbox("Select Group", list(GROUP_DISPLAY.values()), index=list(GROUP_DISPLAY.keys()).index(w["Group"]), key=f"{pos}_gp_{i}")
                        selected_group = [k for k, v in GROUP_DISPLAY.items() if v == group_display][0]
                        w["Group"] = selected_group
                        current_group_context = selected_group 
                    else:
                        if current_group_context:
                            w["Group"] = current_group_context
                            c4.info(f"Team: {GROUP_DISPLAY[current_group_context]}")
                        else:
                            c4.warning("⚠️ No Team Leader!")
                else:
                    group_display = c4.selectbox("Group", list(GROUP_DISPLAY.values()), index=list(GROUP_DISPLAY.keys()).index(w["Group"]), key=f"{pos}_gp_{i}")
                    w["Group"] = [k for k, v in GROUP_DISPLAY.items() if v == group_display][0]

                if c5.button("❌", key=f"del_{pos}_{i}"):
                    st.session_state.winners[pos].pop(i)
                    st.rerun()
            
            if onstage_category == "Group" and len(st.session_state.winners[pos]) > 0: st.markdown("---")

        def save_results(status):
            status = status.strip().lower()
            df = read_results()
            if not df.empty: df = df[df["Event"] != event_name]
            rows = []
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for pos, winners in st.session_state.winners.items():
                for i, w in enumerate(winners):
                    if w["Name"].strip() == "": continue
                    is_leader_row = (i == 0) or w.get("is_new_team", False)
                    current_points = POINTS[pos] if is_leader_row else 0
                    rows.append({
                        "Timestamp": ts, "Event": event_name, "Position": pos,
                        "Name": w["Name"], "Semester": w.get("Semester", ""),
                        "Class": w.get("Class", ""), "Group": w["Group"],
                        "Points": current_points, "Status": status,
                    })

            if rows:
                df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
                write_results(df)
                st.success(f"Results saved as {status}")
                st.cache_data.clear()

        c1, c2 = st.columns(2)
        if c1.button("💾 Save Draft"): save_results("draft")

        if c2.button("🔒 Finalize"):
            save_results("final")
            df = read_results()
            df.loc[df["Event"] == event_name, "Status"] = "final"
            write_results(df)
            st.session_state.just_finalized = True
            st.cache_data.clear()
            st.success("✅ Finalized!")
            time.sleep(1)
            st.rerun()

    # -------- TAB 2: POINT TABLE --------
    with tab2:
        df = read_results()
        df["Status"] = df["Status"].astype(str).str.strip().str.lower()
        final_df = df[df["Status"] == "final"]
        if not final_df.empty:
            leaderboard = final_df.groupby("Group")["Points"].sum().reset_index().sort_values(by="Points", ascending=False)
            leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))
            leaderboard["Group"] = leaderboard["Group"].apply(lambda g: f"{g} – {GROUP_NAMES_ML.get(g, '')}")
            st.table(leaderboard)