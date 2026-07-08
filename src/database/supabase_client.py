from supabase import create_client, Client
import streamlit as st
import os

@st.cache_resource
def init_connection():
    url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Credenciales de Supabase no encontradas")
    return create_client(url, key)

supabase: Client = init_connection()
