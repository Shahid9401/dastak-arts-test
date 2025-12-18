import streamlit as st

def render_header(compact=False):
    import streamlit as st

    if compact:
        # Compact header for login page
        col1, col2 = st.columns([1, 6])
        with col1:
            st.image("logo.png", width=60)
        with col2:
            st.markdown(
                "<h3 style='margin-top:10px;'>ASSABAH ARTS AND SCIENCE COLLEGE</h3>",
                unsafe_allow_html=True
            )
        st.markdown("---")
        return

    # ---------- FULL HEADER (after login) ----------
    st.image("arts_logo.jpg", use_column_width=None)
    st.markdown(
        "<h1 style='text-align:center;'>DASTAK ARTS FESTIVAL 2025</h1>",
        unsafe_allow_html=True
    )
    st.markdown("---")
