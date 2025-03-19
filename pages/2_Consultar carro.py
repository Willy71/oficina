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
# Conexion via gspread a traves de https://console.cloud.google.com/ y Google sheets

# Ruta al archivo de credenciales
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]

# Scopes necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales y autorizar
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

# Clave de la hoja de cálculo (la parte de la URL después de "/d/" y antes de "/edit")
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'  # Reemplaza con la clave de tu documento
SHEET_NAME = 'Hoja 1'  # Nombre de la hoja dentro del documento

try:
    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
    existing_data = pd.DataFrame(worksheet.get_all_records())
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"No se encontró la hoja de cálculo con la clave '{SPREADSHEET_KEY}'. Asegúrate de que la clave es correcta y que has compartido la hoja con el correo electrónico del cliente de servicio.")
#=============================================================================================================================

def centrar_imagen(imagen, ancho):
    # Aplicar estilo CSS para centrar la imagen con Markdown
    st.markdown(
        f'<div style="display: flex; justify-content: center;">'
        f'<img src="{imagen}" width="{ancho}">'
        f'</div>',
        unsafe_allow_html=True
    )


def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>",
                unsafe_allow_html=True)


# Obtener las fechas de ocupación para un cuarto seleccionado
def get_occupied_dates(selected_room, occupancy_data):
    entry_dates = []
    entry_times = []
    exit_dates = []
    exit_times = []
    occupied_dates = []

    for _, row in occupancy_data[occupancy_data["Quarto"] == selected_room].iterrows():
        fecha_entrada = datetime.strptime(row["Data de entrada"], "%d/%m/%Y")
        entry_dates.append(fecha_entrada.strftime("%Y-%m-%d"))
        entry_times.append(row["Hora de entrada"])

        # Verificar si las columnas de hora de entrada y salida existen en el DataFrame
        if "Hora de entrada" in row.index and "Hora de saida" in row.index:
            hora_entrada = row["Hora de entrada"]
            hora_saida = row["Hora de saida"]
        else:
            # En caso de que no existan, asumir horas por defecto
            hora_entrada = "00:00"
            hora_saida = "00:00"

        # Convertir a objetos de fecha y hora
        fecha_saida = datetime.strptime(row["Data de saida"], "%d/%m/%Y")
        exit_dates.append(fecha_saida.strftime("%Y-%m-%d"))
        exit_times.append(hora_saida)

        # Añadir días al rango de fechas
        current_date = fecha_entrada
        while current_date <= fecha_saida:
            occupied_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

    # Asegurarse de que todas las listas tengan la misma longitud
    max_length = max(len(entry_dates), len(entry_times), len(exit_dates), len(exit_times), len(occupied_dates))
    entry_dates += [''] * (max_length - len(entry_dates))
    entry_times += [''] * (max_length - len(entry_times))
    exit_dates += [''] * (max_length - len(exit_dates))
    exit_times += [''] * (max_length - len(exit_times))
    occupied_dates += [''] * (max_length - len(occupied_dates))

    return entry_dates, entry_times, exit_dates, exit_times, occupied_dates

# Titulo de la pagina
centrar_texto("Consultar carro - Histórico", 1, "white")

# ----------------------------------------------------------------------------------------------------------------------------
# Widget para seleccionar el "Quarto" (Room)
#room_options = sorted(existing_data["Quarto"].astype(int).unique())
#selected_room = st.selectbox("Selecione o Quarto:", room_options)
#st.dataframe(existing_data, hide_index=True)


# Obtener las fechas ocupadas para el cuarto seleccionado
#entry_dates, entry_times, exit_dates, exit_times, occupied_dates = get_occupied_dates(selected_room, existing_data)

# Crear DataFrame con las fechas y mostrar en una tabla
#df_occupied_dates = pd.DataFrame({
#    "Hora de Entrada": entry_times,
#    "Fecha de Entrada": entry_dates,
#    "Hora de Salida": exit_times,
#    "Fecha de Salida": exit_dates,
    # "Fechas de Ocupación": occupied_dates
#})
#st.table(df_occupied_dates)
