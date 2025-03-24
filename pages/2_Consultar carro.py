# 2_Consultar_carro.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ----------------------------------------------------------------------------------------------------------------------------------
# Configuración de página (igual que en tu código original)
st.set_page_config(
    page_title="Consultar Veículo",
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
st.title("Consultar Veículo por Placa")

# ----------------------------------------------------------------------------------------------------------------------------------
# Conexión a Google Sheets (usando tu misma configuración)
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

SPREADSHEET_KEY = '1ndVk4efZZN74serPvDpN6tcm2NamLqKlcYfz2-y156g'
SHEET_NAME = 'Hoja1'  # Usamos la misma hoja que en tu gestión de reservas

try:
    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
    dados = pd.DataFrame(worksheet.get_all_records())
    
    # Verificamos si la columna de placas existe
    if 'placa' not in dados.columns:
        st.error("A coluna 'placa' não foi encontrada na planilha.")
        dados = pd.DataFrame()  # DataFrame vazio para evitar erro
except Exception as e:
    st.error(f"Erro ao acessar a planilha: {e}")
    dados = pd.DataFrame()  # DataFrame vazio para evitar erro

# ----------------------------------------------------------------------------------------------------------------------------------
# Função para buscar veículo por placa
def buscar_por_placa(placa):
    if not dados.empty and 'Placa' in dados.columns:
        # Busca coincidencias exactas (ignorando mayúsculas/minúsculas)
        resultado = dados[dados['Placa'].astype(str).str.upper() == placa.upper()]
        return None if resultado.empty else resultado.iloc[0]
    return None

# ----------------------------------------------------------------------------------------------------------------------------------
# Interfaz de usuario
with st.container():
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        placa = st.text_input("Digite a placa do veículo:", "").strip().upper()
    
    with col2:
        st.write("")  # Espaciador
        buscar = st.button("Buscar Veículo")

if buscar and placa:
    if not placa.isalnum():  # Validación básica de placa
        st.warning("Por favor, insira uma placa válida (apenas letras e números)")
    else:
        with st.spinner("Buscando veículo..."):
            veiculo = buscar_por_placa(placa)
            
            if veiculo is not None:
                st.success("Veículo encontrado:")
                
                # Mostrar los datos en formato de tarjetas
                with st.container():
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("Placa", veiculo.get('Placa', 'N/A'))
                    with cols[1]:
                        st.metric("Marca", veiculo.get('Marca', 'N/A'))
                    with cols[2]:
                        st.metric("Modelo", veiculo.get('Modelo', 'N/A'))
                    with cols[3]:
                        st.metric("Ano", veiculo.get('Ano', 'N/A'))
                
                with st.container():
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Proprietário", veiculo.get('Proprietário', 'N/A'))
                    with cols[1]:
                        st.metric("Telefone", veiculo.get('Telefone', 'N/A'))
                    with cols[2]:
                        st.metric("Última Revisão", veiculo.get('Última_Revisão', 'N/A'))
                
                # Mostrar todos los datos disponibles
                with st.expander("Ver todos os detalhes"):
                    st.json(veiculo.to_dict())
            else:
                st.warning("Nenhum veículo encontrado com esta placa")

# Mostrar todos los vehículos si hay datos
if not dados.empty and 'Placa' in dados.columns:
    with st.expander("Ver todos os veículos registrados"):
        st.dataframe(dados[['Placa', 'Marca', 'Modelo', 'Proprietário']], hide_index=True)
else:
    st.info("Nenhum dado de veículo disponível na planilha")
