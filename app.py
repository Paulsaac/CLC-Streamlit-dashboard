import base64
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from data_loader import load_all_data
from pdf_generator import generate_monthly_pdf_report, generate_weekly_pdf_report, generate_annual_pdf_report
from email_service import enviar_reporte_email

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


# ==========================================
# FUNCIONES AUXILIARES DE FORMATEO (ESPAÑOL)
# ==========================================
def fmt_monto(val: float) -> str:
    """Formatea montos en moneda con '.' de miles: $1.250.000"""
    try:
        return f"${float(val):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0"


def fmt_entero(val) -> str:
    """Formatea cantidades enteras con '.' de miles: 1.000"""
    try:
        return f"{int(val):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def fmt_decimal(val: float, dec: int = 2) -> str:
    """Formatea números decimales con ',' decimal y '.' de miles: 1.234,56"""
    try:
        formatted = f"{float(val):,.{dec}f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0,00"


def fmt_roas(val: float) -> str:
    """Formatea multiplicadores ROAS con ',' decimal: 2,15x"""
    try:
        return f"{float(val):.2f}x".replace(".", ",")
    except (ValueError, TypeError):
        return "0,00x"


def fmt_porcentaje(val: float, dec: int = 1) -> str:
    """Formatea porcentajes con ',' decimal: 12,5%"""
    try:
        return f"{float(val):.{dec}f}%".replace(".", ",")
    except (ValueError, TypeError):
        return "0,0%"

# 1. Configuración de la página
icon_path = "icon-white.png" if os.path.exists("icon-white.png") else "🟢"

