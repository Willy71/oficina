import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials, Credentials
from datetime import datetime

# Conectar a Google Sheets
# Autenticación
# Datos de conexión
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'
SHEET_NAME = 'fluxo'

# Autenticación con Google
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
client = gspread.authorize(credentials)

# Abrir hoja
sheet = client.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Formatar colunas
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df['data_pag'] = pd.to_datetime(df['data_pag'], errors='coerce')
df['valor'] = pd.to_numeric(df['valor'], errors='coerce')

# Tabs
aba1, aba2, aba3 = st.tabs(["📊 Resumo Geral", "🕒 Pendentes", "📋 Todos os Lançamentos"])

with aba1:
    st.header("📊 Resumo Geral do Fluxo")

    entradas = df[df['status'] == 'entrada']['valor'].sum()
    saidas = df[df['status'] == 'saida']['valor'].sum()
    pendentes = df[df['status'] == 'pendente']['valor'].sum()
    saldo = entradas - saidas

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Entradas", f"R$ {entradas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    col2.metric("Saídas", f"R$ {saidas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    col3.metric("Pendentes", f"R$ {pendentes:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    col4.metric("Saldo", f"R$ {saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    # Criar coluna mês/ano para agrupamento
    df['mes_ano'] = df['data'].dt.to_period('M').astype(str)
    fluxo_mensal = df[df['status'].isin(['entrada', 'saida'])].groupby(['mes_ano', 'status'])['valor'].sum().unstack().fillna(0)
    fluxo_mensal['saldo'] = fluxo_mensal.get('entrada', 0) - fluxo_mensal.get('saida', 0)

    st.line_chart(fluxo_mensal[['entrada', 'saida', 'saldo']])

with aba2:
    st.header("🕒 Pagamentos Pendentes")
    pend_df = df[df['status'] == 'pendente'].copy()
    pend_df = pend_df.sort_values(by='data_pag')
    st.dataframe(pend_df, use_container_width=True)

with aba3:
    st.header("📋 Todos os Lançamentos")

    status_opcao = st.multiselect("Filtrar por status", df['status'].unique(), default=df['status'].unique())
    cliente_opcao = st.multiselect("Filtrar por cliente", df['cliente'].unique(), default=df['cliente'].unique())

    df_filtrado = df[df['status'].isin(status_opcao) & df['cliente'].isin(cliente_opcao)]
    df_filtrado = df_filtrado.sort_values(by='data', ascending=False)

    st.dataframe(df_filtrado, use_container_width=True)
