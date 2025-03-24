import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import re
import gspread
from google.oauth2.service_account import Credentials

# Colocar nome na pagina, icone e ampliar a tela
st.set_page_config(
    page_title="Consultas",
    page_icon=":car",
    layout="wide"
)

# We reduced the empty space at the beginning of the streamlit
reduce_space ="""
            <style type="text/css">
            /* Remueve el espacio en el encabezado por defecto de las apps de Streamlit */
            div[data-testid="stAppViewBlockContainer"]{
                padding-top:30px;
            }
            </style>
            """
# We load reduce_space
st.html(reduce_space)

# ----------------------------------------------------------------------------------------------------------------------------
# Colocar el background y definir los colores del sidebar
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://i.postimg.cc/jdtSsJ9t/jr-korpa-H-BJWTh-ZRok-unsplash.jpg");
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

#=============================================================================================================================
# 2_Consulta_veiculos.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ----------------------------------------------------------------------------------------------------------------------------------
# Configuración de página (igual que en tu código original)
st.set_page_config(
    page_title="Consulta de Vehículos",
    page_icon=":car:",
    layout="wide"
)

reduce_space = """
            <style type="text/css">
            div[data-testid="stAppViewBlockContainer"]{
                padding-top:30px;
            }
            </style>
            """
st.html(reduce_space)

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://i.postimg.cc/jdtSsJ9t/jr-korpa-H-BJWTh-ZRok-unsplash.jpg");
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
# ----------------------------------------------------------------------------------------------------------------------------------

# Título de la página
st.title("Consulta de Vehículos por Patente")

# ----------------------------------------------------------------------------------------------------------------------------------
# Conexión a Google Sheets (usando tu misma configuración)
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

# Usamos la misma hoja de cálculo que en tu código original
SPREADSHEET_KEY = '1ndVk4efZZN74serPvDpN6tcm2NamLqKlcYfz2-y156g'
SHEET_NAME = 'Veiculos'  # Cambia esto al nombre de tu hoja de vehículos

try:
    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
    veiculos_data = pd.DataFrame(worksheet.get_all_records())
except gspread.exceptions.SpreadsheetNotFound:
    st.error("No se encontró la hoja de cálculo. Verifica la clave y los permisos.")
except gspread.exceptions.WorksheetNotFound:
    st.error(f"No se encontró la hoja '{SHEET_NAME}' en el documento.")

# ----------------------------------------------------------------------------------------------------------------------------------
# Función para buscar vehículo por patente
def buscar_por_patente(patente):
    if not veiculos_data.empty:
        # Busca coincidencias exactas (ajusta según tu estructura de datos)
        resultado = veiculos_data[veiculos_data['Patente'].str.upper() == patente.upper()]
        return None if resultado.empty else resultado.iloc[0].to_dict()
    return None

# ----------------------------------------------------------------------------------------------------------------------------------
# Interfaz de usuario
with st.container():
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        patente = st.text_input("Ingrese la patente del vehículo:", "").strip().upper()
    
    with col2:
        st.write("")  # Espaciador
        buscar = st.button("Buscar Vehículo")

if buscar and patente:
    with st.spinner("Buscando vehículo..."):
        vehiculo = buscar_por_patente(patente)
        
        if vehiculo:
            st.success("Vehículo encontrado:")
            
            # Mostrar los datos en formato de tarjetas (similar a tu estilo)
            with st.container():
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Patente", vehiculo.get('Patente', 'N/A'))
                with cols[1]:
                    st.metric("Marca", vehiculo.get('Marca', 'N/A'))
                with cols[2]:
                    st.metric("Modelo", vehiculo.get('Modelo', 'N/A'))
                with cols[3]:
                    st.metric("Año", vehiculo.get('Año', 'N/A'))
            
            with st.container():
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Dueño", vehiculo.get('Dueño', 'N/A'))
                with cols[1]:
                    st.metric("Teléfono", vehiculo.get('Teléfono', 'N/A'))
                with cols[2]:
                    st.metric("Último Servicio", vehiculo.get('Último_Servicio', 'N/A'))
            
            # Mostrar historial completo (si existe)
            if 'Historial' in vehiculo:
                st.subheader("Historial de Servicios")
                st.write(vehiculo['Historial'])
        else:
            st.warning("No se encontró ningún vehículo con esa patente")

# ----------------------------------------------------------------------------------------------------------------------------------
# Opción para ver todos los vehículos
with st.expander("Ver todos los vehículos registrados"):
    st.dataframe(veiculos_data, hide_index=True)
