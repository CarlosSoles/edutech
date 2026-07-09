import streamlit as st
from src.database.supabase_client import supabase
from src.core.agents import AgentAdvisor

# ── CSS GLOBAL ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --ink: #1E2A28;
    --ink-soft: #5B6B68;
    --bg: #F7F8F5;
    --card: #FFFFFF;
    --line: #E4E7E1;
    --teal: #2D6A66;
    --teal-soft: #E4F0EE;
    --amber: #D98E3D;
    --amber-soft: #FBEEDF;
    --red: #C24C3F;
    --red-soft: #FBEAE7;
    --green: #2A7A4B;
    --green-soft: #E6F4EC;
    --blue: #2563EB;
    --blue-soft: #EFF6FF;
    --radius: 14px;
    --shadow: 0 1px 2px rgba(30,42,40,0.04), 0 4px 16px rgba(30,42,40,0.04);
}

/* Base text */
body, p, span, div, label, input, textarea, select, td, th, li, a,
.stMarkdown, .stText, .element-container {
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 { font-family: 'Fraunces', serif !important; }

/* Page Header */
.page-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
}
.header-icon {
    width: 42px; height: 42px;
    background: var(--blue-soft);
    color: var(--blue);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}
.header-title {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 28px;
    color: var(--ink);
    margin: 0;
}
.header-subtitle {
    font-size: 14px;
    color: var(--ink-soft);
    margin-bottom: 30px;
}

