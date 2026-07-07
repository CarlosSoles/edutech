import streamlit as st

def logout_page():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_info = None
    st.switch_page("src/views/auth.py")

logout_page()
