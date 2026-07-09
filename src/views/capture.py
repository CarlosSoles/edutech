import streamlit as st
from PIL import Image
import datetime
import streamlit.components.v1 as components
from src.core.agents import AgentGemini
from src.database.supabase_client import supabase
import src.utils.cache as db_cache
from src.utils.document_builder import generate_word_report

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

/* Apply Inter only to text elements — NOT to icon fonts */
body, p, span, div, label, input, textarea, select, td, th, li, a,
.stMarkdown, .stText, .element-container {
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 { font-family: 'Fraunces', serif !important; }

/* Page title */
.cap-title {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 28px;
    color: var(--ink);
    margin: 0 0 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.cap-subtitle {
    font-size: 13.5px;
    color: var(--ink-soft);
    margin: 0 0 20px;
    line-height: 1.5;
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
    margin-bottom: 14px;
}
.aula-chip-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--teal);
    flex-shrink: 0;
}

/* Status banners */
.banner {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 18px;
    border-radius: 10px;
    font-size: 13.5px;
    margin-bottom: 14px;
    line-height: 1.5;
}
.banner.success {
    background: var(--green-soft);
    border: 1px solid #b6dfc8;
    color: var(--green);
}
.banner.info {
    background: var(--blue-soft);
    border: 1px solid #bfdbfe;
    color: #1e40af;
}
.banner.warn {
    background: var(--amber-soft);
    border: 1px solid #f6d5a8;
    color: #92400e;
}
.banner-icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 15px;
}
.banner.success .banner-icon { background: var(--green); color: white; }
.banner.info .banner-icon { background: var(--blue); color: white; }
.banner.warn .banner-icon { background: var(--amber); color: white; }
.banner strong { font-weight: 700; }

/* Card title/subtitle for inside containers */
.cap-card-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 16px;
    color: var(--ink);
    margin: 0 0 6px;
}
.cap-card-sub {
    font-size: 12.5px;
    color: var(--ink-soft);
    margin: 0 0 16px;
}

/* ── st.container(border=True) → card look ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    border-color: var(--line) !important;
    box-shadow: var(--shadow) !important;
    padding: 20px 22px !important;
}

/* ── Native file uploader → custom drop zone look ── */
[data-testid="stFileUploader"] label { display: none !important; }

[data-testid="stFileUploaderDropzone"] {
    background: var(--bg) !important;
    border: 2px dashed #D5D9D3 !important;
    border-radius: 12px !important;
    min-height: 210px !important;
    padding: 32px 24px 20px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
}
[data-testid="stFileUploaderDropzone"] > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 4px !important;
    width: 100% !important;
}
[data-testid="stFileUploaderDropzone"] > div > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 2px !important;
    width: 100% !important;
}
/* Drag/drop text — only top-level spans, NOT spans inside the button */
[data-testid="stFileUploaderDropzone"] > div > div > span {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stFileUploaderDropzone"] small {
    font-size: 12px !important;
    color: var(--ink-soft) !important;
    text-align: center !important;
    line-height: 1.5 !important;
    display: block !important;
}
/* Button outer shell */
[data-testid="stFileUploaderDropzone"] > div > div > button {
    background: #E0E5E3 !important;
    border: 1px solid #D0D6D3 !important;
    border-radius: 8px !important;
    padding: 9px 22px !important;
    margin-top: 14px !important;
    cursor: pointer !important;
    transition: background .15s ease !important;
    position: relative !important;
    min-width: 120px !important;
}
[data-testid="stFileUploaderDropzone"] > div > div > button:hover {
    background: #D0D6D3 !important;
}
/* Hide EVERY native element inside the button (svg, span, p, div) */
[data-testid="stFileUploaderDropzone"] > div > div > button svg,
[data-testid="stFileUploaderDropzone"] > div > div > button span,
[data-testid="stFileUploaderDropzone"] > div > div > button p,
[data-testid="stFileUploaderDropzone"] > div > div > button div {
    display: none !important;
}