st.set_page_config(
    page_title="Dashboard CLC - MercadoLibre",
    page_icon=icon_path,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar logo para la visualización web (logo-green.png para el fondo claro)
if os.path.exists("logo-green.png"):
    logo_web_path = "logo-green.png"
elif os.path.exists("logo.png"):
    logo_web_path = "logo.png"
else:
    logo_web_path = "logo-white.png"

logo_b64 = get_image_base64(logo_web_path)

# Inyección de Estilos CSS Corporativos (Sidebar Oscuro Elegante + Contenido Claro CLC)
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
        
        /* Paleta Sidebar Oscuro */
        --fondo-sidebar-dark: #0D1412;
        --fondo-sidebar-input: #172420;
        --borde-sidebar: #223730;
        --texto-sidebar-titulos: #FFFFFF;
        --texto-sidebar-cuerpo: #CFDFDA;
        --texto-sidebar-caption: #8FAEA3;
    }}
    
    /* Fondo General Claro para el contenido principal */
    .stApp {{
        background-color: var(--fondo-blanco) !important;
        color: var(--gris-texto) !important;
    }}

    /* ==========================================
       ESTILOS DEL SIDEBAR (NEGRO / MODO OSCURO CLC)
       ========================================== */
    section[data-testid="stSidebar"] {{
        background-color: var(--fondo-sidebar-dark) !important;
        border-right: 1px solid var(--borde-sidebar) !important;
    }}
    
    /* Encabezados y Títulos en Sidebar */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3, 
    section[data-testid="stSidebar"] .stMarkdown h4 {{
        color: var(--texto-sidebar-titulos) !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px !important;
    }}
    
    /* Textos, Etiquetas y Párrafos en Sidebar */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] label p {{
        color: var(--texto-sidebar-cuerpo) !important;
        font-weight: 500 !important;
    }}
    
    /* Captions y notas en Sidebar */
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] .stCaption {{
        color: var(--texto-sidebar-caption) !important;
    }}
    
    /* Separadores (Divider) en Sidebar */
    section[data-testid="stSidebar"] hr {{
        border-color: var(--borde-sidebar) !important;
        margin-top: 1.2rem !important;
        margin-bottom: 1.2rem !important;
    }}

    /* Campos de Entrada, Selectores y Fechas en Sidebar */
    section[data-testid="stSidebar"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="base-input"],
    div[data-testid="stDateInput"] div[data-baseweb="input"],
    div[data-testid="stDateInput"] div[data-baseweb="base-input"] {{
        background-color: #FFFFFF !important;
        border: 1px solid #C5E1D4 !important;
        border-radius: 6px !important;
        color: #000000 !important;
    }}

    section[data-testid="stSidebar"] input,
    div[data-testid="stDateInput"] input {{
        color: #000000 !important;
        background-color: #FFFFFF !important;
        -webkit-text-fill-color: #000000 !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] div,
    div[data-testid="stDateInput"] span,
    div[data-testid="stDateInput"] div:not([data-testid="stWidgetLabel"]) {{
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }}

    section[data-testid="stSidebar"] input::placeholder,
    div[data-testid="stDateInput"] input::placeholder {{
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
    }}

    /* Opciones desplegables y menús emergentes */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"],
    ul[role="listbox"] {{
        background-color: #FFFFFF !important;
    }}
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] li,
    li[role="option"] {{
        color: #000000 !important;
    }}

    /* Tags / Chips de Selección Múltiple en Sidebar */
    section[data-testid="stSidebar"] div[data-baseweb="tag"] {{
        background-color: var(--verde-principal) !important;
        border: 1px solid var(--verde-medio) !important;
        border-radius: 4px !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="tag"] span {{
        color: #FFFFFF !important;
    }}

    /* Botones dentro del Sidebar con Alto Contraste y Verde CLC */
    section[data-testid="stSidebar"] .stButton > button,
    section[data-testid="stSidebar"] .stDownloadButton > button {{
        background: linear-gradient(135deg, #124E3F 0%, #1E824C 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #25D366 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 9px 18px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4) !important;
    }}
    
    section[data-testid="stSidebar"] .stButton > button:hover,
    section[data-testid="stSidebar"] .stDownloadButton > button:hover {{
        background: linear-gradient(135deg, #1E824C 0%, #25D366 100%) !important;
        color: #0A1410 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(37, 211, 102, 0.4) !important;
        transform: translateY(-1px) !important;
    }}

    /* Alertas en Sidebar */
    section[data-testid="stSidebar"] div[data-testid="stAlert"] {{
        background-color: #122820 !important;
        border: 1px solid #1E824C !important;
        color: #E2F5EE !important;
    }}
    
    /* ==========================================
       ESTILOS DEL CONTENIDO PRINCIPAL (DASHBOARD)
       ========================================== */
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
        border-top: 4px solid var(--verde-principal) !important;
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
    
    /* Cajas Informativas (Alertas en el panel principal) */
    .main div[data-testid="stAlert"] {{
        border-radius: 8px !important;
        border: 1px solid #C5E1D4 !important;
        background-color: var(--verde-fondo-suave) !important;
        color: var(--verde-principal) !important;
    }}
    
    /* Reducir tamaño de fuente en Dataframes (Tablas de Streamlit) */
    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {{
        font-size: 11px !important;
    }}
    div[data-testid="stDataFrame"] * {{
        font-size: 11px !important;
    }}
    
    /* Botones Principales en el panel principal */
    .main .stButton > button, .main .stDownloadButton > button {{
        background-color: var(--verde-principal) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
    }}
    .main .stButton > button:hover, .main .stDownloadButton > button:hover {{
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

# 1. Encabezado: Logo en la esquina superior izquierda + Título
col_logo, col_title = st.columns([1, 5], vertical_alignment="center")
with col_logo:
    if os.path.exists(logo_web_path):
        st.image(logo_web_path, use_container_width=True)
with col_title:
    st.title("Panel de control de Ventas & Performance en Mercado Libre")

# 2. Carga de datos desde data_loader.py
try:
    df_semana, df_catalogo, df_ordenes = load_all_data()
except Exception as e:
    st.sidebar.error(f"Error al conectar con Google Sheets: {e}")
    st.error(f"Ocurrió un error al cargar la información desde Google Sheets: {e}")
    st.stop()

# 3. Filtros en la barra lateral
st.sidebar.header("Filtros de Control")

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

# 4. Módulo de Exportación a PDF en la barra lateral
st.sidebar.divider()
st.sidebar.header("Exportar Reportes en PDF")

tipo_reporte_pdf = st.sidebar.selectbox(
    "Frecuencia del Reporte",
    options=["Reporte Semanal", "Reporte Mensual", "Reporte Anual"],
    index=1
)

try:
    if tipo_reporte_pdf == "Reporte Semanal":
        pdf_bytes = generate_weekly_pdf_report(
            df_semana=df_semana,
            df_ordenes=df_ordenes,
            df_catalogo=df_catalogo
        )
        nombre_archivo = "reporte_semanal_clc.pdf"
        label_btn = "Descargar Reporte Semanal PDF"
    elif tipo_reporte_pdf == "Reporte Anual":
        pdf_bytes = generate_annual_pdf_report(
            df_semana=df_semana,
            df_ordenes=df_ordenes,
            df_catalogo=df_catalogo
        )
        nombre_archivo = "reporte_anual_clc.pdf"
        label_btn = "Descargar Reporte Anual PDF"
    else:  # Reporte Mensual
        pdf_bytes = generate_monthly_pdf_report(
            df_ordenes_filt=df_ordenes_filt,
            df_semana=df_semana,
            df_catalogo=df_catalogo,
            start_date=start_date,
            end_date=end_date,
            report_type="Reporte Mensual Ejecutivo"
        )
        nombre_archivo = "reporte_mensual_clc.pdf"
        label_btn = "Descargar Reporte Mensual PDF"

    st.sidebar.download_button(
        label=label_btn,
        data=pdf_bytes,
        file_name=nombre_archivo,
        mime="application/pdf",
        use_container_width=True
    )
except Exception as pdf_err:
    st.sidebar.error(f"Error generando {tipo_reporte_pdf}: {pdf_err}")

# Módulo de Envío por Correo Electrónico
st.sidebar.divider()
st.sidebar.subheader("Enviar Reporte por Correo")

opcion_correo = st.sidebar.selectbox(
    "Destinatario del Reporte",
    options=["paulsaac@gmail.com", "franco@leveraweb.com", "Otro (escribir manualmente)..."],
    index=0
)

if opcion_correo == "Otro (escribir manualmente)...":
    destinatario_final = st.sidebar.text_input(
        "Ingresa el correo electrónico:",
        placeholder="ejemplo@correo.com"
    ).strip()
else:
    destinatario_final = opcion_correo.strip()

if st.sidebar.button("Generar PDF y Enviar por Correo", use_container_width=True):
    if not destinatario_final:
        st.sidebar.warning("Por favor ingresa o selecciona un correo electrónico válido.")
    elif "@" not in destinatario_final or "." not in destinatario_final:
        st.sidebar.warning("El formato del correo ingresado no es válido.")
    else:
        with st.spinner("Generando reporte y enviando correo..."):
            try:
                ruta_archivo = "reporte_semanal_clc.pdf"
                
                # Generar bytes del PDF semanal si aún no existen
                if 'pdf_weekly_bytes' not in locals() or pdf_weekly_bytes is None:
                    pdf_weekly_bytes = generate_weekly_pdf_report(
                        df_semana=df_semana,
                        df_ordenes=df_ordenes,
                        df_catalogo=df_catalogo
                    )
                    
                # Guardar el PDF en la ruta de archivo local
                with open(ruta_archivo, "wb") as f:
                    f.write(pdf_weekly_bytes)

                # Enviar el correo usando email_service al destinatario elegido
                exito = enviar_reporte_email(ruta_archivo, destinatario_final)

                if exito:
                    st.sidebar.success(f"✅ Reporte enviado exitosamente a: {destinatario_final}")
                else:
                    st.sidebar.error("❌ Error al enviar el correo. Revisa EMAIL_USER/EMAIL_PASSWORD en secrets.toml y la consola.")
            except Exception as e:
                st.sidebar.error(f"❌ Error durante el proceso: {e}")

# 5. Navegación Principal: Reporte Semanal vs. Reporte Histórico Mensual
main_tab_semanal, main_tab_mensual = st.tabs(["📊 Reporte Semanal / Operativo", "🗓️ Reporte Histórico Mensual"])

# ==========================================
# VISTA 1: REPORTE SEMANAL / OPERATIVO (INTACTO)
# ==========================================
with main_tab_semanal:
    # Sub-pestañas del Dashboard Operativo
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
        c1.metric("Ingresos Totales", fmt_monto(tot_ingresos))
        c2.metric("Total Órdenes", fmt_entero(tot_ordenes))
        c3.metric("Unidades Vendidas", fmt_entero(tot_unidades))
        c4.metric("Ticket Promedio", fmt_monto(ticket_prom))
        c5.metric("ROAS Promedio", fmt_roas(roas_prom))

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
                fig_ing.update_layout(
                    separators=",.",
                    yaxis=dict(tickformat="$,.0f", title="Ingresos ($)")
                )
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
                    separators=",.",
                    yaxis=dict(title="Visitas Totales", tickformat=",.0f"),
                    yaxis2=dict(title="Operaciones", overlaying="y", side="right", tickformat=",.0f"),
                    legend=dict(x=0.01, y=0.99)
                )
                st.plotly_chart(fig_vis, use_container_width=True)
            else:
                st.info("No hay datos suficientes para graficar visitas vs. operaciones.")

    # --- TAB 2: ÓRDENES ---
    with tab2:
        st.subheader("Detalle Transaccional de Órdenes")
        
        # Filtro por Estado de la Orden en la pestaña
        df_ordenes_tab = df_ordenes_filt.copy()
        if not df_ordenes_tab.empty and 'Estado' in df_ordenes_tab.columns:
            estados_disponibles = sorted([str(e) for e in df_ordenes_tab['Estado'].dropna().unique().tolist()])
            if estados_disponibles:
                estado_sel = st.multiselect(
                    "Filtrar por Estado de la Orden:",
                    options=estados_disponibles,
                    default=estados_disponibles
                )
                df_ordenes_tab = df_ordenes_tab[df_ordenes_tab['Estado'].isin(estado_sel)]
        
        if not df_ordenes_tab.empty:
            col_o1, col_o2 = st.columns(2)
            
            with col_o1:
                if 'Dia Semana' in df_ordenes_tab.columns and 'Total' in df_ordenes_tab.columns:
                    ventas_dia = df_ordenes_tab.groupby('Dia Semana')['Total'].sum().reset_index()
                    fig_dias = px.bar(
                        ventas_dia,
                        x='Dia Semana',
                        y='Total',
                        title="Ingresos por Día de la Semana",
                        labels={"Total": "Ingresos ($)", "Dia Semana": "Día"},
                        color='Total',
                        color_continuous_scale='Greens'
                    )
                    fig_dias.update_layout(
                        separators=",.",
                        yaxis=dict(tickformat="$,.0f", title="Ingresos ($)")
                    )
                    st.plotly_chart(fig_dias, use_container_width=True)
            
            with col_o2:
                st.markdown("#### Descargar Reporte")
                csv = df_ordenes_tab.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Órdenes en CSV",
                    data=csv,
                    file_name="reporte_ordenes_meli.csv",
                    mime="text/csv"
                )

            cols_ordenes_vista = [c for c in ['Order ID', 'Fecha', 'Producto(s)', 'Total', 'Cantidad Total', 'Estado'] if c in df_ordenes_tab.columns]
            if not cols_ordenes_vista:
                cols_ordenes_vista = list(df_ordenes_tab.columns)

            st.dataframe(
                df_ordenes_tab[cols_ordenes_vista],
                column_config={
                    "Total": st.column_config.NumberColumn("Total ($)", format="$%,.0f"),
                    "Cantidad Total": st.column_config.NumberColumn("Unidades", format="%,.0f"),
                    "Fecha": st.column_config.DatetimeColumn("Fecha", format="DD/MM/YYYY HH:mm"),
                    "Producto(s)": st.column_config.TextColumn("Producto(s)", width="large"),
                    "Order ID": st.column_config.TextColumn("Order ID", width="small"),
                    "Estado": st.column_config.TextColumn("Estado", width="small")
                },
                use_container_width=True,
                hide_index=True
            )
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
                    fig_marca.update_traces(
                        texttemplate="%{label}<br><b>%{value:,.0f}</b> (%{percent:.1%})",
                        textposition="inside",
                        insidetextorientation="horizontal"
                    )
                    fig_marca.update_layout(separators=",.")
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
                    fig_cat.update_layout(
                        separators=",.",
                        xaxis=dict(tickformat=",.0f", title="Visitas Totales"),
                        yaxis_title="Categoría MeLi"
                    )
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
            fig_ads.update_layout(
                separators=",.",
                yaxis=dict(tickformat="$,.0f", title="Monto ($)"),
                xaxis_title="Semana"
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
                fig_roas.update_layout(
                    separators=",.",
                    yaxis=dict(ticksuffix="x", tickformat=",.2f", title="ROAS (Multiplicador)"),
                    xaxis_title="Semana"
                )
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
            
            ads_act = float(last_row.get('Gasto Publicitario', 0.0))
            ads_prev = float(prev_row.get('Gasto Publicitario', 0.0)) if prev_row is not None else 0.0
            delta_ads = f"{((ads_act - ads_prev) / ads_prev * 100):+.0f}% vs. semana anterior" if ads_prev > 0 else None
            
            roas_act = float(last_row.get('ROAS', 0.0))
            roas_prev = float(prev_row.get('ROAS', 0.0)) if prev_row is not None else 0.0
            delta_roas = f"{(roas_act - roas_prev):+.2f}x vs. semana anterior" if roas_prev > 0 else None
            
            k1, k2, k3, k4, k5, k6 = st.columns(6)
            k1.metric("Ingresos de la Semana", fmt_monto(ing_act), delta=delta_ing)
            k2.metric("Operaciones", fmt_entero(ops_act), delta=delta_ops)
            k3.metric("Unidades Vendidas", fmt_entero(uni_act), delta=delta_uni)
            k4.metric("Visitas Totales", fmt_entero(vis_act), delta=delta_vis)
            k5.metric("Inversión en Ads", fmt_monto(ads_act), delta=delta_ads, delta_color="inverse")
            k6.metric("ROAS Semanal", fmt_roas(roas_act), delta=delta_roas)
            
            st.divider()
            
            # Gráficos de apoyo para la última semana
            col_g1, col_g2 = st.columns(2)
            
            # Obtener órdenes específicas de la última semana
            df_ord_last = pd.DataFrame()
            if not df_ordenes.empty and 'Fecha' in df_ordenes.columns and pd.notna(fecha_inicio):
                df_ord_last = df_ordenes[
                    (df_ordenes['Fecha'].dt.date >= fecha_inicio.date()) & 
                    (df_ordenes['Fecha'].dt.date <= fecha_fin.date())
                ]
            
            with col_g1:
                st.markdown("#### Ingresos por Día de la Semana")
                if not df_ord_last.empty and 'Dia Semana' in df_ord_last.columns and 'Total' in df_ord_last.columns:
                    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    dias_map_es = {
                        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                    }
                    
                    ventas_dia_last = df_ord_last.groupby('Dia Semana')['Total'].sum().reset_index()
                    ventas_dia_last['Dia_ES'] = ventas_dia_last['Dia Semana'].map(dias_map_es)
                    
                    df_dias_base = pd.DataFrame({'Dia Semana': dias_orden, 'Order': range(7)})
                    ventas_dia_last = df_dias_base.merge(ventas_dia_last, on='Dia Semana', how='left').fillna({'Total': 0})
                    ventas_dia_last['Dia_ES'] = ventas_dia_last['Dia Semana'].map(dias_map_es)
                    ventas_dia_last = ventas_dia_last.sort_values('Order')
                    
                    fig_dias_last = px.bar(
                        ventas_dia_last,
                        x='Dia_ES',
                        y='Total',
                        labels={'Total': 'Ingresos ($)', 'Dia_ES': 'Día'},
                        color_discrete_sequence=['#124E3F']
                    )
                    fig_dias_last.update_layout(
                        separators=",.",
                        yaxis=dict(tickformat="$,.0f", title="Ingresos ($)"),
                        xaxis_title="Día"
                    )
                    st.plotly_chart(fig_dias_last, use_container_width=True)
                else:
                    st.info("No se encontraron transacciones por día para esta semana.")
                    
            with col_g2:
                st.markdown("#### Mix de Ventas: Ads vs. Orgánico")
                ing_ads_last = float(last_row.get('Ingresos por Ads', 0.0))
                ing_org_last = float(last_row.get('Ingresos Organicos', 0.0))
                
                if (ing_ads_last + ing_org_last) > 0:
                    fig_mix = px.pie(
                        values=[ing_ads_last, ing_org_last],
                        names=['Mercado Ads', 'Orgánico'],
                        color=['Mercado Ads', 'Orgánico'],
                        color_discrete_map={'Mercado Ads': '#1E824C', 'Orgánico': '#124E3F'},
                        hole=0.45
                    )
                    fig_mix.update_traces(
                        textinfo="label+percent",
                        texttemplate="%{label}<br><b>%{percent:.0%}</b>",
                        textposition="inside",
                        insidetextorientation="horizontal",
                        textfont=dict(color="#FFFFFF", size=12, family="Segoe UI, Arial, sans-serif")
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
                            top_prod_last.style.format({'Total': fmt_monto, 'Unidades': fmt_entero}),
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
                                Total=('Total', 'sum') if 'Total' in df_ord_last.columns else ('Order ID', 'count')
                            )
                            .reset_index()
                            .sort_values(by='Total', ascending=False)
                        )
                        st.dataframe(
                            top_marcas_last.style.format({'Total': fmt_monto, 'Unidades': fmt_entero}),
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


# ==========================================
# VISTA 2: REPORTE HISTÓRICO MENSUAL
# ==========================================
with main_tab_mensual:
    col_hm1, col_hm2 = st.columns([3, 1])
    with col_hm1:
        st.subheader("🗓️ Reporte Histórico Mensual Consolidado")
        st.caption("Consolidación y análisis del rendimiento mensual acumulado en el ciclo de 12 meses (Agosto 2025 – Agosto 2026).")
    with col_hm2:
        try:
            pdf_anual_directo = generate_annual_pdf_report(
                df_semana=df_semana,
                df_ordenes=df_ordenes,
                df_catalogo=df_catalogo
            )
            st.download_button(
                label="📥 Exportar Informe PDF (12 Meses)",
                data=pdf_anual_directo,
                file_name="reporte_historico_mensual_clc.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception:
            pass

    # 1. Rango y compilación de 12 meses (Agosto 2025 a Agosto 2026)
    start_12m = pd.Timestamp("2025-08-01")
    end_12m = pd.Timestamp("2026-08-31 23:59:59")

    # Filtrar df_semana para los 12 meses con fallback inteligente
    if not df_semana.empty and "Fecha Inicio Semana" in df_semana.columns:
        df_sem_12m = df_semana[
            (df_semana['Fecha Inicio Semana'] >= start_12m) & 
            (df_semana['Fecha Inicio Semana'] <= end_12m)
        ].copy()
        
        if df_sem_12m.empty:
            max_dt = df_semana['Fecha Inicio Semana'].max()
            if pd.notna(max_dt):
                min_dt = max_dt - pd.DateOffset(months=12)
                df_sem_12m = df_semana[df_semana['Fecha Inicio Semana'] >= min_dt].copy()
            else:
                df_sem_12m = df_semana.copy()
    else:
        df_sem_12m = df_semana.copy()

    # Filtrar df_ordenes para los 12 meses
    if not df_ordenes.empty and "Fecha" in df_ordenes.columns:
        df_ord_12m = df_ordenes[
            (df_ordenes['Fecha'] >= start_12m) & 
            (df_ordenes['Fecha'] <= end_12m)
        ].copy()
        if df_ord_12m.empty:
            max_dt_ord = df_ordenes['Fecha'].max()
            if pd.notna(max_dt_ord):
                min_dt_ord = max_dt_ord - pd.DateOffset(months=12)
                df_ord_12m = df_ordenes[df_ordenes['Fecha'] >= min_dt_ord].copy()
            else:
                df_ord_12m = df_ordenes.copy()
    else:
        df_ord_12m = df_ordenes.copy()

    if not df_sem_12m.empty and "Fecha Inicio Semana" in df_sem_12m.columns:
        # 2. Agrupación mensual con Pandas
        df_sem_12m['Mes_Periodo'] = df_sem_12m['Fecha Inicio Semana'].dt.to_period('M')
        df_sem_12m['Mes_Inicio'] = df_sem_12m['Fecha Inicio Semana'].dt.to_period('M').dt.to_timestamp()

        meses_es = {
            1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
        }
        df_sem_12m['Mes_Label'] = df_sem_12m['Mes_Inicio'].apply(
            lambda d: f"{meses_es.get(d.month, '')} {str(d.year)[2:]}" if pd.notna(d) else ""
        )

        df_mensual = df_sem_12m.groupby(['Mes_Periodo', 'Mes_Inicio', 'Mes_Label']).agg(
            Ingresos=('Ingresos Generados', 'sum'),
            Operaciones=('Cantidad de Operaciones', 'sum'),
            Unidades=('Total de Unidades Vendidas', 'sum'),
            Visitas=('Visitas Totales', 'sum'),
            Gasto_Ads=('Gasto Publicitario', 'sum'),
            Ingresos_Ads=('Ingresos por Ads', 'sum'),
            Ingresos_Org=('Ingresos Organicos', 'sum'),
            Ventas_Ads=('Ventas Ads', 'sum')
        ).reset_index().sort_values(by='Mes_Inicio')

        df_mensual['ROAS'] = np.where(
            df_mensual['Gasto_Ads'] > 0,
            df_mensual['Ingresos_Ads'] / df_mensual['Gasto_Ads'],
            0.0
        )

        # 3. KPIs del Período (12 Meses Acumulados)
        tot_ing_12m = df_mensual['Ingresos'].sum()
        tot_ops_12m = int(df_mensual['Operaciones'].sum())
        tot_uni_12m = int(df_mensual['Unidades'].sum())
        tot_vis_12m = int(df_mensual['Visitas'].sum())
        tot_ads_12m = df_mensual['Gasto_Ads'].sum()
        tot_ads_ing_12m = df_mensual['Ingresos_Ads'].sum()
        roas_avg_12m = (tot_ads_ing_12m / tot_ads_12m) if tot_ads_12m > 0 else 0.0

        st.markdown("#### Indicadores Clave Acumulados (12 Meses)")
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Ingresos Totales", fmt_monto(tot_ing_12m))
        k2.metric("Operaciones", fmt_entero(tot_ops_12m))
        k3.metric("Unidades Vendidas", fmt_entero(tot_uni_12m))
        k4.metric("Visitas Totales", fmt_entero(tot_vis_12m))
        k5.metric("Gasto Publicitario", fmt_monto(tot_ads_12m))
        k6.metric("ROAS Promedio", fmt_roas(roas_avg_12m))

        st.divider()

        # 4. Gráficos de Rendimiento Mensual
        col_gm1, col_gm2 = st.columns([1.6, 1])

        with col_gm1:
            st.markdown("#### Facturación Mensual Consolidada")
            fig_bar_m = px.bar(
                df_mensual,
                x='Mes_Label',
                y='Ingresos',
                title="Evolución Mensual de Ingresos ($)",
                labels={"Ingresos": "Ingresos ($)", "Mes_Label": "Mes"},
                color_discrete_sequence=['#124E3F'],
                text='Ingresos'
            )
            fig_bar_m.update_traces(
                texttemplate='%{text:$,.0f}',
                textposition='outside',
                marker_line_color='#0A2B23',
                marker_line_width=1
            )
            fig_bar_m.update_layout(
                separators=",.",
                yaxis=dict(tickformat="$,.0f", title="Ingresos ($)"),
                xaxis=dict(title="Mes"),
                uniformtext_minsize=7,
                uniformtext_mode='hide'
            )
            st.plotly_chart(fig_bar_m, use_container_width=True)

        with col_gm2:
            st.markdown("#### Tráfico vs. Operaciones Mensuales")
            fig_vis_m = go.Figure()
            fig_vis_m.add_trace(go.Bar(
                x=df_mensual["Mes_Label"],
                y=df_mensual["Visitas"],
                name="Visitas Totales",
                marker_color="#A5D6A7"
            ))
            fig_vis_m.add_trace(go.Scatter(
                x=df_mensual["Mes_Label"],
                y=df_mensual["Operaciones"],
                name="Operaciones",
                yaxis="y2",
                mode="lines+markers",
                line=dict(color="#124E3F", width=3)
            ))
            fig_vis_m.update_layout(
                title="Visitas vs. Operaciones Concretadas",
                separators=",.",
                yaxis=dict(title="Visitas Totales", tickformat=",.0f"),
                yaxis2=dict(title="Operaciones", overlaying="y", side="right", tickformat=",.0f"),
                legend=dict(x=0.01, y=0.99)
            )
            st.plotly_chart(fig_vis_m, use_container_width=True)

        # 5. Tablas Acumuladas (12 Meses)
        st.markdown("#### 🏆 Tablas Acumuladas del Período (12 Meses)")
        col_t1, col_t2 = st.columns(2)

        with col_t1:
            st.markdown("**Top 10 Artículos Más Vendidos (12 Meses)**")
            if not df_ord_12m.empty and "Producto(s)" in df_ord_12m.columns:
                top_art_12m = (
                    df_ord_12m.groupby("Producto(s)")
                    .agg(
                        Unidades=("Cantidad Total", "sum") if "Cantidad Total" in df_ord_12m.columns else ("Order ID", "count"),
                        Total=("Total", "sum") if "Total" in df_ord_12m.columns else ("Order ID", "count")
                    )
                    .reset_index()
                    .sort_values(by="Total", ascending=False)
                    .head(10)
                )
                top_art_12m["% del Total"] = (top_art_12m["Total"] / tot_ing_12m * 100) if tot_ing_12m > 0 else 0.0
                st.dataframe(
                    top_art_12m.style.format({
                        "Total": fmt_monto,
                        "Unidades": fmt_entero,
                        "% del Total": fmt_porcentaje
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No se encontraron registros de productos para el período.")

        with col_t2:
            st.markdown("**Marcas Más Vendidas (12 Meses)**")
            if not df_ord_12m.empty and not df_catalogo.empty and "Item ID" in df_ord_12m.columns and "Marca" in df_catalogo.columns:
                df_ord_marca12 = df_ord_12m.merge(
                    df_catalogo[["Item ID", "Marca"]].drop_duplicates(subset=["Item ID"]),
                    on="Item ID",
                    how="left"
                )
                df_ord_marca12["Marca"] = df_ord_marca12["Marca"].fillna("Sin Marca / Otra")
                top_marcas_12m = (
                    df_ord_marca12.groupby("Marca")
                    .agg(
                        Unidades=("Cantidad Total", "sum") if "Cantidad Total" in df_ord_marca12.columns else ("Order ID", "count"),
                        Total=("Total", "sum") if "Total" in df_ord_marca12.columns else ("Order ID", "count")
                    )
                    .reset_index()
                    .sort_values(by="Total", ascending=False)
                )
                top_marcas_12m["% del Total"] = (top_marcas_12m["Total"] / tot_ing_12m * 100) if tot_ing_12m > 0 else 0.0
                st.dataframe(
                    top_marcas_12m.style.format({
                        "Total": fmt_monto,
                        "Unidades": fmt_entero,
                        "% del Total": fmt_porcentaje
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            elif not df_catalogo.empty and "Categoria MeLi" in df_catalogo.columns:
                cat_summary_12m = (
                    df_catalogo.groupby("Categoria MeLi")
                    .agg(
                        Publicaciones=("Item ID", "count"),
                        Visitas=("Visitas Totales", "sum"),
                    )
                    .reset_index()
                    .sort_values(by="Visitas", ascending=False)
                )
                st.dataframe(cat_summary_12m, use_container_width=True, hide_index=True)
            else:
                st.info("No hay información disponible para la tabla de marcas.")
    else:
        st.info("No se encontraron registros semanales en el período de 12 meses.")