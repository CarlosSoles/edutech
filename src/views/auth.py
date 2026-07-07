import streamlit as st
from src.database.supabase_client import supabase
from src.utils.helpers import upload_profile_picture

# Si el usuario ya inició sesión, mostramos la pantalla de perfil/cerrar sesión
if st.session_state.get("logged_in"):
    st.title("👤 Mi Perfil")
    st.success(f"Sesión activa. Rol: **{st.session_state.role.capitalize()}**")
    
    if st.session_state.role == "docente" and "user_info" in st.session_state:
        user = st.session_state.user_info
        aula_data = user.get('aulas')
        aula_nombre = aula_data.get('nombre', 'No asignada') if aula_data else 'No asignada'
        aula_edad = aula_data.get('edad', '?') if aula_data else '?'
        
        with st.container(border=True):
            colA, colB = st.columns([1, 3])
            
            with colA:
                # Mostrar foto actual si existe
                if user.get("foto_perfil"):
                    st.image(user["foto_perfil"], width=150)
                else:
                    st.info("Sin foto de perfil")
                    
            with colB:
                st.write(f"**Docente:** {user.get('nombre')} {user.get('apellido')}")
                st.write(f"**Usuario:** @{user.get('username')}")
                st.write(f"**Aula asignada:** {aula_nombre} ({aula_edad} años)")
                
                # Formulario para cambiar foto de perfil
                with st.expander("Actualizar foto de perfil"):
                    with st.form("form_cambiar_foto"):
                        nueva_foto = st.file_uploader("Selecciona una nueva foto", type=["jpg", "png", "jpeg"])
                        if st.form_submit_button("Subir Foto", type="primary"):
                            if nueva_foto:
                                with st.spinner("Subiendo foto..."):
                                    try:
                                        url = upload_profile_picture(nueva_foto.getvalue(), nueva_foto.name, "docentes")
                                        supabase.table("docentes").update({"foto_perfil": url}).eq("id", user["id"]).execute()
                                        st.session_state.user_info["foto_perfil"] = url
                                        st.success("¡Foto actualizada!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error al subir la foto: {e}")
                            else:
                                st.warning("Selecciona una foto primero.")

    st.stop()

# ==========================================
# INTERFAZ DE LOGIN (Centrada y moderna)
# ==========================================
st.markdown("<br><br>", unsafe_allow_html=True) # Espacio superior
_, col_centro, _ = st.columns([1.5, 2, 1.5])

with col_centro:
    # Centrar el logo
    _, col_logo, _ = st.columns([1, 1.2, 1])
    with col_logo:
        st.image("src/views/img/logoKubiAI.png", width='stretch')
        
    st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 25px;'>Transformando apuntes en seguimiento inteligente</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        tab1, tab2 = st.tabs(["👩‍🏫 Soy Docente", "⚙️ Administrador"])
        
        # Login de Docente
        with tab1:
            with st.form("login_docente"):
                username = st.text_input("Usuario", placeholder="Ej: docente1")
                password = st.text_input("Contraseña", type="password", placeholder="••••••••")
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Ingresar a mi aula", type="primary", width='stretch')
                
                if submit:
                    if username and password:
                        try:
                            response = supabase.table("docentes").select("*, aulas(nombre, edad)").eq("username", username).eq("password", password).execute()
                            if response.data and len(response.data) > 0:
                                user_data = response.data[0]
                                st.session_state.logged_in = True
                                st.session_state.role = "docente"
                                st.session_state.user_info = user_data
                                st.switch_page("src/views/dashboard.py")
                            else:
                                st.error("Usuario o contraseña incorrectos.")
                        except Exception as e:
                            st.error(f"Error de conexión con la base de datos: {e}")
                    else:
                        st.warning("Por favor, completa ambos campos.")

        # Login de Administrador
        with tab2:
            with st.form("login_admin"):
                admin_pass = st.text_input("Contraseña Maestra", type="password", placeholder="••••••••")
                st.markdown("<br>", unsafe_allow_html=True)
                submit_admin = st.form_submit_button("Acceso Administrativo", width='stretch')
                
                if submit_admin:
                    if admin_pass == "admin2026":
                        st.session_state.logged_in = True
                        st.session_state.role = "admin"
                        st.session_state.user_info = {"nombre": "Administrador Principal"}
                        st.switch_page("src/views/admin_dashboard.py")
                    else:
                        st.error("Contraseña incorrecta.")