/* Sesiones list */
.session-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--line);
}
.session-row:last-child { border-bottom: none; }
.session-check {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 13px;
}
.session-check.done { background: var(--green); color: white; }
.session-check.pending { background: var(--amber-soft); color: var(--amber); border: 1.5px solid var(--amber); }
.session-info { flex: 1; }
.session-date { font-weight: 600; font-size: 13.5px; color: var(--ink); }
.session-meta { font-size: 12px; color: var(--ink-soft); }
.session-badge {
    font-size: 11.5px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
}
.session-badge.done { background: var(--green-soft); color: var(--green); }
.session-badge.pending { background: var(--amber-soft); color: var(--amber); }

/* Form section */
.form-section-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 15px;
    color: var(--ink);
    margin: 20px 0 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--line);
}

/* Override streamlit form border */
div[data-testid="stForm"] { border: none !important; padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── AUTH CHECK ────────────────────────────────────────────────────────────────
if "role" not in st.session_state or st.session_state.role != "docente":
    st.error("Acceso denegado. Solo para docentes.")
    st.stop()

docente_info = st.session_state.user_info
id_aula = docente_info.get('id_aula')
aula_data = docente_info.get('aulas')
aula_nombre = aula_data.get('nombre', 'Desconocida') if aula_data else 'Desconocida'
aula_edad = aula_data.get('edad', '?') if aula_data else '?'

if not id_aula:
    st.warning("No tienes un aula asignada. Pide al administrador que te asigne una.")
    st.stop()

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
st.markdown("""
<h1 class="cap-title">📒 Registro de Cuaderno de Campo</h1>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="aula-chip">
    <span class="aula-chip-dot"></span>
    Aula: {aula_nombre} ({aula_edad} años)
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p class="cap-subtitle">
    Sube la imagen de tu cuaderno de campo físico. La IA la transcribirá y organizará en la plantilla oficial.
</p>
""", unsafe_allow_html=True)

# ── CARGAR DATOS ──────────────────────────────────────────────────────────────
alumnos = db_cache.get_alumnos_by_aula(id_aula)
areas = db_cache.get_areas()

if not alumnos:
    st.warning("⚠️ No tienes alumnos matriculados en tu aula.")
    st.stop()
if not areas:
    st.warning("⚠️ El Administrador aún no ha registrado las Áreas curriculares.")
    st.stop()

alumnos_dict = {a['id']: f"{a['nombre']} {a['apellido']}" for a in alumnos}
areas_dict = {a['id']: a['nombre'] for a in areas}

# ── ESTADO DE SESSION ────────────────────────────────────────────────────────
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None
if "photo_id" not in st.session_state:
    st.session_state.photo_id = None
if "registro_guardado" not in st.session_state:
    st.session_state.registro_guardado = False

# ── SESIONES ──────────────────────────────────────────────────────────────────
sesiones = db_cache.get_sesiones_by_aula(id_aula)
cuadernos_db = db_cache.get_cuadernos_by_aula(id_aula)
pares_cuadernos = {(c['fecha'], c['id_area']) for c in cuadernos_db}
sesiones_faltantes = [s for s in sesiones if (s['fecha'], s['id_area']) not in pares_cuadernos]

# Sesiones de esta semana
hoy = datetime.date.today()
inicio_semana = hoy - datetime.timedelta(days=hoy.weekday())
sesiones_semana = [s for s in sesiones if datetime.date.fromisoformat(s['fecha']) >= inicio_semana]

# ── BANNERS DE ESTADO ─────────────────────────────────────────────────────────
if not sesiones_faltantes:
    st.markdown("""
    <div class="banner success">
        <div class="banner-icon">✓</div>
        <div><strong>¡Excelente!</strong> Tienes todos tus cuadernos de campo registrados para las sesiones dictadas.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="banner info">
    <div class="banner-icon">ℹ</div>
    <div>Para subir un nuevo registro, primero debes crear la sesión (pasar lista) en la pestaña de <strong>Asistencia</strong>.</div>
</div>
""", unsafe_allow_html=True)

# ── DOS COLUMNAS PRINCIPALES ──────────────────────────────────────────────────
col_left, col_right = st.columns([1.1, 1], gap="large")

# ── COLUMNA IZQUIERDA: SUBIR IMAGEN ──────────────────────────────────────────
with col_left:
    with st.container(border=True):
        st.markdown('<p class="cap-card-title">Subir imagen</p>', unsafe_allow_html=True)

        if not sesiones_faltantes:
            st.markdown("""
            <p class="cap-card-sub">
                No hay sesiones <span style="color:var(--amber);font-weight:600;">pendientes</span>
                de registro en este momento.
            </p>
            """, unsafe_allow_html=True)
            # Uploader deshabilitado — zona visual estilizada con CSS
            st.file_uploader(
                "Subir imagen del cuaderno",
                type=['jpg', 'jpeg', 'png'],
                disabled=True,
                label_visibility="collapsed"
            )

        else:
            opciones_sesiones = {
                s['id']: f"📅 {s['fecha']} — {areas_dict.get(s['id_area'], 'Desconocida')}"
                for s in sesiones_faltantes
            }
            sesion_seleccionada_id = st.selectbox(
                "Sesión pendiente",
                options=list(opciones_sesiones.keys()),
                format_func=lambda x: opciones_sesiones[x]
            )
            sesion_seleccionada = next(s for s in sesiones_faltantes if s['id'] == sesion_seleccionada_id)
            fecha_fija = datetime.datetime.strptime(sesion_seleccionada['fecha'], "%Y-%m-%d").date()
            area_fija = sesion_seleccionada['id_area']

            photo = st.file_uploader(
                "Subir imagen del cuaderno",
                type=['jpg', 'jpeg', 'png'],
                label_visibility="collapsed",
                disabled=st.session_state.registro_guardado
            )

            if photo:
                current_photo_id = f"{photo.name}_{photo.size}"
                if st.session_state.photo_id != current_photo_id:
                    st.session_state.photo_id = current_photo_id
                    st.session_state.parsed_data = None
                    st.session_state.registro_guardado = False
                
                btn_text = "Subir nueva imagen"
            else:
                st.session_state.photo_id = None
                st.session_state.parsed_data = None
                btn_text = "+ Elegir archivo"

            st.markdown(f"""
            <style>
            [data-testid="stFileUploaderDropzone"] > div > div > button::before {{
                content: "{btn_text}" !important;
                display: block !important;
                font-size: 13px !important;
                font-weight: 600 !important;
                color: #5B6B68 !important;
                font-family: 'Inter', sans-serif !important;
                white-space: nowrap !important;
            }}
            </style>
            """, unsafe_allow_html=True)

            if photo:
                if not st.session_state.parsed_data and not st.session_state.registro_guardado:
                    if st.button("Generar cuaderno de campo", type="primary", use_container_width=True):
                        with st.status("🧠 Procesando cuaderno de campo con IA...", expanded=True) as status:
                            try:
                                image = Image.open(photo)
                                st.write("🧠 Leyendo y organizando datos...")
                                agent = AgentGemini()
                                parsed_json = agent.process_cuaderno(image)
                                st.session_state.parsed_data = parsed_json
                                status.update(label="¡Plantilla generada exitosamente!", state="complete", expanded=False)
                            except Exception as e:
                                status.update(label="Error en el procesamiento", state="error")
                                st.error(str(e))
                                st.stop()

# ── COLUMNA DERECHA: SESIONES DE LA SEMANA ────────────────────────────────────
with col_right:
    with st.container(border=True):
        st.markdown("""
        <p class="cap-card-title">Sesiones de esta semana</p>
        <p class="cap-card-sub">Estado de los cuadernos de campo por sesión dictada.</p>
        """, unsafe_allow_html=True)

        if not sesiones_semana:
            st.markdown("""
            <p style="font-size:13px;color:var(--ink-soft);font-style:italic;margin:8px 0;">
                No hay sesiones registradas esta semana.
            </p>
            """, unsafe_allow_html=True)
        else:
            dias_es = {
                "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
                "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
            }
            meses_es = {
                1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
                7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"
            }

            rows_html = ""
            for s in sesiones_semana:
                fecha_obj = datetime.date.fromisoformat(s['fecha'])
                dia_nombre = dias_es[fecha_obj.strftime("%A")]
                dia_num = fecha_obj.day
                mes_nombre = meses_es[fecha_obj.month]
                es_registrada = (s['fecha'], s['id_area']) in pares_cuadernos
                n_alumnos = len(alumnos)

                if es_registrada:
                    check_class = "done"
                    check_icon = "✓"
                    badge_class = "done"
                    badge_text = "Registrado"
                else:
                    check_class = "pending"
                    check_icon = "!"
                    badge_class = "pending"
                    badge_text = "Pendiente"

                rows_html += f"""
                <div class="session-row">
                    <div class="session-check {check_class}">{check_icon}</div>
                    <div class="session-info">
                        <div class="session-date">{dia_nombre} {dia_num:02d} {mes_nombre}</div>
                        <div class="session-meta">Aula {aula_nombre} · {n_alumnos} alumnos</div>
                    </div>
                    <span class="session-badge {badge_class}">{badge_text}</span>
                </div>
                """

            st.markdown(rows_html, unsafe_allow_html=True)

# ── FORMULARIO DE VALIDACIÓN ──────────────────────────────────────────────────
if st.session_state.parsed_data and not st.session_state.registro_guardado:
    st.markdown("""
    <div style="margin-top:28px;">
        <div class="banner success">
            <div class="banner-icon">✨</div>
            <div><strong>Extracción exitosa.</strong> Por favor valida la plantilla antes de guardar.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    data = st.session_state.parsed_data

    with st.form("validation_form"):
        st.markdown('<div class="form-section-title">📋 Cabecera del instrumento de evaluación</div>', unsafe_allow_html=True)

        titulo_act = st.text_input("Título de la Actividad de Aprendizaje", value=data.get("titulo_actividad", ""))

        col1, col2 = st.columns(2)
        with col1:
            st.date_input("Fecha", value=fecha_fija, disabled=True)
        with col2:
            st.selectbox("Área", options=[area_fija], format_func=lambda x: areas_dict.get(x, ""), disabled=True)

        competencia = st.text_area("Competencia", value=data.get("competencia", ""), height=100)
        estandar = st.text_area("Estándar de Aprendizaje (Nivel de logro)", value=data.get("estandar", ""), height=150)
        capacidades = st.text_area("Capacidades", value=data.get("capacidades", ""), height=100)
        criterios = st.text_area("Criterios de Evaluación", value=data.get("criterios", ""), height=100)

        st.markdown('<div class="form-section-title">👧👦 Evidencias y Retroalimentación</div>', unsafe_allow_html=True)

        niños_evaluados = data.get("alumnos_evaluados", [])
        if not niños_evaluados:
            st.warning("La IA no detectó ningún niño en el texto. Puedes asignarlo manualmente.")
            niños_evaluados = [{"nombre_detectado": "", "descripcion": "", "retroalimentacion": ""}]

        evidencias_a_guardar = []
        import difflib
        for idx, niño in enumerate(niños_evaluados):
            nombre_detectado = niño.get('nombre_detectado', '')
            st.markdown(f"**Alumno {idx + 1}**")
            st.caption(f"🤖 Nombre detectado por la IA: **{nombre_detectado or 'No detectado'}**")

            # Buscar el índice del alumno que mejor coincida
            default_index = 0
            if nombre_detectado:
                nombres_list = list(alumnos_dict.values())
                nombre_lower = nombre_detectado.lower()
                match_found = False
                
                # 1. Búsqueda por subcadena
                for i, name in enumerate(nombres_list):
                    if nombre_lower in name.lower() or name.lower() in nombre_lower:
                        default_index = i
                        match_found = True
                        break
                        
                # 2. Búsqueda difusa (fuzzy) si no hay coincidencia
                if not match_found:
                    matches = difflib.get_close_matches(nombre_detectado, nombres_list, n=1, cutoff=0.3)
                    if matches:
                        default_index = nombres_list.index(matches[0])

            id_alumno = st.selectbox(
                f"Selecciona al alumno {idx+1}:",
                options=list(alumnos_dict.keys()),
                format_func=lambda x: alumnos_dict[x],
                index=default_index,
                key=f"al_sel_{idx}"
            )
            desc = st.text_area(f"Descripción de evidencias", value=niño.get("descripcion", ""), height=100, key=f"desc_{idx}")
            retro = st.text_area(f"Aspectos a retroalimentar", value=niño.get("retroalimentacion", ""), height=100, key=f"retro_{idx}")

            evidencias_a_guardar.append({"id_alumno": id_alumno, "descripcion": desc, "retroalimentacion": retro})
            st.markdown("<br>", unsafe_allow_html=True)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("✅ Aprobar y Guardar", type="primary", use_container_width=True)
        with col_btn2:
            discarded = st.form_submit_button("❌ Descartar Registro", type="secondary", use_container_width=True)

        if discarded:
            st.session_state.parsed_data = None
            st.session_state.photo_id = None
            st.rerun()

        if submitted:
            try:
                cabecera_data = {
                    "id_docente": docente_info['id'],
                    "id_aula": id_aula,
                    "titulo_actividad": titulo_act,
                    "fecha": str(fecha_fija),
                    "id_area": area_fija,
                    "competencia": competencia,
                    "estandar": estandar,
                    "capacidades": capacidades,
                    "criterios": criterios
                }
                res_cabecera = supabase.table("cuadernos_campo").insert(cabecera_data).execute()
                id_cuaderno = res_cabecera.data[0]['id']

                detalles_insert = [
                    {
                        "id_cuaderno": id_cuaderno,
                        "id_alumno": ev["id_alumno"],
                        "descripcion": ev["descripcion"],
                        "retroalimentacion": ev["retroalimentacion"]
                    }
                    for ev in evidencias_a_guardar
                ]
                supabase.table("evidencias_alumnos").insert(detalles_insert).execute()

                doc_data = {
                    "titulo": titulo_act,
                    "fecha": fecha_fija.strftime("%d/%m/%Y"),
                    "aula": aula_nombre,
                    "edad": aula_edad,
                    "area": areas_dict.get(area_fija, ""),
                    "competencia": competencia,
                    "estandar": estandar,
                    "capacidades": capacidades,
                    "criterios": criterios
                }
                niños_data = [
                    {
                        "nombre": alumnos_dict.get(ev["id_alumno"], "Desconocido"),
                        "descripcion": ev["descripcion"],
                        "retroalimentacion": ev["retroalimentacion"]
                    }
                    for ev in evidencias_a_guardar
                ]
                st.session_state.word_bytes = generate_word_report(doc_data, niños_data)
                st.session_state.registro_guardado = True
                st.rerun()

            except Exception as e:
                st.error(f"Error al guardar en base de datos: {e}")

# ── REGISTRO GUARDADO ─────────────────────────────────────────────────────────
if st.session_state.registro_guardado:
    st.markdown("""
    <div class="banner success" style="margin-top:20px;">
        <div class="banner-icon">🎉</div>
        <div><strong>¡Cuaderno guardado exitosamente!</strong> Descarga el reporte oficial en formato Word.</div>
    </div>
    """, unsafe_allow_html=True)

    col_dl, col_new = st.columns(2)
    with col_dl:
        st.download_button(
            "📄 Descargar Plantilla Oficial (Word)",
            data=st.session_state.word_bytes,
            file_name="Cuaderno_Campo.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            type="primary"
        )
    with col_new:
        if st.button("🔄 Subir nuevo cuaderno", use_container_width=True):
            st.session_state.parsed_data = None
            st.session_state.photo_id = None
            st.session_state.registro_guardado = False
            st.rerun()
