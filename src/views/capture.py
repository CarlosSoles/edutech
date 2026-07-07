import streamlit as st
from PIL import Image
import datetime
from src.core.agents import AgentGemini
from src.database.supabase_client import supabase
from src.utils.document_builder import generate_word_report

st.title("📸 Registro de Cuaderno de Campo")

if "role" not in st.session_state or st.session_state.role != "docente":
    st.error("Acceso denegado. Solo para docentes.")
    st.stop()

docente_info = st.session_state.user_info
id_aula = docente_info.get('id_aula')
aula_data = docente_info.get('aulas')
aula_nombre = aula_data.get('nombre', 'Desconocida') if aula_data else 'Desconocida'
aula_edad = aula_data.get('edad', '?') if aula_data else '?'

st.write(f"**Aula:** {aula_nombre} ({aula_edad} AÑOS)")
st.write("Sube la imagen de tu cuaderno de campo físico. La IA la transcribirá y organizará en la plantilla oficial.")

if not id_aula:
    st.warning("No tienes un aula asignada. Pide al administrador que te asigne una.")
    st.stop()

# Cargar dependencias (Áreas y Alumnos)
@st.cache_data(ttl=60)
def cargar_alumnos(aula_id):
    try:
        res = supabase.table("alumnos").select("*").eq("id_aula", aula_id).execute()
        return res.data
    except Exception as e:
        return []

@st.cache_data(ttl=60)
def cargar_areas():
    try:
        res = supabase.table("areas").select("*").execute()
        return res.data
    except Exception as e:
        return []

alumnos = cargar_alumnos(id_aula)
areas = cargar_areas()

if not alumnos:
    st.warning("⚠️ No tienes alumnos matriculados en tu aula.")
    st.stop()
if not areas:
    st.warning("⚠️ El Administrador aún no ha registrado las Áreas curriculares.")
    st.stop()

alumnos_dict = {a['id']: f"{a['nombre']} {a['apellido']}" for a in alumnos}
areas_dict = {a['id']: a['nombre'] for a in areas}

# Manejo de estado
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None
if "photo_id" not in st.session_state:
    st.session_state.photo_id = None
if "registro_guardado" not in st.session_state:
    st.session_state.registro_guardado = False

# --- LOGICA DE SESIONES PENDIENTES ---
sesiones = supabase.table("sesiones_clase").select("*").eq("id_aula", id_aula).order("fecha", desc=True).execute().data
cuadernos = supabase.table("cuadernos_campo").select("fecha, id_area").eq("id_aula", id_aula).execute().data

pares_cuadernos = {(c['fecha'], c['id_area']) for c in cuadernos}
sesiones_faltantes = [s for s in sesiones if (s['fecha'], s['id_area']) not in pares_cuadernos]

if not sesiones_faltantes:
    st.success("🎉 ¡Excelente! Tienes todos tus cuadernos de campo registrados para las sesiones dictadas.")
    st.info("Para subir un nuevo registro, primero debes crear la sesión (pasar lista) en la pestaña de **Asistencia**.")
    st.stop()

st.write("Selecciona la sesión de clase que vas a registrar (solo aparecen las sesiones con asistencia tomada pero sin cuaderno):")
opciones_sesiones = {s['id']: f"📅 {s['fecha']} - Área: {areas_dict.get(s['id_area'], 'Desconocido')}" for s in sesiones_faltantes}

sesion_seleccionada_id = st.selectbox("Sesión Pendiente", options=list(opciones_sesiones.keys()), format_func=lambda x: opciones_sesiones[x])
sesion_seleccionada = next(s for s in sesiones_faltantes if s['id'] == sesion_seleccionada_id)

fecha_fija = datetime.datetime.strptime(sesion_seleccionada['fecha'], "%Y-%m-%d").date()
area_fija = sesion_seleccionada['id_area']

photo = st.file_uploader("Subir foto del Cuaderno de Campo", type=['jpg', 'jpeg', 'png'])

if photo:
    current_photo_id = f"{photo.name}_{photo.size}"
    if st.session_state.photo_id != current_photo_id:
        st.session_state.photo_id = current_photo_id
        st.session_state.parsed_data = None
        st.session_state.registro_guardado = False
        
        with st.status("🧠 Procesando cuaderno de campo con Inteligencia Artificial...", expanded=True) as status:
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

