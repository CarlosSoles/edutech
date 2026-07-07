import streamlit as st
from src.database.supabase_client import supabase
from src.core.agents import AgentAdvisor

def advisor_page():
    st.title("🧊 Asesor Pedagógico - Kubi AI")
    st.write("Análisis inteligente y dinámicas sugeridas basadas en el desempeño y asistencia.")

    if "role" not in st.session_state or st.session_state.role != "docente":
        st.error("Acceso denegado. Solo para docentes.")
        st.stop()

    docente_id = st.session_state.user_info['id']
    id_aula = st.session_state.user_info.get('id_aula')

    if not id_aula:
        st.warning("No tienes un aula asignada.")
        st.stop()

    # Cargar datos base
    @st.cache_data(ttl=30)
    def cargar_datos_base(aula_id):
        alumnos = supabase.table("alumnos").select("*").eq("id_aula", aula_id).execute().data
        areas = supabase.table("areas").select("*").execute().data
        areas_dict = {a['id']: a['nombre'] for a in areas}
        return alumnos, areas_dict

    alumnos, areas_dict = cargar_datos_base(id_aula)

    if not alumnos:
        st.info("No hay alumnos matriculados en esta aula.")
        st.stop()

    # Funciones para las acciones de base de datos
    def generar_asesoria(alumno_id, contexto, id_evidencia):
        with st.spinner("Generando asesoría pedagógica..."):
            agente = AgentAdvisor()
            texto = agente.generate_advice(contexto)
            
            # Guardar en BD como PENDIENTE
            supabase.table("asesorias_ia").insert({
                "id_alumno": alumno_id,
                "id_docente": docente_id,
                "id_evidencia": id_evidencia,
                "asesoria_texto": texto,
                "estado": "PENDIENTE"
            }).execute()
        st.rerun()

    def resolver_asesoria(asesoria_id, estado_final):
        supabase.table("asesorias_ia").update({"estado": estado_final}).eq("id", asesoria_id).execute()
        st.toast("Feedback guardado exitosamente. Se ha actualizado el estado del alumno.")
        st.rerun()

    st.markdown("---")
    
    # Diseño de 2 columnas: Lista a la izquierda, detalle a la derecha
    col_lista, col_detalle = st.columns([1, 2])
    
    opciones_alumnos = [f"{a['nombre']} {a['apellido']}" for a in alumnos]
    
    with col_lista:
        st.subheader("📋 Alumnos")
        alumno_seleccionado_str = st.radio("Seleccionar alumno:", opciones_alumnos, label_visibility="collapsed")
        
    with col_detalle:
        if alumno_seleccionado_str:
            alumno = next(a for a in alumnos if f"{a['nombre']} {a['apellido']}" == alumno_seleccionado_str)
            
            with st.container(border=True):
                st.subheader(f"🎓 {alumno['nombre']} {alumno['apellido']}")
                
                # --- DATOS DE ASISTENCIA ---
                res_asist = supabase.table("asistencias").select("asistio").eq("id_alumno", alumno['id']).execute().data
                total_clases = len(res_asist)
                if total_clases > 0:
                    asistencias = sum(1 for a in res_asist if a['asistio'])
                    faltas = total_clases - asistencias
                    pct_asist = round((asistencias / total_clases) * 100)
                    pct_faltas = 100 - pct_asist
                else:
                    pct_asist, pct_faltas = 0, 0

                # --- DATOS DE CUADERNOS ---
                res_evidencias = supabase.table("evidencias_alumnos").select(
                    "id, descripcion, retroalimentacion, cuadernos_campo(titulo_actividad, fecha, id_area)"
                ).eq("id_alumno", alumno['id']).execute().data
                
                ultima_area = "General"
                ev_reciente = None
                if res_evidencias:
                    evidencias_ordenadas = sorted(
                        res_evidencias, 
                        key=lambda x: x.get('cuadernos_campo', {}).get('fecha', ''), 
                        reverse=True
                    )
                    ev_reciente = evidencias_ordenadas[0]
                    c = ev_reciente.get('cuadernos_campo', {})
                    ultima_area = areas_dict.get(c.get('id_area'), 'General')
                
                # --- ASESORÍAS ---
                res_asesorias_todas = supabase.table("asesorias_ia").select("*").eq("id_alumno", alumno['id']).execute().data
                asesoria_activa = next((a for a in res_asesorias_todas if a['estado'] == "PENDIENTE"), None)
                evidencias_asesoradas_ids = [a['id_evidencia'] for a in res_asesorias_todas if a.get('id_evidencia')]

                # Renderizado de estadísticas en columnas
                st.markdown("##### 📊 Estadísticas del Alumno")
                col_m1, col_m2, col_m3 = st.columns([2, 2, 3])
                
                with col_m1:
                    st.metric("Asistencias", f"{pct_asist}%", help=f"Total de clases: {total_clases}")
                with col_m2:
                    st.metric("Faltas", f"{pct_faltas}%", delta_color="inverse")
                    
                with col_m3:
                    # Botón de generar (solo si no hay una pendiente)
                    if not asesoria_activa:
                        if st.button("🤖 Generar Asesoría", key=f"gen_{alumno['id']}", width='stretch'):
                            # Construir contexto
                            ctx = f"ALUMNO: {alumno['nombre']} {alumno['apellido']}\n"
                            ctx += f"PORCENTAJE DE FALTAS: {pct_faltas}%\n\n"
                            ctx += "HISTORIAL DE SESIONES EVALUADAS:\n"
                            if not res_evidencias:
                                ctx += "- Sin evaluaciones previas.\n"
                            else:
                                c = ev_reciente.get('cuadernos_campo', {})
                                
                                ctx += f"ÚLTIMA CLASE EVALUADA ({c.get('fecha')}):\n"
                                ctx += f"- Actividad: '{c.get('titulo_actividad')}' ({ultima_area})\n"
                                ctx += f"  Evidencia: {ev_reciente.get('descripcion')}\n"
                                ctx += f"  A retroalimentar: {ev_reciente.get('retroalimentacion')}\n\n"
                                ctx += "OBJETIVO: Brinda tu asesoría pensando específicamente en qué debería hacer el docente en la PRÓXIMA clase para mejorar o reforzar estos aspectos."
                            
                            generar_asesoria(alumno['id'], ctx, ev_reciente['id'])

                # Mostrar evaluaciones pasadas en un expander
                with st.expander("Ver sesiones evaluadas en Cuadernos de Campo", expanded=True):
                    if res_evidencias:
                        for ev in evidencias_ordenadas:
                            c = ev.get('cuadernos_campo', {})
                            area_name = areas_dict.get(c.get('id_area'), 'General')
                            
                            asesoria_vinculada = next((a for a in res_asesorias_todas if a.get('id_evidencia') == ev['id']), None)
                            badge = ""
                            if asesoria_vinculada:
                                if asesoria_vinculada['estado'] == 'MEJORANDO':
                                    badge = "🤖 *(Asesorada - Fue útil)*"
                                elif asesoria_vinculada['estado'] == 'MANTIENE_NIVEL':
                                    badge = "🤖 *(Asesorada - Sin efecto)*"
                                else:
                                    badge = "🤖 *(Asesorada - Pendiente)*"
                            
                            st.markdown(f"**{c.get('fecha')} - {c.get('titulo_actividad')} ({area_name})** {badge}")
                            st.write(f"📝 *Retroalimentación:* {ev.get('retroalimentacion', 'Ninguna')}")
                            st.markdown("---")
                    else:
                        st.write("Aún no ha sido evaluado en ningún cuaderno de campo.")

                # Mostrar Asesoría Activa si existe
                if asesoria_activa:
                    st.info("💡 **Asesoría Activa de Kubi AI**")
                    st.caption(f"*(Esta asesoría está basada en el último registro de retroalimentación del área de **{ultima_area}**)*")
                    st.markdown(asesoria_activa['asesoria_texto'])
                    
                    st.write("¿La dinámica sugerida funcionó con el alumno?")
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("👍 Ha sido de utilidad", key=f"util_{asesoria_activa['id']}", width='stretch', type="primary"):
                            resolver_asesoria(asesoria_activa['id'], "MEJORANDO")
                    with btn_col2:
                        if st.button("👎 No dio el efecto esperado", key=f"noutil_{asesoria_activa['id']}", width='stretch'):
                            resolver_asesoria(asesoria_activa['id'], "MANTIENE_NIVEL")

advisor_page()
