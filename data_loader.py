import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1k9aTmXgJZkinroefA7EEnboXVxMseXVrVfOT79ofFWE"

def clean_currency(val):
    if pd.isna(val) or val == "":
        return 0.0
    val_str = str(val).replace('$', '').replace(',', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def make_unique_columns(columns):
    seen = {}
    unique = []
    for i, col in enumerate(columns):
        col_name = str(col).strip() if str(col).strip() != "" else f"Unnamed_{i}"
        if col_name in seen:
            seen[col_name] += 1
            unique.append(f"{col_name}_{seen[col_name]}")
        else:
            seen[col_name] = 0
            unique.append(col_name)
    return unique

def read_sheet_to_df(sheet):
    values = sheet.get_all_values()
    if not values:
        return pd.DataFrame()
    headers = make_unique_columns(values[0])
    rows = values[1:]
    return pd.DataFrame(rows, columns=headers)

@st.cache_data(ttl=600)
def load_all_data():
    # Leer credenciales desde .streamlit/secrets.toml
    creds_dict = st.secrets["connections"]["gsheets"]
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(credentials)
    
    sh = gc.open_by_key(SPREADSHEET_ID)
    
    # Leer pestañas de Google Sheets
    try:
        df_semana = read_sheet_to_df(sh.worksheet("Semana"))
    except Exception:
        df_semana = pd.DataFrame()

    try:
        df_catalogo = read_sheet_to_df(sh.worksheet("Catálogo"))
    except Exception:
        df_catalogo = pd.DataFrame()

    try:
        df_ordenes = read_sheet_to_df(sh.worksheet("Órdenes"))
    except Exception:
        df_ordenes = pd.DataFrame()

    # Limpieza pestaña Semana
    if not df_semana.empty:
        for col in ['Ingresos Generados', 'Gasto Publicitario', 'Ingresos por Ads', 'Ingresos Organicos']:
            if col in df_semana.columns:
                df_semana[col] = df_semana[col].apply(clean_currency)
        
        for col in ['Cantidad de Operaciones', 'Total de Unidades Vendidas', 'Visitas Totales', 'Ventas Ads']:
            if col in df_semana.columns:
                df_semana[col] = pd.to_numeric(df_semana[col], errors='coerce').fillna(0)
            
        if 'Fecha Inicio Semana' in df_semana.columns:
            df_semana['Fecha Inicio Semana'] = pd.to_datetime(df_semana['Fecha Inicio Semana'], errors='coerce')

        df_semana['ROAS'] = np.where(
            df_semana['Gasto Publicitario'] > 0,
            df_semana['Ingresos por Ads'] / df_semana['Gasto Publicitario'],
            0.0
        )

    # Limpieza pestaña Catálogo
    if not df_catalogo.empty:
        if 'Precio Base' in df_catalogo.columns:
            df_catalogo['Precio Base'] = df_catalogo['Precio Base'].apply(clean_currency)
        if 'Visitas Totales' in df_catalogo.columns:
            df_catalogo['Visitas Totales'] = pd.to_numeric(df_catalogo['Visitas Totales'], errors='coerce').fillna(0)

    # Limpieza pestaña Órdenes
    if not df_ordenes.empty:
        if 'Total' in df_ordenes.columns:
            df_ordenes['Total'] = df_ordenes['Total'].apply(clean_currency)
        if 'Cantidad Total' in df_ordenes.columns:
            df_ordenes['Cantidad Total'] = pd.to_numeric(df_ordenes['Cantidad Total'], errors='coerce').fillna(0)
        if 'Fecha' in df_ordenes.columns:
            df_ordenes['Fecha'] = pd.to_datetime(df_ordenes['Fecha'], errors='coerce')

    return df_semana, df_catalogo, df_ordenes