if st.session_state.parsed_data and not st.session_state.registro_guardado:
    st.success("✨ Extracción exitosa. Por favor valida la plantilla antes de guardar.")
    
    data = st.session_state.parsed_data

    with st.form("validation_form"):
        st.markdown("### 📋 CABECERA DEL INSTRUMENTO DE EVALUACIÓN")
        
        titulo_act = st.text_input("Título de la Actividad de Aprendizaje", value=data.get("titulo_actividad", ""))
        
        col1, col2 = st.columns(2)
        with col1:
            st.date_input("Fecha", value=fecha_fija, disabled=True)
        with col2:
            st.selectbox("Área", options=[area_fija], format_func=lambda x: areas_dict.get(x, ""), disabled=True)
            
        competencia = st.text_area("COMPETENCIA", value=data.get("competencia", ""), height=100)
        estandar = st.text_area("ESTÁNDAR DE APRENDIZAJE (Nivel de logro)", value=data.get("estandar", ""), height=150)
        capacidades = st.text_area("CAPACIDADES", value=data.get("capacidades", ""), height=100)
        criterios = st.text_area("CRITERIOS DE EVALUACIÓN", value=data.get("criterios", ""), height=100)
        
        st.markdown("---")
        st.markdown("### 👧👦 EVIDENCIAS Y RETROALIMENTACIÓN (NIÑOS EVALUADOS)")
        
        niños_evaluados = data.get("alumnos_evaluados", [])
        if not niños_evaluados:
            st.warning("La IA no detectó ningún niño en el texto. Puedes asignarlo manualmente.")
            niños_evaluados = [{"nombre_detectado": "", "descripcion": "", "retroalimentacion": ""}]
            
        # Almacenaremos los datos de los niños en un diccionario temporal
        evidencias_a_guardar = []
        
        for idx, niño in enumerate(niños_evaluados):
            st.markdown(f"#### Alumno {idx + 1}")
            st.caption(f"🤖 Nombre detectado por la IA: **{niño.get('nombre_detectado', 'No detectado')}**")
            
            id_alumno = st.selectbox(
                f"Selecciona al alumno {idx+1} de tu lista:", 
                options=list(alumnos_dict.keys()), 
                format_func=lambda x: alumnos_dict[x],
                key=f"al_sel_{idx}"
            )
            
            desc = st.text_area(f"Descripción de Evidencias (Alumno {idx+1})", value=niño.get("descripcion", ""), height=100, key=f"desc_{idx}")
            retro = st.text_area(f"Aspectos a Retroalimentar (Alumno {idx+1})", value=niño.get("retroalimentacion", ""), height=100, key=f"retro_{idx}")
            
            evidencias_a_guardar.append({
                "id_alumno": id_alumno,
                "descripcion": desc,
                "retroalimentacion": retro
            })
            st.markdown("<br>", unsafe_allow_html=True)
            
        submitted = st.form_submit_button("✅ Aprobar y Guardar Cuaderno de Campo", type="primary")
        
        if submitted:
            try:
                # 1. Insertar Cabecera
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
                
                # 2. Insertar Detalles (Niños)
                detalles_insert = []
                for ev in evidencias_a_guardar:
                    detalles_insert.append({
                        "id_cuaderno": id_cuaderno,
                        "id_alumno": ev["id_alumno"],
                        "descripcion": ev["descripcion"],
                        "retroalimentacion": ev["retroalimentacion"]
                    })
                supabase.table("evidencias_alumnos").insert(detalles_insert).execute()
                
                # 3. Generar documentos en memoria
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
                
                st.success("🎉 ¡Cuaderno de campo guardado exitosamente!")
                st.session_state.registro_guardado = True
                st.rerun()
                
            except Exception as e:
                st.error(f"Error al guardar en base de datos: {e}")

if st.session_state.registro_guardado:
    st.info("El documento ha sido guardado. Desde aquí podrás generar el reporte oficial.")
    
    st.download_button("📄 Descargar Plantilla Oficial (Word)", data=st.session_state.word_bytes, file_name="Cuaderno_Campo.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", width='stretch')
            
    if st.button("🔄 Subir nuevo cuaderno"):
        st.session_state.parsed_data = None
        st.session_state.photo_id = None
        st.session_state.registro_guardado = False
        st.rerun()
