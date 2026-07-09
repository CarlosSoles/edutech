import streamlit as st
from src.database.supabase_client import supabase

@st.cache_data(ttl=300)
def get_alumnos_by_aula(id_aula):
    """Obtiene todos los alumnos de un aula."""
    res = supabase.table("alumnos").select("*").eq("id_aula", id_aula).execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_areas():
    """Obtiene todas las áreas curriculares."""
    res = supabase.table("areas").select("*").execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_sesiones_by_aula(id_aula):
    """Obtiene todas las sesiones de clase de un aula, ordenadas por fecha descendente."""
    res = supabase.table("sesiones_clase").select("*").eq("id_aula", id_aula).order("fecha", desc=True).execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_asistencias_by_sesion(id_sesion):
    """Obtiene todas las asistencias de una sesión."""
    res = supabase.table("asistencias").select("*").eq("id_sesion", id_sesion).execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_asistencias_by_alumno(id_alumno):
    """Obtiene todas las asistencias de un alumno."""
    res = supabase.table("asistencias").select("*").eq("id_alumno", id_alumno).execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_cuadernos_by_aula(id_aula):
    """Obtiene todos los cuadernos de campo de un aula."""
    res = supabase.table("cuadernos_campo").select("*").eq("id_aula", id_aula).execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_cuadernos_by_docente(id_docente):
    """Obtiene todos los cuadernos de campo de un docente, ordenados por fecha."""
    res = supabase.table("cuadernos_campo").select("*").eq("id_docente", id_docente).order("fecha", desc=True).execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_asesorias_global():
    """Obtiene todas las asesorias de la IA."""
    res = supabase.table("asesorias_ia").select("*").execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_asesorias_by_alumno(id_alumno):
    """Obtiene asesorías por alumno."""
    res = supabase.table("asesorias_ia").select("*").eq("id_alumno", id_alumno).execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_evidencias_global():
    """Obtiene todas las evidencias con sus cuadernos de campo."""
    res = supabase.table("evidencias_alumnos").select("*, cuadernos_campo(*)").execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_evidencias_by_alumno(id_alumno):
    """Obtiene evidencias por alumno con cuadernos."""
    res = supabase.table("evidencias_alumnos").select("*, cuadernos_campo(*)").eq("id_alumno", id_alumno).execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_evidencias_by_cuaderno(id_cuaderno):
    """Obtiene evidencias por cuaderno."""
    res = supabase.table("evidencias_alumnos").select("*").eq("id_cuaderno", id_cuaderno).execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_aulas():
    """Obtiene todas las aulas (para Admin)."""
    res = supabase.table("aulas").select("*").execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_docentes_con_aulas():
    """Obtiene todos los docentes con información de sus aulas."""
    res = supabase.table("docentes").select("*, aulas(*)").execute()
    return res.data if res else []

@st.cache_data(ttl=300)
def get_alumnos_con_aulas():
    """Obtiene todos los alumnos con información de sus aulas."""
    res = supabase.table("alumnos").select("*, aulas(*)").execute()
    return res.data if res else []

def clear_cache():
    """Limpia el caché manualmente, útil después de operaciones de inserción/actualización."""
    st.cache_data.clear()
