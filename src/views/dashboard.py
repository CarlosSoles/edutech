import streamlit as st
import pandas as pd
import altair as alt
from src.database.supabase_client import supabase

def dashboard_page():
    st.title("🏠 Inicio")
    
    docente_id = st.session_state.user_info['id']
    id_aula = st.session_state.user_info.get('id_aula')

    if not id_aula:
        st.warning("No tienes un aula asignada.")
        st.stop()
        
    alumnos = supabase.table("alumnos").select("*").eq("id_aula", id_aula).execute().data
    if not alumnos:
        st.info("No hay alumnos matriculados en esta aula.")
        st.stop()
        
    alumnos_dict = {a['id']: f"{a['nombre']} {a['apellido']}" for a in alumnos}
    
    # 1. TOP METRICS
    total_alumnos = len(alumnos)
    
    # Asistencia
    sesiones = supabase.table("sesiones_clase").select("id, fecha, id_area").eq("id_aula", id_aula).order("fecha", desc=True).execute().data
    asistencias_hoy = 0
    fecha_asistencia = "Ninguna"
    if sesiones:
        ultima_sesion = sesiones[0]
        fecha_asistencia = ultima_sesion['fecha']
        asis_data = supabase.table("asistencias").select("asistio").eq("id_sesion", ultima_sesion['id']).execute().data
        asistencias_hoy = sum(1 for a in asis_data if a['asistio'])
        
    # Faltantes
    cuadernos = supabase.table("cuadernos_campo").select("fecha, id_area").eq("id_aula", id_aula).execute().data
    pares_cuadernos = {(c['fecha'], c['id_area']) for c in cuadernos}
    sesiones_faltantes = []
    for s in sesiones:
        if (s['fecha'], s['id_area']) not in pares_cuadernos:
            sesiones_faltantes.append(s)
            
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Alumnos", total_alumnos)
    with col2:
        st.metric(f"Asistencia ({fecha_asistencia})", f"{asistencias_hoy} / {total_alumnos}")
    with col3:
        st.metric("Registros Faltantes", len(sesiones_faltantes), delta_color="inverse")
        
    if sesiones_faltantes:
        areas = supabase.table("areas").select("*").execute().data
        areas_dict = {a['id']: a['nombre'] for a in areas}
        st.warning(f"⚠️ Te falta subir la foto del cuaderno de campo de {len(sesiones_faltantes)} sesiones donde tomaste asistencia.")
        with st.expander("Ver sesiones faltantes"):
            for s in sesiones_faltantes:
                st.write(f"- 📅 {s['fecha']} - Área: **{areas_dict.get(s['id_area'], 'Desconocido')}**")
                
    st.markdown("---")
    
    # 2. MAPA DE ATENCION POR AREAS
    st.subheader("🗺️ Mapa de Atención por Áreas (Áreas Críticas)")
    st.write("Muestra en qué áreas el Asesor Pedagógico ha tenido que intervenir más (es decir, dónde los niños presentan más obstáculos).")
    
    asesorias_global = supabase.table("asesorias_ia").select("estado, id_evidencia").execute().data
    evidencias_global = supabase.table("evidencias_alumnos").select("id, cuadernos_campo(id_area)").execute().data
    
    ev_area_map = {e['id']: e.get('cuadernos_campo', {}).get('id_area') for e in evidencias_global if e.get('cuadernos_campo')}
    
    areas = supabase.table("areas").select("*").execute().data
    areas_dict = {a['id']: a['nombre'] for a in areas}
    
    conteo_asesorias_area = {}
    for a in asesorias_global:
        id_ev = a.get('id_evidencia')
        if id_ev and id_ev in ev_area_map:
            area_id = ev_area_map[id_ev]
            area_name = areas_dict.get(area_id, "Desconocido")
            conteo_asesorias_area[area_name] = conteo_asesorias_area.get(area_name, 0) + 1
            
    if conteo_asesorias_area:
        df_mapa = pd.DataFrame(list(conteo_asesorias_area.items()), columns=["Área", "Intervenciones"])
        
        # Diagrama Circular (Pie Chart) usando Altair
        pie_chart = alt.Chart(df_mapa).mark_arc(innerRadius=0).encode(
            theta=alt.Theta(field="Intervenciones", type="quantitative"),
            color=alt.Color(field="Área", type="nominal"),
            tooltip=['Área', 'Intervenciones']
        ).properties(height=350)
        
        st.altair_chart(pie_chart, use_container_width=True)
    else:
        st.info("Aún no hay asesorías registradas en el aula.")
    
    st.markdown("---")
    
    # 3. PROGRESO INDIVIDUAL
    st.subheader("📈 Progreso Individual y Enfoque por Área")
    alumno_seleccionado_str = st.selectbox("Selecciona un alumno para analizar su distribución de evaluaciones:", list(alumnos_dict.values()))
    
    if alumno_seleccionado_str:
        alumno_id_sel = next(k for k, v in alumnos_dict.items() if v == alumno_seleccionado_str)
        
        # Breakdown por área
        evidencias_alumno = supabase.table("evidencias_alumnos").select(
            "cuadernos_campo(id_area, fecha)"
        ).eq("id_alumno", alumno_id_sel).execute().data
        
        if evidencias_alumno:
            areas = supabase.table("areas").select("*").execute().data
            areas_dict = {a['id']: a['nombre'] for a in areas}
            
            conteo_areas = {}
            for ev in evidencias_alumno:
                c = ev.get('cuadernos_campo')
                if c:
                    area_name = areas_dict.get(c.get('id_area'), 'General')
                    conteo_areas[area_name] = conteo_areas.get(area_name, 0) + 1
                    
            df_areas = pd.DataFrame(list(conteo_areas.items()), columns=["Área", "Total de Evaluaciones"])
            df_areas = df_areas.sort_values(by="Total de Evaluaciones", ascending=False)
            
            st.markdown("##### 📚 Evaluaciones Registradas por Área")
            st.dataframe(df_areas, hide_index=True, use_container_width=True)
            
            # --- NUEVO: EFECTIVIDAD PEDAGÓGICA (LINE CHART) ---
            st.markdown("##### 🧠 Evolución del Aprendizaje (Línea de Tiempo)")
            asesorias_alumno = supabase.table("asesorias_ia").select("estado, created_at").eq("id_alumno", alumno_id_sel).execute().data
            
            if asesorias_alumno:
                # Filtrar solo las resueltas
                asesorias_resueltas = [a for a in asesorias_alumno if a.get('estado') in ['MEJORANDO', 'MANTIENE_NIVEL']]
                
                if asesorias_resueltas:
                    # Ordenar por fecha cronológicamente
                    asesorias_resueltas.sort(key=lambda x: x['created_at'])
                    
                    historial_fechas = []
                    historial_estados = []
                    
                    for i, asis in enumerate(asesorias_resueltas):
                        fecha_corta = asis['created_at'][:10]
                        historial_fechas.append(f"S{i+1} ({fecha_corta})")
                        historial_estados.append(asis['estado'])
                        
                    total_resueltas = len(asesorias_resueltas)
                    exitos = sum(1 for a in asesorias_resueltas if a['estado'] == 'MEJORANDO')
                    pct_exito = round((exitos / total_resueltas) * 100)
                    
                    st.metric("Índice de Progreso General", f"{pct_exito}%")
                    
                    df_evolucion = pd.DataFrame({
                        "Tiempo": historial_fechas,
                        "Estado de Asesoría": historial_estados
                    })
                    
                    # Gráfico de líneas categórico en el eje Y usando Altair
                    line_chart = alt.Chart(df_evolucion).mark_line(point=True).encode(
                        x=alt.X('Tiempo', sort=None, title='Sesiones Evaluadas'),
                        y=alt.Y('Estado de Asesoría', sort=['MANTIENE_NIVEL', 'MEJORANDO'], title='Progreso'),
                        tooltip=['Tiempo', 'Estado de Asesoría']
                    ).properties(height=300)
                    
                    st.altair_chart(line_chart, use_container_width=True)
                else:
                    st.info("Hay asesorías generadas, pero aún no has calificado si las dinámicas sugeridas fueron útiles o no.")
            else:
                st.info("Este alumno no tiene intervenciones del Asesor Pedagógico aún.")
                
        else:
            st.info("Este alumno no tiene evaluaciones registradas aún. ¡Tómale foto a su próximo cuaderno de campo!")

dashboard_page()
