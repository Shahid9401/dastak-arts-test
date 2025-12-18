import streamlit as st
import time
import streamlit as st
from header import render_header
from student_view import render_student_view

st.set_page_config(
    page_title="DASTAK Arts Festival 2025 – Results",
    layout="wide"
)
render_header()
render_student_view()
