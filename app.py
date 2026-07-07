import streamlit as st

def main():
    st.set_page_config(page_title="Kubi AI", layout="wide")
    
    st.logo("src/views/img/logoKubiAI.png")
    
    # CSS para agregar el texto al costado del logo
    st.markdown(
        """
        <style>
        [data-testid="stSidebarHeader"] {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
        }
        [data-testid="stSidebarHeader"]::after {
            content: "Kubi AI";
            font-size: 26px;
            font-weight: 800;
            color: #0f172a;
            margin-left: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize session state for authentication
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "role" not in st.session_state:
        st.session_state.role = None
        
    pages = {}
    
    if not st.session_state.logged_in:
        # If not logged in, only show the Auth page
        pages["Acceso"] = [st.Page("src/views/auth.py", title="Iniciar Sesión", icon="🔐")]
    else:
        # If logged in as admin
        if st.session_state.role == "admin":
            pages["Administración"] = [st.Page("src/views/admin_dashboard.py", title="Dashboard Admin", icon="⚙️")]
        
        # If logged in as docente
        elif st.session_state.role == "docente":
            pages["Mi Aula"] = [
                st.Page("src/views/dashboard.py", title="Inicio", icon="🏠"),
                st.Page("src/views/capture.py", title="Nuevo Registro", icon="📷"),
                st.Page("src/views/history.py", title="Mis Registros", icon="📚"),
                st.Page("src/views/attendance.py", title="Asistencia", icon="✅"),
                st.Page("src/views/advisor.py", title="Asesor Pedagógico", icon="🤖"),
            ]
            
            pages["Cuenta"] = [
                st.Page("src/views/auth.py", title="Mi Perfil", icon="👤"),
                st.Page("src/views/logout.py", title="Cerrar Sesión", icon="🚪")
            ]
        
    # Execute the new native navigation API
    pg = st.navigation(pages)
    
    # Manejar redirecciones de manera segura usando objetos st.Page
    if st.session_state.get("redirect_to"):
        target_title = st.session_state.redirect_to
        st.session_state.redirect_to = None
        for group, page_list in pages.items():
            for p in page_list:
                if p.title == target_title:
                    st.switch_page(p)
                    break
                    
    pg.run()
    
if __name__ == "__main__":
    main()
