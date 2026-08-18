import base64
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from data_loader import load_all_data
from pdf_generator import generate_monthly_pdf_report, generate_weekly_pdf_report

# Configurar plantilla clara por defecto en todos los gráficos Plotly
pio.templates.default = "plotly_white"

# Función para codificar logo local en Base64
def get_image_base64(image_path: str) -> str:
    """Lee un archivo de imagen local y lo convierte a formato data URI Base64."""
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded_string}"

# 1. Configuración de la página
st.set_page_config(
    page_title="Dashboard de Ventas Mercado Libre - CLC",
    page_icon="🟢",
    layout="wide"
)

# Cargar logo para la visualización web (logo-green.png)
logo_web_path = "logo-green.png" if os.path.exists("logo-green.png") else "logo.png"
logo_b64 = get_image_base64(logo_web_path)

# Inyección de Estilos CSS Corporativos (Tema Claro con Paleta Verde CLC)
st.markdown(f"""
<style>
    /* Variables de Paleta Corporativa CLC */
    :root {{
        --verde-principal: #124E3F;
        --verde-medio: #1E824C;
        --verde-acento: #25D366;
        --verde-fondo-suave: #F0F7F4;
        --gris-texto: #222222;
        --gris-secundario: #555555;
        --gris-borde: #E2E8F0;
        --fondo-blanco: #FFFFFF;
        --fondo-sidebar: #F8FAF9;
    }}
    
    /* Fondo General Claro */
    .stApp {{
        background-color: var(--fondo-blanco) !important;
        color: var(--gris-texto) !important;
    }}

    /* Barra Lateral (Sidebar) con Tono Suave y Borde Definido */
    section[data-testid="stSidebar"] {{
        background-color: var(--fondo-sidebar) !important;
        border-right: 1px solid var(--gris-borde) !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3, 
    section[data-testid="stSidebar"] .stMarkdown h4 {{
        color: var(--verde-principal) !important;
        font-weight: 700 !important;
    }}
    
    /* Encabezados y Títulos */
    h1, h2, h3, h4 {{
        color: var(--verde-principal) !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-weight: 700 !important;
    }}
    
    /* Pestañas de Navegación (Tabs) */
    button[data-baseweb="tab"] {{
        font-weight: 600 !important;
        color: var(--gris-secundario) !important;
        background-color: transparent !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--verde-principal) !important;
        border-bottom-color: var(--verde-principal) !important;
        border-bottom-width: 3px !important;
    }}
    
    /* Tarjetas de Métricas (stMetric) con Alto Contraste */
    div[data-testid="stMetric"] {{
        background-color: var(--fondo-blanco) !important;
        border: 1px solid var(--gris-borde) !important;
        border-top: 4px solid var(--verde-acento) !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        box-shadow: 0 2px 6px rgba(18, 78, 63, 0.05) !important;
    }}
    div[data-testid="stMetricLabel"] p {{
        color: var(--verde-principal) !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.3px !important;
    }}
    div[data-testid="stMetricValue"] div {{
        color: var(--gris-texto) !important;
        font-weight: 700 !important;
    }}
    
    /* Cajas Informativas (Alertas) */
    div[data-testid="stAlert"] {{
        border-radius: 8px !important;
        border: 1px solid #C5E1D4 !important;
        background-color: var(--verde-fondo-suave) !important;
        color: var(--verde-principal) !important;
    }}
    
    /* Botones Principales y de Descarga */
    .stButton > button, .stDownloadButton > button {{
        background-color: var(--verde-principal) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        background-color: var(--verde-medio) !important;
        box-shadow: 0 3px 10px rgba(18, 78, 63, 0.25) !important;
        transform: translateY(-1px);
    }}
    
    /* Dataframes y Tablas en Pantalla */
    div[data-testid="stDataFrame"] {{
        border: 1px solid var(--gris-borde) !important;
        border-radius: 8px !important;
        background-color: var(--fondo-blanco) !important;
    }}

    /* Estilos de Impresión / Conversión a PDF */
    @media print {{
        @page {{
            margin-top: 80px;
            margin-bottom: 30px;
            margin-left: 35pt;
            margin-right: 35pt;
        }}
        body {{
            padding-top: 40px;
            padding-left: 35pt;
            padding-right: 35pt;
            background-color: #FFFFFF !important;
        }}
        .main .block-container {{
            padding-left: 35pt !important;
            padding-right: 35pt !important;
            max-width: 100% !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# 1. Logo Corporativo en la parte superior de la barra lateral
if os.path.exists(logo_web_path):
    st.sidebar.image(logo_web_path, use_container_width=True)
    st.sidebar.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

st.title("🟢 Dashboard de Ventas & Performance - CLC Mercado Libre")
st.caption("Datos consolidados desde Google Sheets (BDD API MELI)")

# 2. Carga de datos desde data_loader.py
try:
    df_semana, df_catalogo, df_ordenes = load_all_data()
    
    if not df_semana.empty or not df_catalogo.empty or not df_ordenes.empty:
        st.sidebar.success("✅ Conexión exitosa con Google Sheets")
    else:
        st.sidebar.warning("⚠️ Conexión establecida, pero no se encontraron registros en las pestañas.")
except Exception as e:
    st.sidebar.error(f"Error al procesar los datos: {e}")
    st.error(f"Ocurrió un error durante la carga de información: {e}")
    st.stop()

# 3. Filtros en la barra lateral
st.sidebar.header("🎯 Filtros de Control")

start_date = None
end_date = None

# Filtro por rango de fechas (basado en la pestaña Órdenes)
if not df_ordenes.empty and 'Fecha' in df_ordenes.columns:
    df_ordenes_valid = df_ordenes.dropna(subset=['Fecha'])
    if not df_ordenes_valid.empty:
        min_date = df_ordenes_valid['Fecha'].min().date()
        max_date = df_ordenes_valid['Fecha'].max().date()
        
        date_range = st.sidebar.date_input(
            "Rango de Fechas (Órdenes)",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Desempaquetar la tupla de fechas de inicio y fin
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date = date_range[0]
            end_date = date_range[1]
            
            df_ordenes_filt = df_ordenes[
                (df_ordenes['Fecha'].dt.date >= start_date) & 
                (df_ordenes['Fecha'].dt.date <= end_date)
            ]
        else:
            df_ordenes_filt = df_ordenes.copy()
    else:
        df_ordenes_filt = df_ordenes.copy()
else:
    df_ordenes_filt = df_ordenes.copy()

# Filtro por Estado de la Orden
if not df_ordenes_filt.empty and 'Estado' in df_ordenes_filt.columns:
    estados_disponibles = df_ordenes_filt['Estado'].dropna().unique().tolist()
    if estados_disponibles:
        estado_sel = st.sidebar.multiselect(
            "Estado de la Orden",
            options=estados_disponibles,
            default=estados_disponibles
        )
        df_ordenes_filt = df_ordenes_filt[df_ordenes_filt['Estado'].isin(estado_sel)]

# 4. Módulo de Exportación a PDF en la barra lateral
st.sidebar.divider()
st.sidebar.header("📄 Exportar Reportes en PDF")
st.sidebar.caption("Descarga informes ejecutivos en PDF de la última semana o del consolidado mensual.")

# Botón Reporte Semanal
try:
    pdf_weekly_bytes = generate_weekly_pdf_report(
        df_semana=df_semana,
        df_ordenes=df_ordenes,
        df_catalogo=df_catalogo
    )
    st.sidebar.download_button(
        label="📥 Descargar Reporte Semanal PDF",
        data=pdf_weekly_bytes,
        file_name="reporte_semanal_clc.pdf",
        mime="application/pdf",
        use_container_width=True
    )
except Exception as pdf_w_err:
    st.sidebar.error(f"Error generando PDF Semanal: {pdf_w_err}")

# Botón Reporte Mensual / Consolidado
try:
    pdf_monthly_bytes = generate_monthly_pdf_report(
        df_ordenes_filt=df_ordenes_filt,
        df_semana=df_semana,
        df_catalogo=df_catalogo,
        start_date=start_date,
        end_date=end_date
    )
    st.sidebar.download_button(
        label="📥 Descargar Reporte Mensual PDF",
        data=pdf_monthly_bytes,
        file_name="reporte_mensual_clc.pdf",
        mime="application/pdf",
        use_container_width=True
    )
except Exception as pdf_m_err:
    st.sidebar.error(f"Error generando PDF Mensual: {pdf_m_err}")

# 5. Pestañas de Navegación del Dashboard
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Resumen Ejecutivo", "🛍️ Órdenes", "📦 Catálogo", "📣 Mercado Ads", "🗓️ Última Semana"])

# --- TAB 1: RESUMEN EJECUTIVO ---
with tab1:
    st.subheader("Indicadores Clave de Rendimiento (KPIs)")
    
    tot_ingresos = df_ordenes_filt['Total'].sum() if not df_ordenes_filt.empty and 'Total' in df_ordenes_filt.columns else 0
    tot_ordenes = len(df_ordenes_filt) if not df_ordenes_filt.empty else 0
    tot_unidades = df_ordenes_filt['Cantidad Total'].sum() if not df_ordenes_filt.empty and 'Cantidad Total' in df_ordenes_filt.columns else 0
    ticket_prom = tot_ingresos / tot_ordenes if tot_ordenes > 0 else 0
    
    roas_prom = 0.0
    if not df_semana.empty and 'ROAS' in df_semana.columns:
        roas_vals = df_semana['ROAS'].replace([np.inf, -np.inf], np.nan).dropna()
        if not roas_vals.empty:
            roas_prom = roas_vals.mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Ingresos Totales", f"${tot_ingresos:,.0f}")
    c2.metric("Total Órdenes", f"{tot_ordenes:,}")
    c3.metric("Unidades Vendidas", f"{tot_unidades:,}")
    c4.metric("Ticket Promedio", f"${ticket_prom:,.0f}")
    c5.metric("ROAS Promedio", f"{roas_prom:.2f}x")

    st.divider()

    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### Evolución Semanal de Ingresos")
        if not df_semana.empty and 'Fecha Inicio Semana' in df_semana.columns and 'Ingresos Generados' in df_semana.columns:
            fig_ing = px.line(
                df_semana,
                x="Fecha Inicio Semana",
                y="Ingresos Generados",
                markers=True,
                title="Ingresos Generados por Semana ($)",
                labels={"Ingresos Generados": "Ingresos ($)", "Fecha Inicio Semana": "Semana"}
            )
            fig_ing.update_traces(line_color="#124E3F", line_width=3)
            st.plotly_chart(fig_ing, use_container_width=True)
        else:
            st.info("No hay información semanal disponible.")

    with col_right:
        st.markdown("#### Relación Visitas vs. Operaciones")
        if not df_semana.empty and 'Visitas Totales' in df_semana.columns and 'Cantidad de Operaciones' in df_semana.columns:
            fig_vis = go.Figure()
            fig_vis.add_trace(go.Bar(
                x=df_semana["Fecha Inicio Semana"],
                y=df_semana["Visitas Totales"],
                name="Visitas Totales",
                marker_color="#A5D6A7"
            ))
            fig_vis.add_trace(go.Scatter(
                x=df_semana["Fecha Inicio Semana"],
                y=df_semana["Cantidad de Operaciones"],
                name="Operaciones",
                yaxis="y2",
                mode="lines+markers",
                line=dict(color="#124E3F", width=3)
            ))
            fig_vis.update_layout(
                title="Visitas vs. Operaciones Concretadas",
                yaxis=dict(title="Visitas Totales"),
                yaxis2=dict(title="Operaciones", overlaying="y", side="right"),
                legend=dict(x=0.01, y=0.99)
            )
            st.plotly_chart(fig_vis, use_container_width=True)
        else:
            st.info("No hay datos suficientes para graficar visitas vs. operaciones.")

# --- TAB 2: ÓRDENES ---
with tab2:
    st.subheader("Detalle Transaccional de Órdenes")
    
    if not df_ordenes_filt.empty:
        col_o1, col_o2 = st.columns(2)
        
        with col_o1:
            if 'Dia Semana' in df_ordenes_filt.columns and 'Total' in df_ordenes_filt.columns:
                ventas_dia = df_ordenes_filt.groupby('Dia Semana')['Total'].sum().reset_index()
                fig_dias = px.bar(
                    ventas_dia,
                    x='Dia Semana',
                    y='Total',
                    title="Ingresos por Día de la Semana",
                    labels={"Total": "Ingresos ($)", "Dia Semana": "Día"},
                    color='Total',
                    color_continuous_scale='Greens'
                )
                st.plotly_chart(fig_dias, use_container_width=True)
        
        with col_o2:
            st.markdown("#### Descargar Reporte")
            csv = df_ordenes_filt.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Órdenes en CSV",
                data=csv,
                file_name="reporte_ordenes_meli.csv",
                mime="text/csv"
            )

        st.dataframe(df_ordenes_filt, use_container_width=True, hide_index=True)
    else:
        st.info("No se encontraron órdenes para los filtros seleccionados.")

# --- TAB 3: CATÁLOGO ---
with tab3:
    st.subheader("Catálogo de Publicaciones y Productos")
    if not df_catalogo.empty:
        col_cat1, col_cat2 = st.columns(2)
        
        if 'Marca' in df_catalogo.columns and 'Visitas Totales' in df_catalogo.columns:
            with col_cat1:
                visitas_marca = df_catalogo.groupby('Marca')['Visitas Totales'].sum().reset_index()
                fig_marca = px.pie(
                    visitas_marca,
                    names='Marca',
                    values='Visitas Totales',
                    title="Distribución de Visitas por Marca"
                )
                st.plotly_chart(fig_marca, use_container_width=True)

        if 'Categoria MeLi' in df_catalogo.columns and 'Visitas Totales' in df_catalogo.columns:
            with col_cat2:
                visitas_cat = df_catalogo.groupby('Categoria MeLi')['Visitas Totales'].sum().reset_index()
                fig_cat = px.bar(
                    visitas_cat,
                    x='Visitas Totales',
                    y='Categoria MeLi',
                    orientation='h',
                    title="Visitas por Categoria MeLi"
                )
                fig_cat.update_traces(marker_color="#124E3F")
                st.plotly_chart(fig_cat, use_container_width=True)

        st.dataframe(df_catalogo, use_container_width=True, hide_index=True)
    else:
        st.info("No hay información disponible sobre el catálogo.")

# --- TAB 4: MERCADO ADS ---
with tab4:
    st.subheader("Rendimiento de Inversión en Mercado Ads")
    if not df_semana.empty and 'Gasto Publicitario' in df_semana.columns and 'Ingresos por Ads' in df_semana.columns:
        fig_ads = px.bar(
            df_semana,
            x="Fecha Inicio Semana",
            y=["Gasto Publicitario", "Ingresos por Ads"],
            barmode="group",
            title="Gasto Publicitario vs. Ingresos Generados por Ads ($)",
            labels={"value": "Monto ($)", "variable": "Concepto", "Fecha Inicio Semana": "Semana"},
            color_discrete_map={"Gasto Publicitario": "#A5D6A7", "Ingresos por Ads": "#124E3F"}
        )
        st.plotly_chart(fig_ads, use_container_width=True)
        
        if 'ROAS' in df_semana.columns:
            fig_roas = px.line(
                df_semana,
                x="Fecha Inicio Semana",
                y="ROAS",
                markers=True,
                title="Evolución del ROAS Semanal (Retorno sobre Inversión)",
                labels={"ROAS": "ROAS (Multiplicador)", "Fecha Inicio Semana": "Semana"}
            )
            fig_roas.update_traces(line_color="#25D366", line_width=3)
            st.plotly_chart(fig_roas, use_container_width=True)
    else:
        st.info("No hay datos disponibles sobre la pauta publicitaria.")

# --- TAB 5: ÚLTIMA SEMANA ---
with tab5:
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.subheader("🗓️ Desglose & Diagnóstico de la Última Semana")
    with col_t2:
        try:
            st.download_button(
                label="📥 Exportar Semana en PDF",
                data=pdf_weekly_bytes,
                file_name="reporte_semanal_clc.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception:
            pass
    
    if not df_semana.empty:
        # Extraer datos de la última semana y semana previa
        df_sem_sorted = df_semana.sort_values(by='Fecha Inicio Semana') if 'Fecha Inicio Semana' in df_semana.columns else df_semana
        last_row = df_sem_sorted.iloc[-1]
        prev_row = df_sem_sorted.iloc[-2] if len(df_sem_sorted) > 1 else None
        
        periodo_actual = last_row.get('Periodo', 'N/A')
        fecha_inicio = last_row.get('Fecha Inicio Semana')
        fecha_str = ""
        if pd.notna(fecha_inicio):
            fecha_fin = fecha_inicio + pd.Timedelta(days=6)
            fecha_str = f"Del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
            
        st.info(f"📌 **Período Analizado:** {periodo_actual} {('— ' + fecha_str) if fecha_str else ''}")
        
        # Métricas principales con Delta vs. Semana Anterior (español)
        ing_act = float(last_row.get('Ingresos Generados', 0.0))
        ing_prev = float(prev_row.get('Ingresos Generados', 0.0)) if prev_row is not None else 0.0
        delta_ing = f"{((ing_act - ing_prev) / ing_prev * 100):+.0f}% vs. semana anterior" if ing_prev > 0 else None
        
        ops_act = int(last_row.get('Cantidad de Operaciones', 0))
        ops_prev = int(prev_row.get('Cantidad de Operaciones', 0)) if prev_row is not None else 0
        delta_ops = f"{((ops_act - ops_prev) / ops_prev * 100):+.0f}% vs. semana anterior" if ops_prev > 0 else None
        
        uni_act = int(last_row.get('Total de Unidades Vendidas', 0))
        uni_prev = int(prev_row.get('Total de Unidades Vendidas', 0)) if prev_row is not None else 0
        delta_uni = f"{((uni_act - uni_prev) / uni_prev * 100):+.0f}% vs. semana anterior" if uni_prev > 0 else None
        
        vis_act = int(last_row.get('Visitas Totales', 0))
        vis_prev = int(prev_row.get('Visitas Totales', 0)) if prev_row is not None else 0
        delta_vis = f"{((vis_act - vis_prev) / vis_prev * 100):+.0f}% vs. semana anterior" if vis_prev > 0 else None
        
        roas_act = float(last_row.get('ROAS', 0.0))
        roas_prev = float(prev_row.get('ROAS', 0.0)) if prev_row is not None else 0.0
        delta_roas = f"{(roas_act - roas_prev):+.2f}x vs. semana anterior" if prev_row is not None else None
        
        gasto_act = float(last_row.get('Gasto Publicitario', 0.0))
        gasto_prev = float(prev_row.get('Gasto Publicitario', 0.0)) if prev_row is not None else 0.0
        delta_gasto = f"{((gasto_act - gasto_prev) / gasto_prev * 100):+.0f}% vs. semana anterior" if gasto_prev > 0 else None

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Ingresos Totales", f"${ing_act:,.0f}", delta=delta_ing)
        k2.metric("Operaciones", f"{ops_act:,}", delta=delta_ops)
        k3.metric("Unidades Vendidas", f"{uni_act:,}", delta=delta_uni)
        k4.metric("Visitas Totales", f"{vis_act:,}", delta=delta_vis)
        k5.metric("ROAS Ads", f"{roas_act:.2f}x", delta=delta_roas)
        k6.metric("Gasto Ads", f"${gasto_act:,.0f}", delta=delta_gasto, delta_color="inverse")
        
        st.divider()
        
        # Gráficos de desglose de la última semana
        col_g1, col_g2 = st.columns(2)
        
        # Filtrar órdenes de la última semana
        df_ord_last = pd.DataFrame()
        if not df_ordenes.empty and 'Fecha' in df_ordenes.columns and pd.notna(fecha_inicio):
            fecha_fin_dt = fecha_inicio + pd.Timedelta(days=6)
            df_ord_last = df_ordenes[
                (df_ordenes['Fecha'].dt.date >= fecha_inicio.date()) & 
                (df_ordenes['Fecha'].dt.date <= fecha_fin_dt.date())
            ]
        
        with col_g1:
            st.markdown("#### 📅 Evolución Diaria de Ventas")
            dias_orden = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            dias_map_es = {
                "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
                "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
            }
            df_base_dias = pd.DataFrame({
                "Dia Semana": dias_orden,
                "Dia_ES": [dias_map_es[d] for d in dias_orden],
                "Total": 0.0,
                "Sort_Order": range(7)
            })
            if not df_ord_last.empty and 'Dia Semana' in df_ord_last.columns and 'Total' in df_ord_last.columns:
                ventas_dia_last = df_ord_last.groupby('Dia Semana')['Total'].sum().reset_index()
                merged_dias = df_base_dias.merge(ventas_dia_last, on="Dia Semana", how="left", suffixes=("_base", ""))
                merged_dias["Total"] = merged_dias["Total"].fillna(0.0)
                ventas_dia_last = merged_dias.sort_values(by='Sort_Order')
            else:
                ventas_dia_last = df_base_dias
            
            fig_dia_last = px.bar(
                ventas_dia_last,
                x='Dia_ES',
                y='Total',
                title=f"Ingresos por Día de la Semana ({periodo_actual})",
                labels={'Total': 'Ingresos ($)', 'Dia_ES': 'Día'},
                color_discrete_sequence=['#124E3F']
            )
            fig_dia_last.update_layout(xaxis_title="Día de la Semana", yaxis_title="Ingresos ($)")
            st.plotly_chart(fig_dia_last, use_container_width=True)
                
        with col_g2:
            st.markdown("#### ⚖️ Mix de Ingresos: Mercado Ads vs. Orgánico")
            ing_ads = float(last_row.get('Ingresos por Ads', 0.0))
            ing_org = float(last_row.get('Ingresos Organicos', max(0.0, ing_act - ing_ads)))
            
            if ing_ads > 0 or ing_org > 0:
                mix_df = pd.DataFrame({
                    "Canal": ["Mercado Ads", "Ventas Orgánicas"],
                    "Monto": [ing_ads, ing_org]
                })
                fig_mix = px.pie(
                    mix_df,
                    names="Canal",
                    values="Monto",
                    title=f"Distribución de Ingresos ({periodo_actual})",
                    hole=0.38,
                    color="Canal",
                    color_discrete_map={"Mercado Ads": "#1E824C", "Ventas Orgánicas": "#124E3F"}
                )
                fig_mix.update_traces(
                    texttemplate="%{label}<br>%{percent:.0%}",
                    textposition="inside",
                    textfont=dict(color="#FFFFFF", size=13, family="Segoe UI, Arial, sans-serif")
                )
                st.plotly_chart(fig_mix, use_container_width=True)
            else:
                st.info("No hay datos de distribución de pauta para esta semana.")
                
        # Top Productos, Marcas y Detalle de Órdenes de la Semana
        st.markdown("#### 🛍️ Artículos & Marcas Más Vendidas de la Semana")
        if not df_ord_last.empty:
            col_prod, col_marca = st.columns(2)
            
            with col_prod:
                st.markdown("**Top 10 Artículos Más Vendidos**")
                if 'Producto(s)' in df_ord_last.columns:
                    top_prod_last = (
                        df_ord_last.groupby('Producto(s)')
                        .agg(
                            Unidades=('Cantidad Total', 'sum') if 'Cantidad Total' in df_ord_last.columns else ('Order ID', 'count'),
                            Total=('Total', 'sum') if 'Total' in df_ord_last.columns else ('Order ID', 'count')
                        )
                        .reset_index()
                        .sort_values(by='Total', ascending=False)
                        .head(10)
                    )
                    st.dataframe(
                        top_prod_last.style.format({'Total': '${:,.0f}', 'Unidades': '{:,.0f}'}),
                        use_container_width=True,
                        hide_index=True
                    )
            
            with col_marca:
                st.markdown("**Top Marcas Más Vendidas**")
                if not df_catalogo.empty and 'Item ID' in df_ord_last.columns and 'Marca' in df_catalogo.columns:
                    df_ord_m = df_ord_last.merge(df_catalogo[['Item ID', 'Marca']].drop_duplicates(subset=['Item ID']), on='Item ID', how='left')
                    df_ord_m['Marca'] = df_ord_m['Marca'].fillna('Sin Marca / Otra')
                    top_marcas_last = (
                        df_ord_m.groupby('Marca')
                        .agg(
                            Unidades=('Cantidad Total', 'sum') if 'Cantidad Total' in df_ord_m.columns else ('Order ID', 'count'),
                            Total=('Total', 'sum') if 'Total' in df_ord_m.columns else ('Order ID', 'count')
                        )
                        .reset_index()
                        .sort_values(by='Total', ascending=False)
                    )
                    st.dataframe(
                        top_marcas_last.style.format({'Total': '${:,.0f}', 'Unidades': '{:,.0f}'}),
                        use_container_width=True,
                        hide_index=True
                    )

            st.markdown("#### 📋 Listado de Órdenes del Período")
            cols_mostrar = [c for c in ['Order ID', 'Fecha', 'Comprador', 'Producto(s)', 'Total', 'Cantidad Total', 'Estado'] if c in df_ord_last.columns]
            st.dataframe(df_ord_last[cols_mostrar], use_container_width=True, hide_index=True)
        else:
            st.info("No se encontraron transacciones registradas en la pestaña de órdenes para la última semana.")
    else:
        st.info("No hay información semanal disponible.")