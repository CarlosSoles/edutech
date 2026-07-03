# Acompaña AI - MVP

Acompaña AI es una plataforma SaaS diseñada para resolver la alta carga administrativa y la dificultad de seguimiento individualizado que sufren las docentes de Educación Inicial (niños de 3 a 5 años).

El sistema automatiza el registro de evidencias (Cuaderno de Campo) extrayendo texto manuscrito mediante IA y asociándolo a las competencias del MINEDU.

## Arquitectura y Stack Tecnológico
*   **Frontend y Backend:** Streamlit (Python)
*   **Base de Datos y Almacenamiento:** Supabase (PostgreSQL y Storage)
*   **Pipeline de Inteligencia Artificial (Híbrido):**
    *   **Extracción Visual:** Gemini 1.5 Flash (Google AI Studio)
    *   **Estructuración y Evaluación:** Llama 3.1 (Groq Cloud API)
*   **Generación de Documentos:** python-docx, fpdf2

## Configuración del Proyecto

### 1. Requisitos Previos
Asegúrate de tener Python instalado en tu sistema.

### 2. Entorno Virtual
Este proyecto utiliza un entorno virtual llamado `edutech`. Para activarlo e instalar las dependencias, sigue estos pasos:

**Activar el entorno virtual:**
*   **En PowerShell (Recomendado en Windows / VS Code):**
    ```powershell
    .\edutech\Scripts\Activate.ps1
    ```
*   **En Símbolo del Sistema (CMD):**
    ```cmd
    .\edutech\Scripts\activate.bat
    ```

**Instalar dependencias:**
Una vez activado el entorno (verás `(edutech)` en tu terminal), instala los paquetes requeridos:
```bash
pip install -r requirements.txt
```

### 3. Variables de Entorno y Secretos
Las credenciales de las APIs no deben subirse a ningún repositorio. 
1. Abre el archivo `.streamlit/secrets.toml`.
2. Reemplaza los valores con tus llaves reales de Supabase, Gemini y Groq.

### 4. Ejecutar la Aplicación
Para levantar el servidor de desarrollo de Streamlit:
```bash
streamlit run app.py
```
