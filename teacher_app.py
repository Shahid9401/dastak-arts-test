# ================= ALOKA DASTAK – ARTS FEST RESULT & POINT TABLE APP =================
# FINAL VERSION: Supports Joint Winners (Multiple Groups in same Position)

import streamlit as st
import pandas as pd
from datetime import datetime
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
from header import render_header

# --- CONFIGURATION ---
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

# --- SESSION STATE ---
# ================= LOGIN =================
if st.session_state.role is None:
    # 1. Create 3 columns to center the content (Left, Middle, Right)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # --- HEADER SECTION ---
        # Display Logo (Centered)
        if os.path.exists("logo.png"):
            # This trick centers the image using mini-columns inside the middle column
            l, m, r = st.columns([1, 2, 1]) 
            with m:
                st.image("logo.png", use_container_width=True)
        
        # Styled Title using HTML for custom colors
        st.markdown(
            """
            <div style='text-align: center;'>
                <h2 style='color: #002147; margin-bottom: 0;'>ASSABAH ARTS & SCIENCE COLLEGE</h2>
                <h4 style='color: #B08D57; margin-top: 5px;'>✨ DASTAK ARTS FESTIVAL 2026 ✨</h4>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.write("") # Spacer
        
        # --- LOGIN FORM (Inside a Box) ---
        # border=True creates a nice outline around the login form
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>🔐 Staff Login</h3>", unsafe_allow_html=True)
            
            u = st.text_input("Username", placeholder="Enter your ID")
            p = st.text_input("Password", type="password", placeholder="Enter your password")
            
            st.write("") # Spacer
            
            # Make the button span the full width
            if st.button("Login", type="primary", use_container_width=True):
                if u == TEACHER_USER and p == TEACHER_PASS:
                    st.session_state.role = "teacher"
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                elif u == ADMIN_USER and p == ADMIN_PASS:
                    st.session_state.role = "admin"
                    st.success("Admin login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password")
        
        # --- FOOTER ---
        st.markdown(
            "<p style='text-align: center; color: grey; font-size: 12px; margin-top: 20px;'>© 2026 Dept of Physics | Valayamkulam</p>", 
            unsafe_allow_html=True
        )

    st.stop()
# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="DASTAK Arts Festival 2025 – Admin", layout="wide")
if st.session_state.role is None:
    render_header(compact=True)
else:
    render_header()

# ---------------- DATA INIT ----------------
DATA_FILE = "results.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "Timestamp", "Event", "Position", "Name",
        "Semester", "Class", "Group", "Points", "Status"
    ]).to_csv(DATA_FILE, index=False)

# ================= SIDEBAR INSTRUCTIONS =================
if st.session_state.role == "teacher":
    st.sidebar.markdown("### 👨‍🏫 Teacher Panel")
    
    with st.sidebar.expander("📖 Guide: Joint Winners", expanded=False):
        st.markdown("""
        **For Group Items:**
        1. **Start a Team:** Click **➕ Add New Team**. Select the Group (e.g., Group 1).
        2. **Add Members:** Click **Add Member** to add more students to *that specific group*.
        3. **Joint Winners:** If another group (e.g., Group 2) *also* won First:
           - Click **➕ Add New Team** *again*.
           - Select "Group 2".
           - Add members for them.
        
        **Points:**
        - Each "Team" entry gets the full points (5, 3, or 1).
        - Extra members do not multiply the points.
        """)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.role = None
        st.rerun()

# ================= LOGIN =================
if st.session_state.role is None:
    st.subheader("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == TEACHER_USER and p == TEACHER_PASS:
            st.session_state.role = "teacher"
            st.success("Teacher login successful")
            st.rerun()
        elif u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.role = "admin"
            st.success("Admin login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# ================= MAIN APP =================
else:
    if st.session_state.role == "teacher":
        st.success("Welcome, Arts Festival Coordinator 🎭")

        event_type = st.radio("Select Event Type", ["Off-stage", "On-stage"], horizontal=True)
        tab1, tab2 = st.tabs(["📝 Result Entry", "📊 Overall Point Table"])
        
        # -------- TAB 1: RESULT ENTRY --------
        with tab1:
            if event_type == "Off-stage":
                event_list = OFF_STAGE_EVENTS
                event_options = ["--Select Event--"] + OFF_STAGE_EVENTS
                event_name = st.selectbox("Off-stage Event", event_options)
                onstage_category = "Individual" 
            else:
                event_list = ON_STAGE_EVENTS
                event_name = st.selectbox("On-stage Event", ["--Select Event--"] + ON_STAGE_EVENTS)
                onstage_category = st.radio("Select Category", ["Individual", "Group"], horizontal=True)

            # Reset on category switch
            if "last_onstage_category" not in st.session_state:
                st.session_state.last_onstage_category = onstage_category

            if st.session_state.last_onstage_category != onstage_category:
                st.session_state.winners = {"First": [], "Second": [], "Third": []}
                st.session_state.last_onstage_category = onstage_category

            if event_name == "-- Select Event --":
                st.info("ℹ️ Please select an event.")
                st.stop()

            # ... (after event_name selection) ...

            # [FIX] CHECK IF ALREADY FINALIZED
            df_check = read_results()
            df_check["Status"] = df_check["Status"].astype(str).str.strip().str.lower()
            df_check["Event"] = df_check["Event"].astype(str).str.strip()
            
            # Check if this event is locked
            is_locked = not df_check[(df_check["Event"] == event_name) & (df_check["Status"] == "final")].empty

            if is_locked:
                st.warning(f"🔒 Event '{event_name}' is Finalized. Editing is disabled.")
                st.subheader("🖨️ Downloads & Certificates")
                
                col1, col2 = st.columns(2)
                
                # 1. DOWNLOAD LIST
                final_df = df_check[(df_check["Event"] == event_name) & (df_check["Status"] == "final")]
                pdf_file = generate_event_pdf(event_name, final_df)
                
                with open(pdf_file, "rb") as f:
                    col1.download_button("📄 Download Result List", f, file_name=os.path.basename(pdf_file), mime="application/pdf")

                # 2. GENERATE CERTIFICATES
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
                
                # STOP HERE so the inputs and save buttons don't show
                st.stop() 

            # ... (The rest of your code: "winners" init, inputs, etc.) ...

            if "winners" not in st.session_state:
                st.session_state.winners = {"First": [], "Second": [], "Third": []}

            # UPDATED ADD FUNCTION: Handles "New Team" flag
            def add_winner(pos, is_new_team=False):
                st.session_state.winners[pos].append({
                    "Name": "", "Semester": "", "Class": "",
                    "Group": list(GROUPS.keys())[0],
                    "is_new_team": is_new_team # Flag to identify Team Leaders
                })

            # --- INPUT LOOP ---
            for pos in ["First", "Second", "Third"]:
                st.markdown(f"### {pos} Place <span style='font-size:0.8em; color:grey'>({POINTS[pos]} pts)</span>", unsafe_allow_html=True)
                
                # BUTTON LOGIC
                c_btn1, c_btn2, c_space = st.columns([1.5, 1.5, 3])
                
                if onstage_category == "Group":
                    # Button 1: Start a BRAND NEW Group (Joint Winner)
                    if c_btn1.button(f"➕ Add New Team", key=f"add_team_{pos}"):
                        add_winner(pos, is_new_team=True)
                    
                    # Button 2: Add member to the LAST added group
                    if len(st.session_state.winners[pos]) > 0:
                        if c_btn2.button(f"➕ Add Member", key=f"add_mem_{pos}"):
                            add_winner(pos, is_new_team=False)
                    elif len(st.session_state.winners[pos]) == 0:
                        # If list is empty, 'Add Member' should act like 'Add Team'
                        pass 
                else:
                    if c_btn1.button(f"➕ Add Winner", key=f"add_{pos}"):
                        add_winner(pos, is_new_team=True)

                # RENDER ROWS
                current_group_context = None # Tracks the group of the current 'Team' block
                
                for i, w in enumerate(st.session_state.winners[pos]):
                    c1, c2, c3, c4, c5 = st.columns([3, 1.5, 2, 3, 1])
                    
                    # Logic to identify if this row is a "Team Leader"
                    # It is a leader if: It's the first row (i=0) OR it has the 'is_new_team' flag
                    is_leader = (i == 0) or w.get("is_new_team", False)
                    
                    # Name Input
                    label = "Team Leader / Winner" if is_leader else f"Member"
                    w["Name"] = c1.text_input(label, key=f"{pos}_nm_{i}", placeholder="Student Name")
                        
                    w["Semester"] = c2.text_input("Sem", key=f"{pos}_sm_{i}")
                    w["Class"] = c3.text_input("Class", key=f"{pos}_cl_{i}")
                    
                    # GROUP SELECTION
                    if onstage_category == "Group":
                        if is_leader:
                            # This row STARTS a group. Show SelectBox.
                            group_display = c4.selectbox(
                                "Select Group",
                                list(GROUP_DISPLAY.values()),
                                index=list(GROUP_DISPLAY.keys()).index(w["Group"]),
                                key=f"{pos}_gp_{i}"
                            )
                            # Update the row's group
                            selected_group = [k for k, v in GROUP_DISPLAY.items() if v == group_display][0]
                            w["Group"] = selected_group
                            current_group_context = selected_group # Set context for following members
                        else:
                            # This row FOLLOWS a group. Inherit from context.
                            if current_group_context:
                                w["Group"] = current_group_context
                                c4.info(f"Team: {GROUP_DISPLAY[current_group_context]}")
                            else:
                                c4.warning("⚠️ No Team Leader above!")
                    else:
                        # Individual Item - Always selectable
                        group_display = c4.selectbox(
                            "Group", list(GROUP_DISPLAY.values()),
                            index=list(GROUP_DISPLAY.keys()).index(w["Group"]),
                            key=f"{pos}_gp_{i}"
                        )
                        w["Group"] = [k for k, v in GROUP_DISPLAY.items() if v == group_display][0]

                    if c5.button("❌", key=f"del_{pos}_{i}"):
                        st.session_state.winners[pos].pop(i)
                        st.rerun()
                
                # Visual divider if multiple teams exist in one position
                if onstage_category == "Group" and len(st.session_state.winners[pos]) > 0:
                    st.markdown("---")

            # --- SAVE FUNCTION (UPDATED) ---
            def save_results(status):
                status = status.strip().lower()
                df = read_results()
                
                # [FIX] 1. Remove OLD entries for this specific event to prevent duplicates
                if not df.empty:
                    df = df[df["Event"] != event_name]
                
                rows = []
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for pos, winners in st.session_state.winners.items():
                    for i, w in enumerate(winners):
                        if w["Name"].strip() == "": continue
                        
                        # Joint Winner Point Logic
                        is_leader_row = (i == 0) or w.get("is_new_team", False)
                        current_points = POINTS[pos] if is_leader_row else 0

                        rows.append({
                            "Timestamp": ts, "Event": event_name, "Position": pos,
                            "Name": w["Name"], "Semester": w.get("Semester", ""),
                            "Class": w.get("Class", ""), "Group": w["Group"],
                            "Points": current_points, "Status": status,
                        })

                if rows:
                    # [FIX] 2. Concat the CLEANED df with the NEW rows
                    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
                    write_results(df)
                    
                    if status == "draft":
                         # Optional: Clear inputs after draft save, or keep them? 
                         # Usually better to keep them in session if just drafting.
                         pass 
                         
                    st.success(f"Results saved as {status}")
                    st.cache_data.clear()

            c1, c2 = st.columns(2)
            if c1.button("💾 Save Draft"): save_results("draft")

            if c2.button("🔒 Finalize"):
                df = read_results()
                df["Status"] = df["Status"].astype(str).str.strip().str.lower()
                mask = (df["Event"] == event_name) & (df["Status"] != "final")
                
                # Logic to prevent double finalizing is handled by UI check below
                # Just mark 'final'
                df.loc[df["Event"] == event_name, "Status"] = "final"
                
                final_df_for_pdf = df[df["Event"] == event_name].copy()
                try:
                    pdf_file = generate_event_pdf(event_name, final_df_for_pdf)
                    st.session_state['generated_pdf'] = pdf_file
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")

                write_results(df)
                st.session_state.just_finalized = True
                st.cache_data.clear()
                st.success("✅ Finalized!")
                time.sleep(1)
                add_notification("FINAL", f"Results declared for {event_name}", event_name)
                st.rerun()

            # --- PDF DOWNLOAD ---
            df = read_results()
            df["Status"] = df["Status"].astype(str).str.strip().str.lower()
            df["Event"] = df["Event"].astype(str).str.strip()
            is_final = not df[(df["Event"] == event_name) & (df["Status"] == "final")].empty
            
            # ... (Inside teacher_app.py, scroll to the 'if is_final:' block) ...
            
            if is_final:
                st.markdown("---")
                st.subheader("🖨️ Downloads & Certificates")
                
                col1, col2 = st.columns(2)
                
                # --- 1. RESULT LIST PDF ---
                final_df = df[(df["Event"] == event_name) & (df["Status"] == "final")]
                
                # Check for existing PDF or generate new one
                if 'generated_pdf' in st.session_state and st.session_state.just_finalized:
                    pdf_file = st.session_state['generated_pdf']
                else:
                    pdf_file = generate_event_pdf(event_name, final_df)
                
                if os.path.exists(pdf_file):
                    with open(pdf_file, "rb") as f:
                        col1.download_button(
                            "📄 Download Result List", 
                            f, 
                            file_name=pdf_file.split(os.sep)[-1], 
                            mime="application/pdf"
                        )

                # --- 2. CERTIFICATES ---
                # This button triggers the import and generation
                # ... inside teacher_app.py ...

                # --- 2. CERTIFICATES ---
                if col2.button("🎓 Generate Certificates"):
                    from certificate_generator import generate_certificates_for_event
                    
                    with st.spinner("Generating certificates..."):
                        try:
                            # PASS THE DATAFRAME DIRECTLY HERE 👇
                            # We use 'df' (the full dataframe) or 'final_df' (the filtered one)
                            # Passing 'df' is safer as the function filters it again.
                            result_msg = generate_certificates_for_event(event_name, source_df=df)
                            
                            if "✅" in result_msg:
                                cert_file = result_msg.split(": ")[-1].strip()
                            else:
                                cert_file = result_msg

                            if cert_file.endswith(".pdf") and os.path.exists(cert_file):
                                st.session_state['last_cert_file'] = cert_file
                                st.success("✅ Certificates Ready!")
                            else:
                                st.error(result_msg)
                                
                        except Exception as e:
                            st.error(f"Error: {e}")

                # Show Download Button if a certificate exists in session
                if 'last_cert_file' in st.session_state:
                    # Security check: Ensure the file belongs to the CURRENT event
                    current_safe_name = event_name.replace(" ", "_").replace("/", "-")
                    
                    if current_safe_name in st.session_state['last_cert_file']:
                        path = st.session_state['last_cert_file']
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                col2.download_button(
                                    "📥 Download All Certificates",
                                    f,
                                    file_name=path,
                                    mime="application/pdf"
                                )
        with tab2:
            # ... (Point Table code remains same) ...
            from sheet_utils import read_results
            df = read_results()
            df["Status"] = df["Status"].astype(str).str.strip().str.lower()
            final_df = df[df["Status"] == "final"]
            if not final_df.empty:
                leaderboard = final_df.groupby("Group")["Points"].sum().reset_index().sort_values(by="Points", ascending=False)
                leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))
                leaderboard["Group"] = leaderboard["Group"].apply(lambda g: f"{g} – {GROUP_NAMES_ML.get(g, '')}")
                st.table(leaderboard)