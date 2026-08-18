import toml
import gspread
from google.oauth2.service_account import Credentials

print("--- INICIO DE DIAGNÓSTICO ---")

# 1. Verificar lectura de secretos
try:
    with open(".streamlit/secrets.toml", "r", encoding="utf-8") as f:
        secrets = toml.load(f)
    creds_dict = secrets["connections"]["gsheets"]
    print("✅ Paso 1: Archivo .streamlit/secrets.toml leído correctamente.")
    print(f"   - Email registrado: {creds_dict.get('client_email')}")
    print(f"   - Project ID: {creds_dict.get('project_id')}")
except Exception as e:
    print(f"❌ Paso 1 Falló: Error al leer secrets.toml -> {e}")
    exit()

# 2. Verificar Autenticación con Google Cloud
try:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(credentials)
    print("✅ Paso 2: Autenticación exitosa con la API de Google.")
except Exception as e:
    print(f"❌ Paso 2 Falló: Error de autenticación de credenciales -> {e}")
    exit()

# 3. Intentar abrir la Hoja por su ID
SPREADSHEET_ID = "1k9aTmXgJZkinroefA7EEnboXVxMseXVrVfOT79ofFWE"

try:
    sh = gc.open_by_key(SPREADSHEET_ID)
    print(f"✅ Paso 3: Documento [MeLi-CLC BDD-API MELI] abierto correctamente.")
    print(f"   - Título del archivo: '{sh.title}'")
except Exception as e:
    print(f"❌ Paso 3 Falló: No se pudo abrir la hoja con el ID especificado -> {e}")
    exit()

# 4. Listar pestañas reales del documento
try:
    worksheets = sh.worksheets()
    print("✅ Paso 4: Pestañas detectadas en el documento:")
    for ws in worksheets:
        print(f"   - Pestaña: '{ws.title}'")
except Exception as e:
    print(f"❌ Paso 4 Falló: Error al obtener lista de pestañas -> {e}")
    exit()

# 5. Lectura robusta con get_all_values() y Pandas
try:
    import pandas as pd
    ws_first = worksheets[0]
    values = ws_first.get_all_values()
    if values:
        headers = values[0]
        rows = values[1:]
        df = pd.DataFrame(rows, columns=headers)
        print(f"✅ Paso 5: Lectura exitosa de la pestaña '{ws_first.title}' usando get_all_values(). Registros leídos: {len(df)}")
        print("--- DIAGNÓSTICO FINALIZADO CON ÉXITO ---")
except Exception as e:
    print(f"❌ Paso 5 Falló: Error al leer datos de la pestaña '{ws_first.title}' -> {e}")