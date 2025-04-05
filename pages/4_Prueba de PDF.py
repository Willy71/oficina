# 4_Painel_de_controle.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

#===================================================================================================================================================================
# Configuración de página (igual que tu código original)
st.set_page_config(
    page_title="Teste de PDF",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS (copiados de tu código original)
reduce_space = """
<style type="text/css">
div[data-testid="stAppViewBlockContainer"]{
    padding-top:30px;
}
</style>
"""
st.markdown(reduce_space, unsafe_allow_html=True)

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://github.com/Willy71/oficina/blob/main/pictures/wallpaper%20black%20vintage.jpg?raw=true");
background-size: 180%;
background-position: top left;
background-repeat: repeat;
background-attachment: local;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}

[data-testid="stSidebar"] {{
background: rgba(0,0,0,0);
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

#===================================================================================================================================================================
# Conexion via gspread a traves de https://console.cloud.google.com/ y Google sheets

# Scopes necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Ruta al archivo de credenciales
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]

# Clave de la hoja de cálculo (la parte de la URL después de "/d/" y antes de "/edit")
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'  # Reemplaza con la clave de tu documento
SHEET_NAME = 'Hoja 1'  # Nombre de la hoja dentro del documento

# Cargar credenciales y autorizar
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)
credenciales_json = credentials


def autenticar_gspread():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    cliente = gspread.authorize(credentials)
    return cliente

def inicializar_hoja():
    try:
        # Abrir la hoja de cálculo
        spreadsheet = gc.open_by_key(SPREADSHEET_KEY)
        
        # Intentar abrir la hoja específica
        try:
            worksheet = spreadsheet.worksheet(SHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            # Si la hoja no existe, crearla
            worksheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=100, cols=50)
            # Agregar los encabezados de las columnas
            worksheet.append_row(columnas_ordenadas)  # Asegúrate de definir `columnas_ordenadas`
        
        return worksheet
    except Exception as e:
        st.error(f"Erro ao acessar planilha: {str(e)}")
        return None

# Definir las columnas en el orden correcto
# Definir el esquema de columnas en el orden correcto
columnas_ordenadas = ['user_id', 'date_in', 'date_prev', 'date_out', 'carro', 'modelo', 'cor', 'placa', 'km', 'ano', 
                      'estado', 'dono_empresa', 'telefone', 'endereco', 'item_serv_1', 'desc_ser_1', 'valor_serv_1',
                      'item_serv_2', 'desc_ser_2', 'valor_serv_2', 'item_serv_3', 'desc_ser_3', 'valor_serv_3',
                      'item_serv_4', 'desc_ser_4', 'valor_serv_4', 'item_serv_5', 'desc_ser_5', 'valor_serv_5',
                      'item_serv_6', 'desc_ser_6', 'valor_serv_6', 'item_serv_7', 'desc_ser_7', 'valor_serv_7',
                      'item_serv_8', 'desc_ser_8', 'valor_serv_8', 'item_serv_9', 'desc_ser_9', 'valor_serv_9',
                      'item_serv_10', 'desc_ser_10', 'valor_serv_10', 'item_serv_11', 'desc_ser_11', 'valor_serv_11',
                      'item_serv_12', 'desc_ser_12', 'valor_serv_12', 'total_serviço', 'porcentaje_adicional',
                      'quant_peca_1', 'desc_peca_1', 'valor_peca_1', 'sub_tota_peca_1', 'valor_total_peca_1', 
                      'quant_peca_2', 'desc_peca_2', 'valor_peca_2', 'sub_tota_peca_2','valor_total_peca_2',
                      'quant_peca_3', 'desc_peca_3', 'valor_peca_3', 'sub_tota_peca_3', 'valor_total_peca_3',
                      'quant_peca_4', 'desc_peca_4', 'valor_peca_4', 'sub_tota_peca_4', 'valor_total_peca_4',
                      'quant_peca_5', 'desc_peca_5', 'valor_peca_5', 'sub_tota_peca_5', 'valor_total_peca_5',
                      'quant_peca_6', 'desc_peca_6', 'valor_peca_6', 'sub_tota_peca_6', 'valor_total_peca_6',
                      'quant_peca_7', 'desc_peca_7', 'valor_peca_7', 'sub_tota_peca_7', 'valor_total_peca_7',
                      'quant_peca_8', 'desc_peca_8', 'valor_peca_8', 'sub_tota_peca_8', 'valor_total_peca_8',
                      'quant_peca_9', 'desc_peca_9', 'valor_peca_9', 'sub_tota_peca_9', 'valor_total_peca_9',
                      'quant_peca_10', 'desc_peca_10', 'valor_peca_10', 'sub_tota_peca_10', 'valor_total_peca_10',
                      'quant_peca_11', 'desc_peca_11', 'valor_peca_11', 'sub_tota_peca_11', 'valor_total_peca_11',
                      'quant_peca_12', 'desc_peca_12', 'valor_peca_12', 'sub_tota_peca_12', 'valor_total_peca_12',
                      'quant_peca_13', 'desc_peca_13', 'valor_peca_13', 'sub_tota_peca_13', 'valor_total_peca_13',
                      'quant_peca_14', 'desc_peca_14', 'valor_peca_14', 'sub_tota_peca_14', 'valor_total_peca_14',
                      'quant_peca_15', 'desc_peca_15', 'valor_peca_15', 'sub_tota_peca_15', 'valor_total_peca_15',
                      'quant_peca_16', 'desc_peca_16', 'valor_peca_16', 'sub_tota_peca_16', 'valor_total_peca_16',
                      'total_costo_inicial', 'total_costo_final', 'forma_de_pagamento', 'pagamento_parcial', 
                      'valor_pago_parcial', 'data_prox_pag', 'valor_prox_pag', 'pag_total', 'valor_pag_total'
                     ]

# Función para cargar datos desde Google Sheets
def cargar_datos(worksheet):
    try:
        records = worksheet.get_all_records()
        if not records:
            # Si no hay registros, crear un DataFrame vacío con las columnas necesarias
            return pd.DataFrame(columns=columnas_ordenadas)
        else:
            # Convertir los registros a DataFrame
            df = pd.DataFrame(records)
            # Asegurarse de que la columna 'user_id' sea numérica
            df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce').fillna(0).astype(int)
            return df
    except Exception as e:
        st.error(f"Erro ao cargar dados: {str(e)}")
        return pd.DataFrame(columns=columnas_ordenadas)


# Inicializar la hoja de cálculo
worksheet = inicializar_hoja()

# Cargar datos desde Google Sheets
existing_data = cargar_datos(worksheet)


vendor_to_update = st.selectbox("Selecione o ID", options=existing_data["user_id"].tolist())
vendor_data = existing_data[existing_data["user_id"] == vendor_to_update].iloc[0]
