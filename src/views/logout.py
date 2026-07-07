import streamlit as st

def logout_page():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_info = None
    st.rerun()

logout_page()
