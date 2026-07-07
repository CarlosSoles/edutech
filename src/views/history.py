import streamlit as st
import datetime
from src.database.supabase_client import supabase
from src.utils.document_builder import generate_word_report

def history_page():
    st.title("📚 Mis Registros (Historial)")

    if "role" not in st.session_state or st.session_state.role != "docente":
        st.error("Acceso denegado. Solo para docentes.")
        st.stop()

    docente_id = st.session_state.user_info['id']
    aula_data = st.session_state.user_info.get('aulas', {})
    aula_nombre = aula_data.get('nombre', '')
    aula_edad = aula_data.get('edad', '')

    @st.cache_data(ttl=60)
    def cargar_areas():
        try:
            res = supabase.table("areas").select("*").execute()
            return {a['id']: a['nombre'] for a in res.data}
        except Exception:
            return {}

    @st.cache_data(ttl=60)
    def cargar_alumnos(id_aula):
        try:
            res = supabase.table("alumnos").select("*").eq("id_aula", id_aula).execute()
            return {a['id']: f"{a['nombre']} {a['apellido']}" for a in res.data}
        except Exception:
            return {}

    areas_dict = cargar_areas()
    alumnos_dict = cargar_alumnos(st.session_state.user_info.get('id_aula'))

    def load_cuadernos():
        res = supabase.table("cuadernos_campo").select("*").eq("id_docente", docente_id).order("fecha", desc=True).execute()
        return res.data

    cuadernos = load_cuadernos()

    if not cuadernos:
        st.info("Aún no tienes ningún registro guardado.")
        st.stop()

    # Si el usuario solicitó generar el word de un cuaderno específico
    if st.session_state.get("generar_word_id"):
        c_id = st.session_state.generar_word_id
        cuaderno = next((c for c in cuadernos if c['id'] == c_id), None)
        
        if cuaderno:
            with st.spinner("Generando documento oficial..."):
                res_ev = supabase.table("evidencias_alumnos").select("*").eq("id_cuaderno", c_id).execute()
                
                doc_data = {
                    "titulo": cuaderno.get("titulo_actividad", ""),
                    "fecha": cuaderno.get("fecha", ""),
                    "aula": aula_nombre,
                    "edad": aula_edad,
                    "area": areas_dict.get(cuaderno.get("id_area"), "No definida"),
                    "competencia": cuaderno.get("competencia", ""),
                    "estandar": cuaderno.get("estandar", ""),
                    "capacidades": cuaderno.get("capacidades", ""),
                    "criterios": cuaderno.get("criterios", "")
                }
                
                niños_data = []
                for ev in res_ev.data:
                    niños_data.append({
                        "nombre": alumnos_dict.get(ev["id_alumno"], "Desconocido"),
                        "descripcion": ev.get("descripcion", ""),
                        "retroalimentacion": ev.get("retroalimentacion", "")
                    })
                    
                word_bytes = generate_word_report(doc_data, niños_data)
                
                st.success(f"¡Documento '{cuaderno.get('titulo_actividad')}' listo para descargar!")
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.download_button("⬇️ Descargar Plantilla Oficial (Word)", data=word_bytes, file_name=f"Cuaderno_{cuaderno['fecha']}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", width='stretch')
                with col2:
                    if st.button("Cerrar", width='stretch'):
                        st.session_state.generar_word_id = None
                        st.rerun()
                        
        st.markdown("---")

    st.write("Aquí puedes consultar todos tus cuadernos de campo anteriores:")

    for c in cuadernos:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(c['titulo_actividad'])
                st.caption(f"📅 Fecha: {c['fecha']} | 📚 Área: {areas_dict.get(c['id_area'], 'N/A')}")
            with col2:
                if st.button("Preparar Word", key=f"btn_{c['id']}", width='stretch'):
                    st.session_state.generar_word_id = c['id']
                    st.rerun()

history_page()
