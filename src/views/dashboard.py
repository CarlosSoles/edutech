import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components
from src.database.supabase_client import supabase
import src.utils.cache as db_cache

def dashboard_page():
    # Inyección de CSS global basada en el rediseño
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
            --radius: 14px;
            --shadow: 0 1px 2px rgba(30,42,40,0.04), 0 4px 16px rgba(30,42,40,0.04);
        }
        
        .stMarkdown, .stText, p, span, div {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Fraunces', serif !important;
        }
        
        /* Topbar */
        .topbar {
            display:flex; justify-content:space-between; align-items:flex-start;
            margin-bottom:26px;
        }
        @media (max-width: 600px) {
            .topbar { flex-direction: column; gap: 10px; }
        }
        .page-title {
            font-family:'Fraunces',serif; font-weight:600; font-size:26px; margin:0 0 4px;
            display:flex; align-items:center; gap:10px; color: var(--ink);
        }
        .page-sub {color:var(--ink-soft); font-size:13.5px; margin:0;}
        .date-chip {
            font-size:12.5px; color:var(--ink-soft); background:var(--card);
            border:1px solid var(--line); padding:7px 13px; border-radius:20px;
        }
        
        /* KPI ROW */
        .kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:28px;}
        @media (max-width: 768px) {
            .kpi-row { grid-template-columns: 1fr; }
        }
        .kpi-card{
            background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
            padding:18px 20px;box-shadow:var(--shadow);
            display:flex;flex-direction:column;gap:10px;
        }
        .kpi-top{display:flex;justify-content:space-between;align-items:center;}
        .kpi-label{font-size:12.5px;color:var(--ink-soft);font-weight:500;}
        .kpi-icon{width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center;}
        .kpi-icon svg{width:15px;height:15px;}
        .kpi-value{font-family:'Fraunces',serif;font-size:32px;font-weight:600;line-height:1;color:var(--ink);}
        .kpi-note{font-size:12px;color:var(--ink-soft);}
        .kpi-note.good{color:var(--teal);}
        .kpi-note.warn{color:var(--red);}
        .bar-mini{height:5px;border-radius:3px;background:#EEF1EE;overflow:hidden;}
        .bar-mini > div{height:100%;border-radius:3px;}
        
        /* Modificar el estilo de las pestañas o headers nativos */
        h2 { color: var(--ink); font-size: 18px !important; margin-bottom: 5px !important;}
        .stSelectbox label { font-family: 'Inter', sans-serif !important; font-weight: 500 !important; }
        </style>
    """, unsafe_allow_html=True)
    
    import datetime
    hoy_str = datetime.datetime.now().strftime('%d %b %Y')
    
    st.markdown(f"""
    <div class="topbar">
        <div>
        <h1 class="page-title">🏠 Inicio</h1>
        <p class="page-sub">Resumen del aula</p>
        </div>
        <div class="date-chip">Hoy: {hoy_str}</div>
    </div>
    """, unsafe_allow_html=True)
    
    docente_id = st.session_state.user_info['id']
    id_aula = st.session_state.user_info.get('id_aula')

    if not id_aula:
        st.warning("No tienes un aula asignada.")
        st.stop()
        
    alumnos = db_cache.get_alumnos_by_aula(id_aula)
    if not alumnos:
        st.info("No hay alumnos matriculados en esta aula.")
        st.stop()
        
    alumnos_dict = {a['id']: f"{a['nombre']} {a['apellido']}" for a in alumnos}
    
    # 1. TOP METRICS
    total_alumnos = len(alumnos)
    
    # Asistencia
    sesiones = db_cache.get_sesiones_by_aula(id_aula)
    asistencias_hoy = 0
    fecha_asistencia = "Ninguna"
    if sesiones:
        ultima_sesion = sesiones[0]
        fecha_asistencia = ultima_sesion['fecha']
        asis_data = db_cache.get_asistencias_by_sesion(ultima_sesion['id'])
        asistencias_hoy = sum(1 for a in asis_data if a['asistio'])
        
    # Faltantes
    cuadernos = db_cache.get_cuadernos_by_aula(id_aula)
    pares_cuadernos = {(c['fecha'], c['id_area']) for c in cuadernos}
    sesiones_faltantes = []
    for s in sesiones:
        if (s['fecha'], s['id_area']) not in pares_cuadernos:
            sesiones_faltantes.append(s)
            
    pct_asistencia = 100 if total_alumnos == 0 else int((asistencias_hoy / total_alumnos) * 100)
    faltantes_count = len(sesiones_faltantes)
    
    html_kpis = f"""
    <div class="kpi-row">
        <div class="kpi-card">
        <div class="kpi-top">
            <span class="kpi-label">Total de Alumnos</span>
            <div class="kpi-icon" style="background:var(--teal-soft);color:var(--teal);">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.3 3-6 6.5-6s6.5 2.7 6.5 6M17 8.5a3 3 0 1 0 0-6M21.5 20c0-2.7-2-5-4.7-5.7"/></svg>
            </div>
        </div>
        <div class="kpi-value">{total_alumnos}</div>
        <span class="kpi-note">Matriculados este periodo</span>
        </div>
        <div class="kpi-card">
        <div class="kpi-top">
            <span class="kpi-label">Asistencia ({fecha_asistencia[-5:] if fecha_asistencia != 'Ninguna' else 'N/A'})</span>
            <div class="kpi-icon" style="background:var(--teal-soft);color:var(--teal);">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/></svg>
            </div>
        </div>
        <div class="kpi-value">{asistencias_hoy} / {total_alumnos}</div>
        <div class="bar-mini"><div style="width:{pct_asistencia}%;background:var(--teal);"></div></div>
        <span class="kpi-note {'good' if pct_asistencia == 100 else ''}">{pct_asistencia}% de asistencia</span>
        </div>
        <div class="kpi-card">
        <div class="kpi-top">
            <span class="kpi-label">Registros Faltantes</span>
            <div class="kpi-icon" style="background:var({'--red-soft' if faltantes_count > 0 else '--teal-soft'});color:var({'--red' if faltantes_count > 0 else '--teal'});">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 9v4M12 17h.01M10.3 3.9 2.6 18a2 2 0 0 0 1.8 3h15.2a2 2 0 0 0 1.8-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>
            </div>
        </div>
        <div class="kpi-value">{faltantes_count}</div>
        <span class="kpi-note {'warn' if faltantes_count > 0 else 'good'}">{'¡Sube tus cuadernos!' if faltantes_count > 0 else 'Todos los registros al día'}</span>
        </div>
    </div>
    """
    st.markdown(html_kpis, unsafe_allow_html=True)
        
    if sesiones_faltantes:
        areas = db_cache.get_areas()
        areas_dict = {a['id']: a['nombre'] for a in areas}
        st.warning(f"⚠️ Te falta subir la foto del cuaderno de campo de {len(sesiones_faltantes)} sesiones donde tomaste asistencia.")
        with st.expander("Ver sesiones faltantes"):
            for s in sesiones_faltantes:
                st.write(f"- 📅 {s['fecha']} - Área: **{areas_dict.get(s['id_area'], 'Desconocida')}**")

    # DOS COLUMNAS PARA MAPA Y PROGRESO
    col1, col2 = st.columns([1.05, 1], gap="large")
    
    with col1:
        asesorias_global = db_cache.get_asesorias_global()
        evidencias_global = db_cache.get_evidencias_global()
        
        ev_area_map = {e['id']: e.get('cuadernos_campo', {}).get('id_area') for e in evidencias_global if e.get('cuadernos_campo')}
        
        areas = db_cache.get_areas()
        areas_dict = {a['id']: a['nombre'] for a in areas}
        
        conteo_asesorias_area = {name: 0 for name in areas_dict.values()}
        for a in asesorias_global:
            id_ev = a.get('id_evidencia')
            if id_ev and id_ev in ev_area_map:
                area_id = ev_area_map[id_ev]
                area_name = areas_dict.get(area_id, "Desconocido")
                if area_name in conteo_asesorias_area:
                    conteo_asesorias_area[area_name] += 1
                    
        # Preparar datos para Chart.js
        labels = list(conteo_asesorias_area.keys())
        data = list(conteo_asesorias_area.values())
        total_asesorias = sum(data)
        
        # Paleta de colores basada en el diseño
        colors = []
        for area in labels:
            if area == "Comunicación":
                colors.append('#2D6A66')
            elif area == "Personal Social":
                colors.append('#D98E3D')
            elif area.lower().startswith("ciencia"):
                colors.append('#3066BE')
            elif area == "Matemática":
                colors.append('#808080')
            else:
                colors.append('#C24C3F')
                
        chart_data = data if total_asesorias > 0 else [1]
        chart_colors = colors if total_asesorias > 0 else ['#E4E7E1']
        chart_labels = labels if total_asesorias > 0 else ["Sin datos"]
        
        # Generar lista de leyendas en HTML
        leyendas_html = ""
        for i, (area, valor) in enumerate(conteo_asesorias_area.items()):
            pct = int((valor / total_asesorias) * 100) if total_asesorias > 0 else 0
            c = colors[i]
            leyendas_html += f'''
            <div class="legend-row">
                <span class="legend-dot" style="background:{c};"></span>
                <div class="legend-text">
                    <div class="legend-name">{area}</div>
                    <div class="legend-hint">{valor} intervenciones registradas</div>
                </div>
                <span class="legend-pct">{pct}%</span>
            </div>
            '''
                
        html_donut = f"""
        <!DOCTYPE html>
        <html><head>
        <link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
        <style>
          :root{{
            --ink: #1E2A28; --ink-soft: #5B6B68; --bg: #F7F8F5; --card: #FFFFFF; --line: #E4E7E1;
            --teal: #2D6A66; --teal-soft: #E4F0EE; --amber: #D98E3D; --amber-soft: #FBEEDF;
            --radius: 14px; --shadow: 0 1px 2px rgba(30,42,40,0.04), 0 4px 16px rgba(30,42,40,0.04);
          }}
          body{{ margin:0; font-family:'Inter', sans-serif; color:var(--ink); background:transparent; }}
          .section-card{{ background:var(--card); border:1px solid var(--line); border-radius:var(--radius); padding:18px 20px; box-shadow:var(--shadow); }}
          .section-head{{ margin-bottom:12px; }}
          .section-title{{ font-family:'Fraunces',serif; font-weight:600; font-size:16.5px; margin:0 0 4px; display:flex; align-items:center; gap:8px; }}
          .section-desc{{ font-size:12.8px; color:var(--ink-soft); margin:0; line-height:1.5; }}
          .donut-wrap{{ display:flex; align-items:flex-start; gap:20px; }}
          @media (max-width: 600px) {{
            .donut-wrap {{ flex-direction: column; align-items: center; }}
            .legend-list {{ width: 100%; }}
          }}
          .donut-canvas-box{{ width:130px; height:130px; position:relative; flex-shrink:0; }}
          .donut-center{{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; pointer-events:none; }}
          .donut-center .n{{ font-family:'Fraunces',serif; font-size:18px; font-weight:600; }}
          .donut-center .l{{ font-size:10px; color:var(--ink-soft); }}
          .legend-list{{ display:flex; flex-direction:column; gap:8px; flex:1; }}
          .legend-row{{ display:flex; align-items:center; gap:8px; }}
          .legend-dot{{ width:10px; height:10px; border-radius:3px; flex-shrink:0; }}
          .legend-text{{ flex:1; }}
          .legend-name{{ font-size:12.5px; font-weight:600; }}
          .legend-hint{{ font-size:11px; color:var(--ink-soft); }}
          .legend-pct{{ font-family:'Fraunces',serif; font-size:14px; font-weight:600; }}
        </style>
        </head><body>
        <div class="section-card">
          <div class="section-head">
            <h2 class="section-title">📘 Mapa de Atención por Áreas</h2>
            <p class="section-desc">Muestra en qué áreas el Asesor Pedagógico ha intervenido más — es decir, dónde los niños presentan más obstáculos.</p>
          </div>
          <div class="donut-wrap">
            <div class="donut-canvas-box">
              <canvas id="donutChart"></canvas>
              <div class="donut-center">
                <div class="n">{total_asesorias}</div>
                <div class="l">evaluaciones</div>
              </div>
            </div>
            <div class="legend-list">
              {leyendas_html}
            </div>
          </div>
        </div>
        <script>
          Chart.defaults.font.family = "Inter, sans-serif";
          new Chart(document.getElementById('donutChart'), {{
            type: 'doughnut',
            data: {{
              labels: {json.dumps(chart_labels)},
              datasets: [{{
                data: {json.dumps(chart_data)},
                backgroundColor: {json.dumps(chart_colors)},
                borderWidth: 0,
                cutout: '72%'
              }}]
            }},
            options: {{ plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}, responsive: true, maintainAspectRatio: false }}
          }});
        </script>
        </body></html>
        """
        components.html(html_donut, height=450)
    
    alumno_seleccionado_str = None
    with col2:
        st.markdown("""
        <div>
            <h2 class="section-title">✏️ Progreso Individual y Enfoque por Área</h2>
            <p class="section-desc" style="margin-bottom: 12px;">Selecciona un alumno para analizar su distribución de evaluaciones.</p>
        </div>
        """, unsafe_allow_html=True)
        alumno_seleccionado_str = st.selectbox("Seleccionar Alumno", list(alumnos_dict.values()), label_visibility="collapsed")
        
        if alumno_seleccionado_str:
            alumno_id_sel = next(k for k, v in alumnos_dict.items() if v == alumno_seleccionado_str)
            
            # Breakdown por área
            evidencias_alumno = db_cache.get_evidencias_by_alumno(alumno_id_sel)
            
            if evidencias_alumno:
                conteo_areas = {name: 0 for name in areas_dict.values()}
                for ev in evidencias_alumno:
                    c = ev.get('cuadernos_campo')
                    if c:
                        area_name = areas_dict.get(c.get('id_area'), 'General')
                        if area_name in conteo_areas:
                            conteo_areas[area_name] += 1
                            
                df_areas = pd.DataFrame(list(conteo_areas.items()), columns=["Área", "Total de Evaluaciones"])
                df_areas = df_areas.sort_values(by="Total de Evaluaciones", ascending=False)
                
                # HTML Table for Progreso Individual
                max_evals = df_areas["Total de Evaluaciones"].max() if not df_areas.empty else 1
                if max_evals == 0: max_evals = 1
                table_rows = ""
                areas_con_cero = []
                
                for _, row in df_areas.iterrows():
                    area = row["Área"]
                    val = row["Total de Evaluaciones"]
                    if val == 0:
                        areas_con_cero.append(area)
                        continue
                        
                    pct = int((val / max_evals) * 100)
                    if area == "Personal Social":
                        color = "#D98E3D"
                    elif area == "Comunicación":
                        color = "#2D6A66"
                    elif area.lower().startswith("ciencia"):
                        color = "#3066BE"
                    elif area == "Matemática":
                        color = "#808080"
                    else:
                        color = "#C24C3F"
                    table_rows += f"<tr><td><span style='display:inline-flex;align-items:center;gap:7px;font-weight:600;font-size:13px;color:var(--ink);'><span style='width:8px;height:8px;border-radius:50%;background:{color};'></span>{area}</span></td><td><div style='display:flex;align-items:center;gap:10px;'><div style='flex:1;height:6px;background:#EEF1EE;border-radius:4px;overflow:hidden;max-width:120px;'><div style='height:100%;border-radius:4px;background:{color};width:{pct}%;'></div></div><span style='font-weight:600;font-family:\"Fraunces\",serif;font-size:14px;width:16px;text-align:right;color:var(--ink);'>{val}</span></div></td></tr>"
                    
                empty_note_html = ""
                if areas_con_cero:
                    nombres = " y ".join(areas_con_cero)
                    empty_note_html = f"<div style='font-size:12.5px;color:var(--ink-soft);font-style:italic;margin-top:16px;'>Sin evaluaciones registradas aún en {nombres}</div>"
                    
                html_table = f"<div class='section-card' style='margin-top: 10px;'><table style='width:100%;border-collapse:collapse;font-size:13px;font-family:\"Inter\", sans-serif;'><thead><tr><th style='text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--ink-soft);font-weight:600;padding:0 0 8px;border-bottom:1px solid var(--line);'>Área</th><th style='text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--ink-soft);font-weight:600;padding:0 0 8px;border-bottom:1px solid var(--line);'>Evaluaciones</th></tr></thead><tbody>{table_rows}</tbody></table>{empty_note_html}</div>"
                st.markdown(html_table, unsafe_allow_html=True)
            else:
                st.info("Este alumno no tiene evaluaciones registradas aún. ¡Tómale foto a su próximo cuaderno de campo!")

    # --- EFECTIVIDAD PEDAGÓGICA ---
    if alumno_seleccionado_str:
        st.markdown("<br>", unsafe_allow_html=True)
        
        asesorias_alumno = db_cache.get_asesorias_by_alumno(alumno_id_sel)
        
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
                pct_exito = round((exitos / total_resueltas) * 100) if total_resueltas > 0 else 0
                
                html_evo = f"""
                <!DOCTYPE html>
                <html><head>
                <link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
                <style>
                  :root{{ --ink: #1E2A28; --ink-soft: #5B6B68; --card: #FFFFFF; --line: #E4E7E1; --teal: #2D6A66; --amber: #D98E3D; --amber-soft: #FBEEDF; --radius: 14px; --shadow: 0 1px 2px rgba(30,42,40,0.04), 0 4px 16px rgba(30,42,40,0.04); }}
                  body{{ margin:0; font-family:'Inter', sans-serif; color:var(--ink); background:transparent; }}
                  .section-card{{ background:var(--card); border:1px solid var(--line); border-radius:var(--radius); padding:22px 24px; box-shadow:var(--shadow); height:100%; }}
                  .section-head{{ margin-bottom:16px; }}
                  .section-title{{ font-family:'Fraunces',serif; font-weight:600; font-size:16.5px; margin:0 0 4px; display:flex; align-items:center; gap:8px; }}
                  .section-desc{{ font-size:12.8px; color:var(--ink-soft); margin:0; line-height:1.5; }}
                  .evo-top{{ display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:6px; }}
                  .evo-metric-label{{ font-size:12.5px; color:var(--ink-soft); margin-bottom:2px; }}
                  .evo-metric-value{{ font-family:'Fraunces',serif; font-size:30px; font-weight:600; color:var(--teal); }}
                  .evo-chart-box{{ height:220px; position:relative; }}
                  .evo-empty-note{{ display:flex; align-items:center; gap:8px; font-size:12px; color:var(--ink-soft); background:var(--amber-soft); border-radius:8px; padding:9px 12px; margin-top:12px; }}
                  .evo-empty-note svg{{ width:14px; height:14px; flex-shrink:0; color:var(--amber); }}
                </style>
                </head><body>
                <div class="section-card">
                  <div class="section-head">
                    <h2 class="section-title">🕓 Evolución del Aprendizaje</h2>
                    <p class="section-desc">Índice de progreso general.</p>
                  </div>
                  <div class="evo-top">
                    <div>
                      <div class="evo-metric-label">Índice de Progreso</div>
                      <div class="evo-metric-value">{pct_exito}%</div>
                    </div>
                  </div>
                  <div class="evo-chart-box">
                    <canvas id="evoChart"></canvas>
                  </div>
                  {"<div class='evo-empty-note'><svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M12 9v4M12 17h.01M10.3 3.9 2.6 18a2 2 0 0 0 1.8 3h15.2a2 2 0 0 0 1.8-3L13.7 3.9a2 2 0 0 0-3.4 0Z'/></svg>Solo hay 1 sesión evaluada.</div>" if len(historial_fechas) == 1 else ""}
                </div>
                <script>
                  Chart.defaults.font.family = "Inter, sans-serif";
                  new Chart(document.getElementById('evoChart'), {{
                    type: 'line',
                    data: {{
                      labels: {json.dumps(historial_fechas)},
                      datasets: [{{
                        data: {json.dumps([100 if e == 'MEJORANDO' else 50 for e in historial_estados])},
                        borderColor: '#2D6A66',
                        backgroundColor: 'rgba(45,106,102,0.08)',
                        pointBackgroundColor: '#2D6A66',
                        pointRadius: 6,
                        fill: true,
                        tension: 0.35,
                        spanGaps: false
                      }}]
                    }},
                    options: {{
                      responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }},
                      scales: {{ y: {{ min: 0, max: 100, grid: {{ color: '#EFF1EE' }}, ticks: {{ callback: v => v + '%' }} }}, x: {{ grid: {{ display: false }} }} }}
                    }}
                  }});
                </script>
                </body></html>
                """
                components.html(html_evo, height=465)
            else:
                st.info("Hay asesorías generadas, pero aún no has calificado si las dinámicas sugeridas fueron útiles o no.")
        else:
            st.info("Este alumno no tiene intervenciones del Asesor Pedagógico aún.")

dashboard_page()
