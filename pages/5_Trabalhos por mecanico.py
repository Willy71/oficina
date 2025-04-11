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

# Autenticación
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'
SHEET_NAME = 'Hoja 1'

credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)
worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)

def cargar_datos():
    datos = worksheet.get_all_records()
    df = pd.DataFrame(datos)
    df["date_in"] = pd.to_datetime(df["date_in"], errors='coerce')
    
    # Convertir todos los valores de servicio a numéricos (del 1 al 12)
    for i in range(1, 13):
        df[f"valor_serv_{i}"] = pd.to_numeric(df.get(f"valor_serv_{i}", 0), errors='coerce')
    
    return df

def formatar_dos(valor):
    try:
        valor_float = float(valor)
        return f"{valor_float:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except (ValueError, TypeError):
        return "0,00"

# -------------------------- CONSULTA DE TRABAJOS ------------------------------
st.title("🛠️ Relatório de Trabalhos por Mecânico")

with st.sidebar:
    st.header("🔍 Filtros")
    data_inicial = st.date_input("Data inicial", datetime(datetime.now().year, datetime.now().month, 1))
    data_final = st.date_input("Data final", datetime.now())
    comissao_pct = st.slider("% Comissão do mecânico", 0.0, 100.0, 40.0, step=5.0)

# ------------------------ FILTRAR E AGRUPAR ----------------------------------
df = cargar_datos()
df_filtrado = df[(df['date_in'] >= pd.to_datetime(data_inicial)) & (df['date_in'] <= pd.to_datetime(data_final))]

# Remover linhas sem mecânico
df_filtrado = df_filtrado[df_filtrado['mecanico'].notna() & (df_filtrado['mecanico'] != '')]

# Calcular total de serviços (sem peças)
df_filtrado["total_servicos"] = df_filtrado[[f"valor_serv_{i}" for i in range(1, 13)]].sum(axis=1, skipna=True)

resultado["total_servicos_fmt"] = resultado["total_servicos"].apply(formatar_dos)
resultado["comissao_fmt"] = resultado["comissao"].apply(formatar_dos)

# -------------------------- EXIBIR RESULTADO ---------------------------------
st.subheader("📊 Resumo por Mecânico")
st.dataframe(resultado[["mecanico", "total_servicos_fmt", "comissao_fmt"]], use_container_width=True)

# Mostrar totais
total_geral = resultado["total_servicos"].sum()
total_comissao = resultado["comissao"].sum()

st.markdown(f"**🔧 Total de serviços no período:** R$ {formatar_dos(total_geral)}")
st.markdown(f"**💰 Total de comissões:** R$ {formatar_dos(total_comissao)} ({comissao_pct:.0f}%)")




