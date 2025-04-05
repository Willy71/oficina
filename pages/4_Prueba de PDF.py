# 4_Painel_de_controle.py
import pdfkit
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
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


# Función para buscar vehículo por placa
def buscar_por_placa(placa, df):
    if df.empty:
        return None
    
    # Buscar coincidencias exactas (ignorando mayúsculas/minúsculas y espacios)
    resultado = df[df['placa'].astype(str).str.upper().str.strip() == placa.upper().strip()]
    
    if not resultado.empty:
        return resultado.iloc[-1].to_dict()  # Tomar el último ingreso en lugar del primero
    return None



# Inicializar la hoja de cálculo
worksheet = inicializar_hoja()

# Cargar datos
dados = cargar_datos(worksheet)


# ----------------------------------------------------------------------------------------------------------------------------------
placa = st.text_input("Digite a placa do veículo:", "", key="placa_input").strip().upper()
buscar = st.button("Buscar Veículo", key="buscar_btn")
if buscar:
    veiculo = buscar_por_placa(placa, dados)
    
    if veiculo:
        st.success("✅ Veículo encontrado!")

        # Por esto (usa directamente los valores del DataFrame):
        placa = veiculo["placa"]
        carro = veiculo["carro"]
        modelo = veiculo["modelo"]
        ano = veiculo["ano"]
        date_in = veiculo["date_in"]
        
        # Muestra los valores si lo deseas (opcional)
        st.write(f"Placa: {placa}")
        st.write(f"Carro: {carro}")
        st.write(f"Modelo: {modelo}")
        st.write(f"Ano: {ano}")
        st.write(f"Data de entrada: {date_in}")
        
        
        env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
        template = env.get_template("template_2.html")
                
submit = st.button("Gerar PDF")
                
if submit:
    try:
        html = template.render(
            placa=placa,
            carro=carro,
            modelo=modelo,
            ano=ano,
            date_in=date_in
        )

        pdf = pdfkit.from_string(html, False)
        st.balloons()
        
        st.success("🎉 Seu PDF foi gerado com sucesso")  # Cambiado de right.success a st.success
        
        st.download_button(  # Cambiado de right.download_button a st.download_button
            "⬇️ Download PDF",
            data=pdf,
            file_name="carro.pdf",
            mime="application/octet-stream",
        )


