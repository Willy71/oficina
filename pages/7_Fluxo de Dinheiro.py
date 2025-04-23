import streamlit as st
import pandas as pd
import gspread
import uuid
from google.oauth2.service_account import Credentials
from datetime import datetime
import plotly.express as px

# Conexão com Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SPREADSHEET_KEY = "1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4"
SHEET_NAME = "fluxo"

credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)

# Funções utilitárias
def carregar_dados():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def adicionar_lancamento(status, data, data_pag, cliente, descricao, carro, placa, motivo, forma, valor):
    novo_id = str(uuid.uuid4())
    nova_linha = [novo_id, str(data), str(data_pag) if data_pag else "", cliente, descricao, carro, placa, motivo, forma, valor, status]
    sheet.append_row(nova_linha)
    return novo_id

def atualizar_linha_por_id(id_alvo, novos_dados):
    df = carregar_dados()
    if id_alvo in df["ids"].values:
        linha = df[df["ids"] == id_alvo].index[0] + 2  # +2 por cabeçalho e índice 0-based
        for i, valor in enumerate(novos_dados):
            sheet.update_cell(linha, i + 1, valor)
        return True
    return False

def excluir_linha_por_id(id_alvo):
    df = carregar_dados()
    if id_alvo in df["ids"].values:
        linha = df[df["ids"] == id_alvo].index[0] + 2
        sheet.delete_rows(linha)
        return True
    return False

# Interface
st.set_page_config("Fluxo de Caixa", layout="wide")
st.title("💰 Fluxo de Caixa")

aba1, aba2, aba3, aba4 = st.tabs(["➕ Novo Registro", "📋 Ver Lançamentos", "✏️ Editar", "🗑️ Excluir"])

with aba1:
    st.subheader("➕ Novo Registro")
    tipo = st.selectbox("Tipo", ["entrada", "saida", "pendente"])
    data = st.date_input("Data do lançamento")
    data_pag = st.date_input("Data de pagamento prevista", value=None) if tipo == "pendente" else None
    cliente = st.text_input("Cliente")
    descricao = st.text_input("Descrição")
    carro = st.text_input("Carro")
    placa = st.text_input("Placa")
    motivo = st.text_input("Motivo")
    forma = st.selectbox("Forma de pagamento", ["dinheiro", "pix", "cartão", "boleto", "outro"])
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    if st.button("Salvar Registro"):
        adicionar_lancamento(tipo, data, data_pag, cliente, descricao, carro, placa, motivo, forma, valor)
        st.success("Registro salvo com sucesso!")

with aba2:
    st.subheader("📋 Lançamentos")
    df = carregar_dados()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)  # 🔧 fix

    st.markdown("### 📊 Resumo Financeiro")
    total_entrada = df[df["status"] == "entrada"]["valor"].sum()
    total_saida = df[df["status"] == "saida"]["valor"].sum()
    total_pendente = df[df["status"] == "pendente"]["valor"].sum()
    saldo = total_entrada - total_saida

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🟢 Entradas", f"R$ {total_entrada:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("🔴 Saídas", f"R$ {total_saida:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col3.metric("🟡 Pendentes", f"R$ {total_pendente:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col4.metric("💰 Saldo", f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta=f"{saldo:.2f}")

    df_grafico = pd.DataFrame({
        "Tipo": ["Entradas", "Saídas", "Pendentes"],
        "Valor": [total_entrada, total_saida, total_pendente]
    })
    fig = px.bar(df_grafico, x="Tipo", y="Valor", text_auto=".2s", color="Tipo",
                 color_discrete_map={
                     "Entradas": "green",
                     "Saídas": "red",
                     "Pendentes": "orange"
                 })
    fig.update_layout(title="Totais por Tipo", xaxis_title="", yaxis_title="R$")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)




