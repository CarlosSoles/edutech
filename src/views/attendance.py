import streamlit as st
import datetime
from src.database.supabase_client import supabase
import src.utils.cache as db_cache

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
    --radius: 14px;
    --shadow: 0 1px 2px rgba(30,42,40,0.04), 0 4px 16px rgba(30,42,40,0.04);
}

/* Page title */
.att-title {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 28px;
    color: var(--ink);
    margin: 0 0 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Aula chip */
.aula-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 12.5px;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 18px;
}
.aula-chip-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--teal);
    flex-shrink: 0;
}

/* Main card */
.att-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 24px 28px;
    box-shadow: var(--shadow);
    margin-bottom: 20px;
}
.att-card-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 18px;
    color: var(--ink);
    margin: 0 0 20px;
}

/* Form fields row */
.field-label {
    font-size: 11.5px;
    font-weight: 600;
    color: var(--ink-soft);
    text-transform: uppercase;
    letter-spacing: .04em;
    margin-bottom: 6px;
}

/* Instruction row */
.att-instruction {
    font-size: 13px;
    color: var(--ink-soft);
    margin-bottom: 14px;
}

/* Counters */
.att-counters {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
    justify-content: flex-end;
}
.counter-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 12.5px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
}
.counter-badge.present {
    background: var(--green-soft);
    color: var(--green);
}
.counter-badge.absent {
    background: var(--red-soft);
    color: var(--red);
}
.counter-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}
.counter-badge.present .counter-dot { background: var(--green); }
.counter-badge.absent .counter-dot { background: var(--red); }

/* Student rows */
.student-row {
    display: flex;
    align-items: center;
    padding: 13px 0;
    border-bottom: 1px solid var(--line);
    gap: 14px;
}
.student-row:last-child { border-bottom: none; }
.student-name {
    flex: 1;
    font-size: 14px;
    font-weight: 500;
    color: var(--ink);
}
.student-name.absent {
    color: var(--ink-soft);
    text-decoration: line-through;
}

/* Toggle label */
.toggle-label {
    font-size: 12.5px;
    font-weight: 600;
    margin-left: 4px;
}
.toggle-label.present { color: var(--green); }
.toggle-label.absent  { color: var(--red); }

/* Confirm section */
.att-confirm {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 16px 0 8px;
    font-size: 13px;
    color: var(--teal);
    border-top: 1px solid var(--line);
    margin-top: 8px;
}
.att-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 4px;
}
.att-footer-note {
    font-size: 12.5px;
    color: var(--ink-soft);
}

