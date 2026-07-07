import streamlit as st
from src.database.supabase_client import supabase
from src.utils.helpers import upload_profile_picture

if st.session_state.get("role") != "admin":
    st.error("Acceso denegado. Se requieren privilegios de administrador.")
    st.stop()

st.title("⚙️ Panel de Administración")
st.write("Gestión centralizada de Áreas, Aulas, Docentes y Alumnos.")

def fetch_areas():
    res = supabase.table("areas").select("*").execute()
    return res.data

def fetch_aulas():
    res = supabase.table("aulas").select("*").execute()
    return res.data

def fetch_docentes():
    res = supabase.table("docentes").select("*, aulas(nombre, edad)").execute()
    return res.data

def fetch_alumnos():
    res = supabase.table("alumnos").select("*, aulas(nombre, edad)").execute()
    return res.data

tab_areas, tab_aulas, tab_docentes, tab_alumnos = st.tabs(["📚 Áreas", "🏫 Aulas", "👩‍🏫 Docentes", "👶 Alumnos"])

# ==========================================
# GESTIÓN DE ÁREAS
# ==========================================
with tab_areas:
    st.subheader("Gestión de Áreas Curriculares")
    modo_area = st.radio("Acción:", ["Crear Nueva Área", "Ver/Editar/Eliminar"], horizontal=True, key="radio_areas")
    
    if modo_area == "Crear Nueva Área":
        with st.form("form_crear_area"):
            nombre_area = st.text_input("Nombre del Área (Ej. Matemática)")
            if st.form_submit_button("Crear Área", type="primary"):
                if nombre_area:
                    try:
                        supabase.table("areas").insert({"nombre": nombre_area}).execute()
                        st.success(f"Área '{nombre_area}' creada exitosamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error (Podría ser un nombre duplicado): {e}")
                else:
                    st.warning("El nombre es obligatorio.")
    else:
        areas = fetch_areas()
        if areas:
            area_ids = {a['id']: a['nombre'] for a in areas}
            area_a_editar = st.selectbox("Selecciona un área:", options=list(area_ids.keys()), format_func=lambda x: area_ids[x])
            
            area_data = next((a for a in areas if a['id'] == area_a_editar), None)
            if area_data:
                with st.form("form_editar_area"):
                    nuevo_nombre_area = st.text_input("Nombre del Área", value=area_data['nombre'])
                    col1, col2 = st.columns(2)
                    with col1:
                        btn_guardar_area = st.form_submit_button("💾 Guardar Cambios")
                    with col2:
                        btn_eliminar_area = st.form_submit_button("🗑️ Eliminar Área")
                        
                    if btn_guardar_area:
                        try:
                            supabase.table("areas").update({"nombre": nuevo_nombre_area}).eq("id", area_a_editar).execute()
                            st.success("Cambios guardados.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if btn_eliminar_area:
                        try:
                            supabase.table("areas").delete().eq("id", area_a_editar).execute()
                            st.success("Área eliminada.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar: {e}")
        else:
            st.info("No hay áreas creadas.")

# ==========================================
# GESTIÓN DE AULAS
# ==========================================
with tab_aulas:
    st.subheader("Gestión de Aulas")
    modo_aula = st.radio("Acción:", ["Crear Nueva Aula", "Ver/Editar/Eliminar"], horizontal=True)
    
    if modo_aula == "Crear Nueva Aula":
        with st.form("form_crear_aula"):
            nombre_aula = st.text_input("Nombre del Aula (Ej. Los Ositos)")
            edad_aula = st.selectbox("Edad correspondiente", [3, 4, 5])
            if st.form_submit_button("Crear Aula", type="primary"):
                if nombre_aula:
                    try:
                        supabase.table("aulas").insert({"nombre": nombre_aula, "edad": edad_aula}).execute()
                        st.success(f"Aula '{nombre_aula}' creada exitosamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("El nombre es obligatorio.")
                    
    else:
        aulas = fetch_aulas()
        if aulas:
            aula_ids = {a['id']: f"{a['nombre']} ({a['edad']} años)" for a in aulas}
            aula_a_editar = st.selectbox("Selecciona un aula:", options=list(aula_ids.keys()), format_func=lambda x: aula_ids[x])
            
            aula_data = next((a for a in aulas if a['id'] == aula_a_editar), None)
            if aula_data:
                with st.form("form_editar_aula"):
                    nuevo_nombre = st.text_input("Nombre del Aula", value=aula_data['nombre'])
                    nueva_edad = st.selectbox("Edad", [3, 4, 5], index=[3,4,5].index(aula_data['edad']))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        btn_guardar = st.form_submit_button("💾 Guardar Cambios")
                    with col2:
                        btn_eliminar = st.form_submit_button("🗑️ Eliminar Aula")
                        
                    if btn_guardar:
                        try:
                            supabase.table("aulas").update({"nombre": nuevo_nombre, "edad": nueva_edad}).eq("id", aula_a_editar).execute()
                            st.success("Cambios guardados.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                            
                    if btn_eliminar:
                        try:
                            supabase.table("aulas").delete().eq("id", aula_a_editar).execute()
                            st.success("Aula eliminada.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar: {e}")
        else:
            st.info("No hay aulas creadas.")

# ==========================================
# GESTIÓN DE DOCENTES
# ==========================================
with tab_docentes:
    st.subheader("Gestión de Docentes")
    aulas = fetch_aulas()
    if not aulas:
        st.warning("Debes crear al menos un Aula antes de registrar docentes.")
    else:
        aula_opciones = {a['id']: f"{a['nombre']} ({a['edad']} años)" for a in aulas}
        
        modo_docente = st.radio("Acción:", ["Registrar Nueva Docente", "Ver/Editar/Eliminar"], horizontal=True, key="radio_docentes")
        
        if modo_docente == "Registrar Nueva Docente":
            with st.form("form_crear_docente"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre = st.text_input("Nombre(s)")
                    username = st.text_input("Nombre de Usuario (Único)")
                    id_aula = st.selectbox("Asignar Aula", options=list(aula_opciones.keys()), format_func=lambda x: aula_opciones[x])
                with col2:
                    apellido = st.text_input("Apellido(s)")
                    password = st.text_input("Contraseña temporal", type="password")
                
                if st.form_submit_button("Registrar Docente", type="primary"):
                    if nombre and apellido and username and password:
                        try:
                            data = {
                                "nombre": nombre, "apellido": apellido,
                                "id_aula": id_aula, "username": username, "password": password
                            }
                            supabase.table("docentes").insert(data).execute()
                            st.success(f"Docente {nombre} registrada.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error (Verifica que el usuario sea único): {e}")
                    else:
                        st.warning("Completa todos los campos.")
                        
        else:
            docentes = fetch_docentes()
            if docentes:
                docente_ids = {d['id']: f"{d['nombre']} {d['apellido']} - {d['aulas']['nombre'] if d.get('aulas') else 'Sin Aula'}" for d in docentes}
                docente_a_editar = st.selectbox("Selecciona una docente:", options=list(docente_ids.keys()), format_func=lambda x: docente_ids[x])
                
                doc_data = next((d for d in docentes if d['id'] == docente_a_editar), None)
                if doc_data:
                    if doc_data.get("foto_perfil"):
                        st.image(doc_data["foto_perfil"], width=100, caption="Foto Actual")
                    
                    with st.form("form_editar_docente"):
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_nombre = st.text_input("Nombre", value=doc_data['nombre'])
                            edit_user = st.text_input("Usuario", value=doc_data['username'])
                            current_aula_index = list(aula_opciones.keys()).index(doc_data['id_aula']) if doc_data['id_aula'] in aula_opciones else 0
                            edit_aula = st.selectbox("Aula", options=list(aula_opciones.keys()), format_func=lambda x: aula_opciones[x], index=current_aula_index)
                        with col2:
                            edit_apellido = st.text_input("Apellido", value=doc_data['apellido'])
                            edit_pass = st.text_input("Nueva Contraseña (dejar en blanco para no cambiar)", type="password")
                            edit_foto = st.file_uploader("Actualizar Foto de Perfil", type=["jpg", "png", "jpeg"])
                            
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            btn_guardar_doc = st.form_submit_button("💾 Guardar Cambios")
                        with col_btn2:
                            btn_eliminar_doc = st.form_submit_button("🗑️ Eliminar Docente")
                            
                        if btn_guardar_doc:
                            try:
                                update_data = {
                                    "nombre": edit_nombre, "apellido": edit_apellido,
                                    "username": edit_user, "id_aula": edit_aula
                                }
                                if edit_pass:
                                    update_data["password"] = edit_pass
                                    
                                if edit_foto:
                                    url = upload_profile_picture(edit_foto.getvalue(), edit_foto.name, "docentes")
                                    update_data["foto_perfil"] = url
                                    
                                supabase.table("docentes").update(update_data).eq("id", docente_a_editar).execute()
                                st.success("Docente actualizada.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                                
                        if btn_eliminar_doc:
                            try:
                                supabase.table("docentes").delete().eq("id", docente_a_editar).execute()
                                st.success("Docente eliminada.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al eliminar: {e}")
            else:
                st.info("No hay docentes registradas.")

# ==========================================
# GESTIÓN DE ALUMNOS
# ==========================================
with tab_alumnos:
    st.subheader("Gestión de Alumnos")
    if not aulas:
        st.warning("Debes crear al menos un Aula antes de matricular alumnos.")
    else:
        modo_alumno = st.radio("Acción:", ["Matricular Nuevo Alumno", "Ver/Editar/Eliminar"], horizontal=True, key="radio_alumnos")
        
        if modo_alumno == "Matricular Nuevo Alumno":
            with st.form("form_crear_alumno"):
                col3, col4 = st.columns(2)
                with col3:
                    nombre_al = st.text_input("Nombre del Alumno")
                    fecha_nac = st.date_input("Fecha de Nacimiento")
                with col4:
                    apellido_al = st.text_input("Apellido del Alumno")
                    id_aula_al = st.selectbox("Aula Asignada", options=list(aula_opciones.keys()), format_func=lambda x: aula_opciones[x], key="aula_nuevo_al")
                    
                if st.form_submit_button("Registrar Alumno", type="primary"):
                    if nombre_al and apellido_al:
                        try:
                            data = {
                                "nombre": nombre_al, "apellido": apellido_al,
                                "fecha_nacimiento": str(fecha_nac), "id_aula": id_aula_al
                            }
                            supabase.table("alumnos").insert(data).execute()
                            st.success(f"Alumno {nombre_al} matriculado.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Completa los campos de nombre y apellido.")
                        
        else:
            alumnos = fetch_alumnos()
            if alumnos:
                aula_filtro = st.selectbox("Filtro rápido por Aula:", options=["Todas"] + list(aula_opciones.keys()), format_func=lambda x: "Ver Todas" if x == "Todas" else aula_opciones[x])
                
                alumnos_filtrados = alumnos
                if aula_filtro != "Todas":
                    alumnos_filtrados = [a for a in alumnos if a['id_aula'] == aula_filtro]
                
                if alumnos_filtrados:
                    alumno_ids = {a['id']: f"{a['nombre']} {a['apellido']} - {a['aulas']['nombre'] if a.get('aulas') else 'Sin Aula'}" for a in alumnos_filtrados}
                    alumno_a_editar = st.selectbox("Selecciona un alumno:", options=list(alumno_ids.keys()), format_func=lambda x: alumno_ids[x])
                    
                    al_data = next((a for a in alumnos if a['id'] == alumno_a_editar), None)
                    if al_data:
                        if al_data.get("foto_perfil"):
                            st.image(al_data["foto_perfil"], width=100, caption="Foto Actual")
                            
                        with st.form("form_editar_alumno"):
                            col3, col4 = st.columns(2)
                            import datetime
                            with col3:
                                edit_nombre_al = st.text_input("Nombre", value=al_data['nombre'])
                                fecha_obj = datetime.datetime.strptime(al_data['fecha_nacimiento'], "%Y-%m-%d").date() if al_data.get('fecha_nacimiento') else datetime.date.today()
                                edit_fecha_al = st.date_input("Fecha de Nacimiento", value=fecha_obj)
                            with col4:
                                edit_apellido_al = st.text_input("Apellido", value=al_data['apellido'])
                                current_aula_al_index = list(aula_opciones.keys()).index(al_data['id_aula']) if al_data['id_aula'] in aula_opciones else 0
                                edit_aula_al = st.selectbox("Aula", options=list(aula_opciones.keys()), format_func=lambda x: aula_opciones[x], index=current_aula_al_index, key="edit_aula_al")
                                edit_foto_al = st.file_uploader("Actualizar Foto de Perfil", type=["jpg", "png", "jpeg"])
                                
                            col_btn3, col_btn4 = st.columns(2)
                            with col_btn3:
                                btn_guardar_al = st.form_submit_button("💾 Guardar Cambios")
                            with col_btn4:
                                btn_eliminar_al = st.form_submit_button("🗑️ Eliminar Alumno")
                                
                            if btn_guardar_al:
                                try:
                                    update_data = {
                                        "nombre": edit_nombre_al, "apellido": edit_apellido_al,
                                        "fecha_nacimiento": str(edit_fecha_al), "id_aula": edit_aula_al
                                    }
                                    if edit_foto_al:
                                        url = upload_profile_picture(edit_foto_al.getvalue(), edit_foto_al.name, "alumnos")
                                        update_data["foto_perfil"] = url
                                        
                                    supabase.table("alumnos").update(update_data).eq("id", alumno_a_editar).execute()
                                    st.success("Alumno actualizado.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                                    
                            if btn_eliminar_al:
                                try:
                                    supabase.table("alumnos").delete().eq("id", alumno_a_editar).execute()
                                    st.success("Alumno eliminado.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error al eliminar: {e}")
                else:
                    st.info("No hay alumnos en el aula seleccionada.")
            else:
                st.info("No hay alumnos matriculados.")
