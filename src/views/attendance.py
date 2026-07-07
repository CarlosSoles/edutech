import streamlit as st
import datetime
from src.database.supabase_client import supabase

def attendance_page():
    st.title("✅ Control de Asistencia")

    if "role" not in st.session_state or st.session_state.role != "docente":
        st.error("Acceso denegado. Solo para docentes.")
        st.stop()

    docente_info = st.session_state.user_info
    id_aula = docente_info.get('id_aula')
    aula_data = docente_info.get('aulas', {})
    aula_nombre = aula_data.get('nombre', 'Desconocida')

    if not id_aula:
        st.warning("No tienes un aula asignada.")
        st.stop()

    st.write(f"**Aula:** {aula_nombre}")

    @st.cache_data(ttl=60)
    def cargar_areas():
        res = supabase.table("areas").select("*").execute()
        return res.data

    @st.cache_data(ttl=60)
    def cargar_alumnos(aula_id):
        res = supabase.table("alumnos").select("*").eq("id_aula", aula_id).execute()
        return res.data

    areas = cargar_areas()
    alumnos = cargar_alumnos(id_aula)

    if not areas or not alumnos:
        st.warning("Asegúrate de que haya alumnos y áreas registradas en el sistema.")
        st.stop()

    areas_dict = {a['id']: a['nombre'] for a in areas}

    tab_registro, tab_historial = st.tabs(["✅ Registrar Asistencia", "🕒 Historial de Sesiones"])

    with tab_registro:
        st.subheader("Nueva Sesión de Clase")
        fecha_sesion = st.date_input("Fecha de Sesión", value=datetime.date.today())

        # Verificar si ya existe alguna sesión hoy para bloquear la creación de una segunda
        sesion_existente = supabase.table("sesiones_clase") \
            .select("*") \
            .eq("id_aula", id_aula) \
            .eq("fecha", str(fecha_sesion)) \
            .execute()

        asistencias_previas = {}
        id_sesion_actual = None

        if sesion_existente.data:
            ses = sesion_existente.data[0]
            id_sesion_actual = ses['id']
            area_sesion = ses['id_area']
            st.info("⚠️ Ya tomaste lista para esta fecha. Solo puedes editar el registro existente.")
            area_seleccionada = st.selectbox("Área evaluada", options=[area_sesion], format_func=lambda x: areas_dict.get(x, "Desconocido"), disabled=True)
            
            res_asist = supabase.table("asistencias").select("*").eq("id_sesion", id_sesion_actual).execute()
            asistencias_previas = {a['id_alumno']: a['asistio'] for a in res_asist.data}
        else:
            area_seleccionada = st.selectbox("Área a evaluar", options=list(areas_dict.keys()), format_func=lambda x: areas_dict[x])

        with st.form("form_asistencia"):
            st.write("Desmarca a los alumnos que faltaron a clases hoy:")
            
            nuevas_asistencias = {}
            for alumno in alumnos:
                # Si hay registro previo lo usamos, si no, por defecto True
                valor_por_defecto = asistencias_previas.get(alumno['id'], True)
                
                # Checkbox con el nombre del alumno
                col_ch, col_name = st.columns([1, 10])
                with col_ch:
                    asistio = st.checkbox("Asistió", value=valor_por_defecto, key=f"chk_{alumno['id']}", label_visibility="collapsed")
                with col_name:
                    if asistio:
                        st.markdown(f"🟢 **{alumno['nombre']} {alumno['apellido']}**")
                    else:
                        st.markdown(f"🔴 ~~{alumno['nombre']} {alumno['apellido']}~~")
                        
                nuevas_asistencias[alumno['id']] = asistio

            st.markdown("---")
            conforme = st.checkbox("☑️ Declaro que el registro de asistencia es conforme y he terminado de pasar lista.")
            submitted = st.form_submit_button("💾 Guardar Asistencia", type="primary")
            
            if submitted:
                if not conforme:
                    st.error("⚠️ Debes marcar la casilla de conformidad para poder guardar la asistencia.")
                else:
                    try:
                        if not id_sesion_actual:
                            # Crear sesión nueva
                            res_ses = supabase.table("sesiones_clase").insert({
                                "id_aula": id_aula,
                                "fecha": str(fecha_sesion),
                                "id_area": area_seleccionada
                            }).execute()
                            id_sesion_actual = res_ses.data[0]['id']
                        
                        # Preparar asistencias (upsert o delete+insert)
                        # Lo más simple: borrar las viejas e insertar las nuevas para esa sesión
                        supabase.table("asistencias").delete().eq("id_sesion", id_sesion_actual).execute()
                        
                        datos_asistencia = []
                        for al_id, asis in nuevas_asistencias.items():
                            datos_asistencia.append({
                                "id_sesion": id_sesion_actual,
                                "id_alumno": al_id,
                                "asistio": asis
                            })
                            
                        supabase.table("asistencias").insert(datos_asistencia).execute()
                        
                        st.success("¡Asistencia guardada correctamente!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

    with tab_historial:
        st.subheader("Historial de Sesiones Anteriores")
        
        # Cargar todas las sesiones
        sesiones = supabase.table("sesiones_clase").select("*").eq("id_aula", id_aula).order("fecha", desc=True).execute()
        
        if not sesiones.data:
            st.info("No hay sesiones registradas en el historial.")
        else:
            for s in sesiones.data:
                with st.expander(f"📅 {s['fecha']} - {areas_dict.get(s['id_area'], '')}"):
                    # Cargar asistencias de esta sesión al expandir
                    res_det = supabase.table("asistencias").select("id_alumno, asistio").eq("id_sesion", s['id']).execute()
                    if res_det.data:
                        asistieron = []
                        faltaron = []
                        for d in res_det.data:
                            # Buscar nombre del alumno
                            nombre_alumno = next((f"{a['nombre']} {a['apellido']}" for a in alumnos if a['id'] == d['id_alumno']), "Desconocido")
                            if d['asistio']:
                                asistieron.append(nombre_alumno)
                            else:
                                faltaron.append(nombre_alumno)
                                
                        st.write(f"**Asistencias ({len(asistieron)}):**")
                        if asistieron:
                            st.write(", ".join(asistieron))
                        else:
                            st.write("Ninguno.")
                            
                        st.write(f"**Faltas ({len(faltaron)}):**")
                        if faltaron:
                            st.error(", ".join(faltaron))
                        else:
                            st.success("¡Asistencia perfecta!")
                    else:
                        st.write("No hay detalle de asistencia para esta sesión.")

attendance_page()
