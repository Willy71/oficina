import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --------------------------- CONFIG INICIAL ----------------------------------
st.set_page_config(page_title="Trabalhos por Mecânico", layout="wide", page_icon="🛠️")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] > .main {
    background-color: #00001a;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --------------------------- CARGAR PLANILHA ----------------------------------
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SPREADSHEET_KEY = st.secrets["SPREADSHEET_KEY"]
SHEET_NAME = 'Hoja 1'

credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO)
gc = gspread.authorize(credentials)
worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)

@st.cache_data(ttl=600)
def cargar_datos():
    datos = worksheet.get_all_records()
    df = pd.DataFrame(datos)
    df["date_in"] = pd.to_datetime(df["date_in"], errors='coerce')
    
    # Convertir todos los valores de servicio a numéricos (del 1 al 12)
    for i in range(1, 13):
        df[f"valor_serv_{i}"] = pd.to_numeric(df.get(f"valor_serv_{i}", 0), errors='coerce')
    
    return df


# -------------------------- CONSULTA DE TRABAJOS ------------------------------
st.title("🛠️ Relatório de Trabalhos por Mecânico")

with st.sidebar:
    st.header("🔍 Filtros")
    data_inicial = st.date_input("Data inicial", datetime(datetime.now().year, datetime.now().month, 1))
    data_final = st.date_input("Data final", datetime.now())
    comissao_pct = st.slider("% Comissão do mecânico", 0.0, 100.0, 40.0, step=5.0)

# ------------------------ FILTRAR E AGRUPAR ----------------------------------
df = cargar_datos()
df_filtrado["total_servicos"] = df_filtrado[[f"valor_serv_{i}" for i in range(1, 13)]].sum(axis=1, skipna=True)

# Remover linhas sem mecânico
df_filtrado = df_filtrado[df_filtrado['mecanico'].notna() & (df_filtrado['mecanico'] != '')]

# Calcular total de serviços (sem peças)
df_filtrado["total_servicos"] = df_filtrado[["valor_serv_1", "valor_serv_2", "valor_serv_3"]].sum(axis=1, skipna=True)

# Agrupar por mecânico
resultado = df_filtrado.groupby("mecanico")["total_servicos"].sum().reset_index()
resultado["comissao"] = resultado["total_servicos"] * (comissao_pct / 100)

# -------------------------- EXIBIR RESULTADO ---------------------------------
st.subheader("📊 Resumo por Mecânico")
st.dataframe(resultado, use_container_width=True)

# Mostrar totais
total_geral = resultado["total_servicos"].sum()
total_comissao = resultado["comissao"].sum()

st.markdown(f"**🔧 Total de serviços no período:** R$ {total_geral:,.2f}")
st.markdown(f"**💰 Total de comissões:** R$ {total_comissao:,.2f} ({comissao_pct:.0f}%)")