/* Card containers via st.container(border=True) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: var(--radius) !important;
    border-color: var(--line) !important;
    box-shadow: var(--shadow) !important;
    background: var(--card) !important;
}

/* List Card Specifics */
.list-title {
    font-weight: 700;
    font-size: 16px;
    color: var(--ink);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.list-subtitle {
    font-size: 12px;
    color: var(--ink-soft);
    margin-top: 4px;
    margin-bottom: 16px;
}

/* Search input styling */
[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    font-size: 13px !important;
}

/* Radio button list styling to look like selectable items */
[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background: transparent;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 2px;
    cursor: pointer;
    transition: all 0.2s;
    display: block;
    width: 100%;
}
[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    background: var(--bg);
}
/* Hide the circle */
[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}
/* Text inside radio */
[data-testid="stRadio"] > div[role="radiogroup"] > label p {
    font-size: 13.5px !important;
    color: var(--ink) !important;
    margin: 0 !important;
    font-weight: 500 !important;
}
/* Checked state */
[data-testid="stRadio"] > div[role="radiogroup"] > label[aria-checked="true"],
[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
    background: var(--teal-soft) !important;
}
[data-testid="stRadio"] > div[role="radiogroup"] > label[aria-checked="true"] p,
[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] p {
    font-weight: 600 !important;
    color: var(--teal) !important;
}

/* Detail Card Specifics */
.detail-name {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 24px;
    color: var(--ink);
    margin: 0 0 4px;
}
.detail-subtitle {
    font-size: 13px;
    color: var(--ink-soft);
    margin: 0 0 24px;
}
.metric-label {
    font-size: 12px;
    color: var(--ink-soft);
    font-weight: 500;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
}
.metric-value {
    font-family: 'Fraunces', serif;
    font-size: 32px;
    font-weight: 600;
    color: #B0B7B6;
    margin: 0;
    line-height: 1;
}
.metric-line {
    height: 3px;
    background: var(--line);
    border-radius: 2px;
    margin-top: 8px;
    width: 100%;
}

/* Expander styling */
[data-testid="stExpander"] {
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    margin-top: 20px !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: var(--ink) !important;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 30px 20px;
}
.empty-icon {
    width: 48px;
    height: 48px;
    background: var(--amber-soft);
    color: var(--amber);
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 16px;
}
.empty-text {
    font-size: 13.5px;
    color: var(--ink-soft);
    line-height: 1.5;
}

/* Button overrides for teal */
[data-testid="baseButton-primary"] {
    background-color: var(--teal) !important;
    border-color: var(--teal) !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="baseButton-primary"]:hover {
    background-color: #245552 !important;
    border-color: #245552 !important;
}

</style>
""", unsafe_allow_html=True)

def advisor_page():
    if "role" not in st.session_state or st.session_state.role != "docente":
        st.error("Acceso denegado. Solo para docentes.")
        st.stop()

    docente_id = st.session_state.user_info['id']
    id_aula = st.session_state.user_info.get('id_aula')
    aula_data = st.session_state.user_info.get('aulas', {})
    aula_nombre = aula_data.get('nombre', 'Desconocida') if aula_data else 'Desconocida'

    if not id_aula:
        st.warning("No tienes un aula asignada.")
        st.stop()

    # ── CARGAR DATOS ──────────────────────────────────────────────────────────
    @st.cache_data(ttl=60)
    def cargar_datos_base(aula_id):
        alumnos = supabase.table("alumnos").select("*").eq("id_aula", aula_id).order("apellido").execute().data
        areas = supabase.table("areas").select("*").execute().data
        areas_dict = {a['id']: a['nombre'] for a in areas}
        return alumnos, areas_dict

    alumnos, areas_dict = cargar_datos_base(id_aula)

    if not alumnos:
        st.info("No hay alumnos matriculados en esta aula.")
        st.stop()

    # Ordenar por apellido (seguridad extra en Python)
    alumnos = sorted(alumnos, key=lambda a: a.get('apellido', '').lower())

    # ── FUNCIONES ASESORÍA ───────────────────────────────────────────────────
    def generar_asesoria(alumno_id, contexto, id_evidencia):
        with st.spinner("Generando asesoría pedagógica..."):
            agente = AgentAdvisor()
            texto = agente.generate_advice(contexto)
            
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
        st.toast("Feedback guardado exitosamente.")
        st.rerun()

    # ── PAGE HEADER ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-header">
        <div class="header-icon">🎓</div>
        <h1 class="header-title">Asesor Pedagógico</h1>
    </div>
    <div class="header-subtitle">
        Análisis inteligente y dinámicas sugeridas basadas en el desempeño y la asistencia de cada alumno.
    </div>
    """, unsafe_allow_html=True)

    # ── DISEÑO DE COLUMNAS ────────────────────────────────────────────────────
    col_lista, col_detalle = st.columns([1, 2.3])

    with col_lista:
        with st.container(border=True):
            st.markdown(f"""
            <h3 class="list-title">📋 Alumnos</h3>
            <div class="list-subtitle">{len(alumnos)} alumnos · Aula {aula_nombre}</div>
            """, unsafe_allow_html=True)
            
            search_query = st.text_input("Buscar alumno", placeholder="🔍 Buscar alumno...", label_visibility="collapsed")
            
            if search_query:
                alumnos_filtrados = [a for a in alumnos if search_query.lower() in f"{a['nombre']} {a['apellido']}".lower()]
            else:
                alumnos_filtrados = alumnos
                
            if alumnos_filtrados:
                opciones = [f"{a['nombre']} {a['apellido']}" for a in alumnos_filtrados]
                alumno_seleccionado_str = st.radio("Lista de Alumnos", opciones, label_visibility="collapsed")
            else:
                st.write("No se encontraron alumnos.")
                alumno_seleccionado_str = None

    with col_detalle:
        if alumno_seleccionado_str:
            alumno = next(a for a in alumnos if f"{a['nombre']} {a['apellido']}" == alumno_seleccionado_str)
            
            with st.container(border=True):
                # Detalle Header (Sin logo/avatar, solo texto como pediste)
                st.markdown(f"""
                <h2 class="detail-name">{alumno['nombre']} {alumno['apellido']}</h2>
                <p class="detail-subtitle">Aula {aula_nombre}</p>
                """, unsafe_allow_html=True)
                
                # Datos Asistencia
                res_asist = supabase.table("asistencias").select("asistio").eq("id_alumno", alumno['id']).execute().data
                total_clases = len(res_asist)
                if total_clases > 0:
                    asistencias = sum(1 for a in res_asist if a['asistio'])
                    faltas = total_clases - asistencias
                    pct_asist = round((asistencias / total_clases) * 100)
                    pct_faltas = 100 - pct_asist
                else:
                    pct_asist, pct_faltas = 0, 0

                # Datos Cuadernos
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

                # Asesorías
                res_asesorias_todas = supabase.table("asesorias_ia").select("*").eq("id_alumno", alumno['id']).execute().data
                asesoria_activa = next((a for a in res_asesorias_todas if a['estado'] == "PENDIENTE"), None)

                # Metricas Row
                col_m1, col_m2, col_btn = st.columns([1, 1, 2.5])
                with col_m1:
                    st.markdown(f"""
                    <div class="metric-label">⊙ Asistencias</div>
                    <div class="metric-value">{pct_asist}%</div>
                    <div class="metric-line"></div>
                    """, unsafe_allow_html=True)
                with col_m2:
                    st.markdown(f"""
                    <div class="metric-label">⊙ Faltas</div>
                    <div class="metric-value">{pct_faltas}%</div>
                    <div class="metric-line"></div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                    if not asesoria_activa:
                        if st.button("🪄 Generar Asesoría", use_container_width=True, type="primary", key=f"btn_gen_{alumno['id']}"):
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
                            
                            id_ev_reciente = ev_reciente['id'] if ev_reciente else None
                            generar_asesoria(alumno['id'], ctx, id_ev_reciente)

                # Expander Sesiones
                with st.expander("📑 Ver sesiones evaluadas en Cuadernos de Campo", expanded=True):
                    if not res_evidencias:
                        st.markdown("""
                        <div class="empty-state">
                            <div class="empty-icon">⏱</div>
                            <div class="empty-text">
                                <strong>Aún no ha sido evaluado</strong> en ningún cuaderno de campo.<br>
                                En cuanto se registre una sesión para este alumno, aparecerá aquí.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        for ev in evidencias_ordenadas:
                            c = ev.get('cuadernos_campo', {})
                            area_name = areas_dict.get(c.get('id_area'), 'General')
                            
                            asesoria_vinc = next((a for a in res_asesorias_todas if a.get('id_evidencia') == ev['id']), None)
                            badge = ""
                            if asesoria_vinc:
                                if asesoria_vinc['estado'] == 'MEJORANDO': badge = "🤖 *(Asesorada - Fue útil)*"
                                elif asesoria_vinc['estado'] == 'MANTIENE_NIVEL': badge = "🤖 *(Asesorada - Sin efecto)*"
                                else: badge = "🤖 *(Asesorada - Pendiente)*"
                            
                            st.markdown(f"**{c.get('fecha')} - {c.get('titulo_actividad')} ({area_name})** {badge}")
                            st.write(f"📝 *Retroalimentación:* {ev.get('retroalimentacion', 'Ninguna')}")
                            st.markdown("---")

                # Asesoría Activa
                if asesoria_activa:
                    st.markdown("---")
                    st.info("💡 **Asesoría Activa de Kubi AI**")
                    st.caption(f"*(Esta asesoría está basada en el último registro de retroalimentación del área de **{ultima_area}**)*")
                    st.markdown(asesoria_activa['asesoria_texto'])
                    
                    st.write("¿La dinámica sugerida funcionó con el alumno?")
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("👍 Ha sido de utilidad", key=f"util_{asesoria_activa['id']}", use_container_width=True, type="primary"):
                            resolver_asesoria(asesoria_activa['id'], "MEJORANDO")
                    with btn_col2:
                        if st.button("👎 No dio el efecto esperado", key=f"noutil_{asesoria_activa['id']}", use_container_width=True):
                            resolver_asesoria(asesoria_activa['id'], "MANTIENE_NIVEL")

advisor_page()
