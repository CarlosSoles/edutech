# Kubi AI - MVP (Hackathon)

**Kubi AI** es una plataforma SaaS inteligente diseñada para resolver la alta carga administrativa y la dificultad del seguimiento individualizado que sufren las docentes de Educación Inicial (niños de 3 a 5 años). 

El sistema digitaliza el proceso pedagógico mediante una arquitectura de Inteligencia Artificial que no solo extrae datos manuscritos de los cuadernos de campo (anecdotarios), sino que también los estructura en rúbricas oficiales (MINEDU), mide el progreso cualitativo del niño a través del tiempo, y sugiere dinámicas personalizadas de intervención.

## Arquitectura y Stack Tecnológico

El sistema fue construido pensando en la escalabilidad, la velocidad de procesamiento y la mejor experiencia de usuario para las docentes:

*   **Frontend y Lógica de Interfaz:** Streamlit (Python) - *Manejo de estados de sesión, subida de evidencias y generación de dashboards interactivos y visuales.*
*   **Base de Datos y Almacenamiento (BaaS):** Supabase (PostgreSQL y Storage) - *Manejo relacional de alumnos, asistencia obligatoria, registros diarios y almacenamiento seguro de imágenes de perfil.*
*   **Generación de Documentos:** `python-docx` - *Exportación automática a plantillas oficiales estructuradas listas para imprimir.*

## Arquitectura de Agentes de Inteligencia Artificial

Kubi AI basa su "cerebro" en un sistema Multi-Agente especializado. Ambos agentes utilizan la API de **Google GenAI** ejecutando el modelo **Gemini 2.5 Flash**, lo que garantiza una extracción multimodal (visión computacional + comprensión de lenguaje) ultra rápida.

### 1. AgentGemini (Agente Extractor y Analista)
*   **Función:** Procesamiento Multimodal y OCR Semántico.
*   **Proceso:** Recibe la fotografía del Cuaderno de Campo físico escrito a mano de forma rápida por la profesora durante la clase.
*   **Salida:** Mediante un *system prompt* estricto, lee la letra manuscrita, entiende el contexto de la anécdota, deduce a qué área curricular pertenece la actividad (ej. Personal Social, Psicomotriz, Comunicación), y devuelve un objeto JSON estructurado listo para inyectarse en la base de datos y en la plantilla final de Word.
    
### 2. AgentAdvisor (Agente Pedagogo Clínico)
*   **Función:** Análisis de Evolución y Generación de Estrategias.
*   **Proceso:** Analiza el historial consolidado de registros acumulados, el comportamiento y las faltas de un alumno específico.
*   **Salida:** Emite una asesoría pedagógica clínica y concisa estructurada en 3 pasos: *Diagnóstico Breve, Dinámica Sugerida, y Qué Observar*. El docente retroalimenta a este agente indicando si la asesoría "Fue útil (mejoró)" o "No tuvo efecto", lo que alimenta el Dashboard gerencial para medir la verdadera "Respuesta al Aprendizaje" del alumno a lo largo del tiempo.

---

## Configuración y Despliegue Local

### 1. Requisitos Previos
Asegúrate de tener Python 3.10+ instalado en tu sistema.

### 2. Entorno Virtual
Para activarlo e instalar las dependencias, sigue estos pasos:

**En PowerShell (Windows):**
```powershell
.\edutech\Scripts\Activate.ps1
```

**Instalar dependencias:**
```bash
pip install -r requirements.txt
```

### 3. Variables de Entorno y Secretos
Las credenciales de las APIs no deben subirse a ningún repositorio. 
1. Abre el archivo `.streamlit/secrets.toml`.
2. Reemplaza los valores con tus llaves reales de **Supabase** y tu **GEMINI_API_KEY**.

### 4. Ejecutar la Aplicación
Para levantar el servidor local y ver la interfaz:
```bash
streamlit run app.py
```
