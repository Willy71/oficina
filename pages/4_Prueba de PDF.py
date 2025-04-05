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

# Conexão com Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPES)
gc = gspread.authorize(creds)

@st.cache_data(ttl=600)
def carregar_dados():
    try:
        worksheet = gc.open_by_key('1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4').worksheet('Hoja 1')
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        
        # Conversão de datas
        df['date_in'] = pd.to_datetime(df['date_in'], dayfirst=True, errors='coerce')
        df['date_prev'] = pd.to_datetime(df['date_prev'], dayfirst=True, errors='coerce')
        df['date_out'] = pd.to_datetime(df['date_out'], dayfirst=True, errors='coerce')
        
        df_completo = df.copy()

        # Filtrar apenas veículos NÃO Entregados
        df_filtrado = df[~df['estado'].astype(str).str.strip().str.lower().eq('Entregado')]
        
        return df_filtrado.sort_values('date_in', ascending=False), df_completo
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()
        return pd.DataFrame()

#===================================================================================================================================================
# Título e carregamento de dados
st.title("📊 Teste para descarregar PDF")
#===================================================================================================================================================
# Carregando os dados corretamente
dados, dados_completos = carregar_dados()

# Normalizar a coluna 'estado'
dados_completos['estado'] = dados_completos['estado'].astype(str).str.strip().str.lower()

st.header(dados_completos['estado'])