/* History rows */
.hist-row {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.hist-date { font-weight: 600; font-size: 14px; color: var(--ink); }
.hist-area { font-size: 12.5px; color: var(--ink-soft); }
.hist-badge {
    font-size: 12px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    background: var(--green-soft);
    color: var(--green);
}

/* Override Streamlit form */
div[data-testid="stForm"] { border: none !important; padding: 0 !important; }

/* Card containers via st.container(border=True) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    border-color: var(--line) !important;
    box-shadow: var(--shadow) !important;
    padding: 18px 22px !important;
    background: var(--card) !important;
}

/* Toggle OFF → dark border so absence is clearly visible */
[data-testid="stToggle"]:has(input:not(:checked)) [role="switch"] {
    border: 2px solid #1E2A28 !important;
    background: #F0F0EE !important;
}

/* Style toggle (checkbox) to look like the design */
.stCheckbox > label {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
}
</style>
""", unsafe_allow_html=True)


def attendance_page():
    # ── AUTH CHECK ────────────────────────────────────────────────────────────
    if "role" not in st.session_state or st.session_state.role != "docente":
        st.error("Acceso denegado. Solo para docentes.")
        st.stop()

    docente_info = st.session_state.user_info
    id_aula = docente_info.get('id_aula')
    aula_data = docente_info.get('aulas', {})
    aula_nombre = aula_data.get('nombre', 'Desconocida') if aula_data else 'Desconocida'

    if not id_aula:
        st.warning("No tienes un aula asignada.")
        st.stop()

    # ── PAGE HEADER ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
        <div style="width:36px;height:36px;background:var(--green-soft);border-radius:10px;
                    display:flex;align-items:center;justify-content:center;font-size:18px;">✅</div>
        <h1 class="att-title" style="margin:0;">Control de Asistencia</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="aula-chip">
        <span class="aula-chip-dot"></span>
        Aula: {aula_nombre}
    </div>
    """, unsafe_allow_html=True)

    # ── CARGAR DATOS ──────────────────────────────────────────────────────────
    areas = db_cache.get_areas()
    alumnos = db_cache.get_alumnos_by_aula(id_aula)

    if not areas or not alumnos:
        st.warning("Asegúrate de que haya alumnos y áreas registradas en el sistema.")
        st.stop()

    # Ordenar por apellido (segundo nivel de seguridad, en caso de que DB no lo haga)
    alumnos = sorted(alumnos, key=lambda a: a.get('apellido', '').lower())
    areas_dict = {a['id']: a['nombre'] for a in areas}

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab_registro, tab_historial = st.tabs(["⊙ Registrar Asistencia", "⊙ Historial de Sesiones"])

    # ── TAB 1: REGISTRAR ─────────────────────────────────────────────────────
    with tab_registro:
        # Verificar sesión existente
        # 1. Obtener la fecha seleccionada primero
        today = datetime.date.today()
        
        # Card principal
        with st.container(border=True):
            st.markdown('<p class="att-card-title">Nueva Sesión de Clase</p>', unsafe_allow_html=True)

            col_fecha, col_area = st.columns(2)
            
            with col_fecha:
                st.markdown('<div class="field-label">Fecha de Sesión</div>', unsafe_allow_html=True)
                # Usamos key="fecha_sesion_input" para guardar el estado si es necesario
                fecha_sesion = st.date_input("Fecha", value=today, max_value=today, label_visibility="collapsed")
        
            if fecha_sesion.weekday() >= 5:
                st.error("❌ Los fines de semana no hay clases. Por favor, selecciona una fecha correcta (Lunes a Viernes).")
                st.stop()
                
            # 2. Verificar sesión existente para la fecha seleccionada
            asistencias_previas = {}
            id_sesion_actual = None
            
            sesion_existente = supabase.table("sesiones_clase") \
                .select("*").eq("id_aula", id_aula).eq("fecha", str(fecha_sesion)).execute()

            area_disabled = False
            if sesion_existente.data:
                ses = sesion_existente.data[0]
                id_sesion_actual = ses['id']
                area_sesion = ses['id_area']
                area_disabled = True
                res_asist = supabase.table("asistencias").select("*").eq("id_sesion", id_sesion_actual).execute()
                asistencias_previas = {a['id_alumno']: a['asistio'] for a in res_asist.data}

            with col_area:
                st.markdown('<div class="field-label">Área a evaluar</div>', unsafe_allow_html=True)
                if area_disabled:
                    area_seleccionada = st.selectbox(
                        "Área",
                        options=[area_sesion],
                        format_func=lambda x: areas_dict.get(x, ""),
                        disabled=True,
                        label_visibility="collapsed"
                    )
                else:
                    lista_areas_ids = list(areas_dict.keys())
                    default_area_index = 0
                    area_por_dia = {
                        0: "Personal Social",
                        1: "Psicomotriz",
                        2: "Comunicación",
                        3: "Matemática",
                        4: "Ciencia y tecnología"
                    }
                    nombre_esperado = area_por_dia.get(fecha_sesion.weekday())
                    if nombre_esperado:
                        for i, area_id in enumerate(lista_areas_ids):
                            import unicodedata
                            def normalize(s):
                                return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower()
                            
                            if normalize(areas_dict[area_id]) == normalize(nombre_esperado):
                                default_area_index = i
                                break
                                
                    area_seleccionada = st.selectbox(
                        "Área",
                        options=lista_areas_ids,
                        format_func=lambda x: areas_dict[x],
                        index=default_area_index,
                        label_visibility="collapsed"
                    )

            if area_disabled:
                st.info("⚠️ La asistencia de este día ya fue tomada. Si haces un cambio en este registro, se actualizará la asistencia de este día.")

        # ── FORM DE ASISTENCIA ────────────────────────────────────────────────
        with st.form("form_asistencia"):

            # Instrucción + contadores (se actualizan al guardar)
            st.markdown("""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span class="att-instruction">Desmarca a los alumnos que faltaron a clases hoy</span>
            </div>
            """, unsafe_allow_html=True)

            nuevas_asistencias = {}
            for alumno in alumnos:
                valor_por_defecto = asistencias_previas.get(alumno['id'], True)
                nombre_completo = f"{alumno['nombre']} {alumno['apellido']}"

                col_name, col_toggle = st.columns([5, 1])
                with col_name:
                    st.markdown(
                        f'<div class="student-name">{nombre_completo}</div>',
                        unsafe_allow_html=True
                    )
                with col_toggle:
                    asistio = st.toggle(
                        "Presente",
                        value=valor_por_defecto,
                        key=f"tog_{alumno['id']}",
                        label_visibility="collapsed"
                    )

                nuevas_asistencias[alumno['id']] = asistio

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<hr style='border:none;border-top:1px solid var(--line);margin:0 0 12px;'>", unsafe_allow_html=True)

            conforme = st.checkbox(
                "Declaro que el registro de asistencia es conforme y he terminado de pasar lista.",
                key="conforme_check"
            )

            # Cross-platform date format (%-d only works on Unix, not Windows)
            hoy_fmt = f"{today.day} {today.strftime('%b %Y')}"

            col_note, col_btn = st.columns([3, 1])
            with col_note:
                st.markdown(
                    f'<div class="att-footer-note">Se guardará para el Aula {aula_nombre} · {hoy_fmt}</div>',
                    unsafe_allow_html=True
                )
            with col_btn:
                submitted = st.form_submit_button(
                    "💾 Guardar Asistencia",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                if not conforme:
                    st.error("⚠️ Debes marcar la casilla de conformidad para poder guardar la asistencia.")
                else:
                    try:
                        if not id_sesion_actual:
                            res_ses = supabase.table("sesiones_clase").insert({
                                "id_aula": id_aula,
                                "fecha": str(fecha_sesion),
                                "id_area": area_seleccionada
                            }).execute()
                            id_sesion_actual = res_ses.data[0]['id']

                        supabase.table("asistencias").delete().eq("id_sesion", id_sesion_actual).execute()

                        datos_asistencia = [
                            {"id_sesion": id_sesion_actual, "id_alumno": al_id, "asistio": asis}
                            for al_id, asis in nuevas_asistencias.items()
                        ]
                        supabase.table("asistencias").insert(datos_asistencia).execute()

                        db_cache.clear_cache()
                        st.success("¡Asistencia guardada con éxito!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

    # ── TAB 2: HISTORIAL ──────────────────────────────────────────────────────
    with tab_historial:
        sesiones = supabase.table("sesiones_clase") \
            .select("*").eq("id_aula", id_aula).order("fecha", desc=True).execute()

        if not sesiones.data:
            st.info("No hay sesiones registradas en el historial.")
        else:
            dias_es = {
                "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
                "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
            }
            meses_es = {
                1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
                7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"
            }

            for s in sesiones.data:
                fecha_obj = datetime.date.fromisoformat(s['fecha'])
                dia_nombre = dias_es.get(fecha_obj.strftime("%A"), "")
                dia_num = fecha_obj.day
                mes = meses_es[fecha_obj.month]
                area_nombre = areas_dict.get(s['id_area'], 'Desconocida')

                with st.expander(f"📅  {dia_nombre} {dia_num:02d} {mes} — {area_nombre}"):
                    res_det = supabase.table("asistencias") \
                        .select("id_alumno, asistio").eq("id_sesion", s['id']).execute()

                    if res_det.data:
                        # Ordenar alumnos por apellido en historial también
                        alumnos_sorted = sorted(alumnos, key=lambda a: a.get('apellido', '').lower())
                        asistieron, faltaron = [], []
                        asis_map = {d['id_alumno']: d['asistio'] for d in res_det.data}

                        for a in alumnos_sorted:
                            nombre = f"{a['nombre']} {a['apellido']}"
                            if asis_map.get(a['id'], True):
                                asistieron.append(nombre)
                            else:
                                faltaron.append(nombre)

                        col_a, col_f = st.columns(2)
                        with col_a:
                            st.markdown(f"**✅ Presentes ({len(asistieron)})**")
                            for n in asistieron:
                                st.markdown(f"<span style='font-size:13px;color:var(--green);'>• {n}</span>", unsafe_allow_html=True)
                        with col_f:
                            st.markdown(f"**❌ Ausentes ({len(faltaron)})**")
                            if faltaron:
                                for n in faltaron:
                                    st.markdown(f"<span style='font-size:13px;color:var(--red);'>• {n}</span>", unsafe_allow_html=True)
                            else:
                                st.markdown("<span style='font-size:13px;color:var(--green);'>¡Asistencia perfecta!</span>", unsafe_allow_html=True)
                    else:
                        st.info("No hay detalle de asistencia para esta sesión.")


attendance_page()
