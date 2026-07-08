from supabase import create_client, Client
import streamlit as st
import os

@st.cache_resource
def init_connection():
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
    except Exception:
        url = None
        key = None
        
    url = url or os.environ.get("SUPABASE_URL")
    key = key or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Credenciales de Supabase no encontradas")
    return create_client(url, key)

supabase: Client = init_connection()
