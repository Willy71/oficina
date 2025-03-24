# 2_Consultar_carro.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuración de página (igual que tu código original)
st.set_page_config(
    page_title="Consultar Veículo",
    page_icon=":car:",
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

# Título de la página
st.title("🔍 Consultar Veículo")

# ----------------------------------------------------------------------------------------------------------------------------------
# Conexión a Google Sheets (mismo método que usas)
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

SPREADSHEET_KEY = '1ndVk4efZZN74serPvDpN6tcm2NamLqKlcYfz2-y156g'
SHEET_NAME = 'Hoja1'

try:
    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
    dados = pd.DataFrame(worksheet.get_all_records())
    
    # Verificamos columnas disponibles para identificar vehículos
    colunas_disponiveis = dados.columns.tolist()
    
    # Sugerimos columnas que podrían contener la placa
    possiveis_colunas_placa = [col for col in colunas_disponiveis if 'placa' in col.lower() or 'matrícula' in col.lower() or 'patente' in col.lower()]
    
    if not possiveis_colunas_placa:
        st.warning("Não foi encontrada uma coluna específica para placas de veículos.")
        st.info("Colunas disponíveis na planilha: " + ", ".join(colunas_disponiveis))
        
except Exception as e:
    st.error(f"Erro ao acessar a planilha: {e}")
    dados = pd.DataFrame()

# ----------------------------------------------------------------------------------------------------------------------------------
# Interfaz de usuario mejorada
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        # Si encontramos posibles columnas de placa
        if 'possiveis_colunas_placa' in locals() and possiveis_colunas_placa:
            coluna_placa = st.selectbox(
                "Selecione a coluna que contém as placas:",
                options=possiveis_colunas_placa,
                index=0
            )
            placa = st.text_input(f"Digite a placa do veículo ({coluna_placa}):", "").strip().upper()
        else:
            placa = st.text_input("Digite a placa/identificação do veículo:", "").strip().upper()
    
    with col2:
        st.write("")  # Espaciador
        buscar = st.button("Buscar Veículo")

if buscar and placa:
    if not dados.empty:
        try:
            # Buscamos en la columna seleccionada o en todas las columnas posibles
            resultados = []
            if 'coluna_placa' in locals():
                resultados = dados[dados[coluna_placa].astype(str).str.upper() == placa.upper()]
            else:
                # Búsqueda en todas las columnas si no se identificó columna de placa
                for col in dados.columns:
                    if dados[col].dtype == object:
                        resultados.extend(dados[dados[col].astype(str).str.upper() == placa.upper()].to_dict('records'))
            
            if len(resultados) > 0:
                st.success("Registro(s) encontrado(s):")
                for i, registro in enumerate(resultados[:3]):  # Mostramos máximo 3 resultados
                    with st.expander(f"Registro {i+1}"):
                        st.json(registro)
            else:
                st.warning("Nenhum registro encontrado com esta identificação")
                
        except Exception as e:
            st.error(f"Erro na busca: {e}")
    else:
        st.warning("Nenhum dado disponível para busca")

# Mostrar todos los datos disponibles (con precaución)
if not dados.empty:
    with st.expander("⚠️ Visualizar todos os registros (cuidado com datos sensíveis)"):
        st.dataframe(dados, hide_index=True)
else:
    st.info("Nenhum dado disponível na planilha")
