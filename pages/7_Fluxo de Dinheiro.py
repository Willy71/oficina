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

def salvar_dados(df):
    sheet.clear()
    sheet.append_row(df.columns.tolist())  # Encabezados
    for _, row in df.iterrows():
        sheet.append_row(row.tolist())

# Interface
st.set_page_config("Fluxo de Caixa", layout="wide")
st.title("💰 Fluxo de Caixa")

aba1, aba2, aba3, aba4 = st.tabs(["➕ Novo Lançamento", "📋 Lançamentos", "🛠️ Editar / Remover", "📊 Resumo Financeiro"])

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
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["status"] = df["status"].str.strip().str.lower()  # 👈 esto faltaba
    
    st.write("📄 Dados carregados:", df.shape)
    st.dataframe(df)

    #st.markdown("### 📊 Resumo Financeiro")
    total_entrada = df[df["status"] == "entrada"]["valor"].sum()
    total_saida = df[df["status"] == "saida"]["valor"].sum()
    total_pendente = df[df["status"] == "pendente"]["valor"].sum()
    saldo = total_entrada - total_saida

with aba3:
    st.subheader("🛠️ Editar ou Remover Lançamento")

    df = carregar_dados()
    st.write("📄 Dados carregados:", df.shape)

    if df.empty:
        st.info("Nenhum lançamento encontrado.")
    else:
        # Mostrar lista de lançamentos com índice para escolha
        opcoes = df["descricao"] + " | " + df["cliente"] + " | R$ " + df["valor"].astype(str) + " | " + df["status"]
        escolha = st.selectbox("Selecione um lançamento para editar ou remover:", opcoes)

        if escolha:
            idx = opcoes[opcoes == escolha].index[0]
            lancamento = df.loc[idx]

            # Formulário de edição
            with st.form("form_edicao"):
                nova_data = st.date_input("Data", pd.to_datetime(lancamento["data"]))
                # Verifica se a data_pag é válida
                try:
                    data_pag_padrao = pd.to_datetime(lancamento["data_pag"])
                    if pd.isnull(data_pag_padrao):
                        data_pag_padrao = datetime.today()
                except Exception:
                    data_pag_padrao = datetime.today()
                
                nova_data_pag = st.date_input("Data Pagamento (se aplicável)", data_pag_padrao)

                novo_cliente = st.text_input("Cliente", lancamento["cliente"])
                nova_descricao = st.text_input("Descrição", lancamento["descricao"])
                novo_carro = st.text_input("Carro", lancamento["carro"])
                nova_placa = st.text_input("Placa", lancamento["placa"])
                novo_motivo = st.text_input("Motivo", lancamento["motivo"])
                opcoes_forma = ["dinheiro", "pix", "cartão", "outro"]
                valor_atual_forma = lancamento["form"].strip().lower()      
                if valor_atual_forma in opcoes_forma:
                    idx_forma = opcoes_forma.index(valor_atual_forma)
                else:
                    idx_forma = 0  # default: "dinheiro"
                nova_forma = st.selectbox("Forma de Pagamento", opcoes_forma, index=idx_forma)
                try:
                    valor_padrao = float(str(lancamento["valor"]).replace("R$", "").replace(",", ".").strip())
                except Exception:
                    valor_padrao = 0.0
                
                novo_valor = st.number_input("Valor", value=valor_padrao)

                novo_status = st.selectbox("Status", ["entrada", "saida", "pendente"], index=["entrada", "saida", "pendente"].index(lancamento["status"]))

                col1, col2 = st.columns(2)
                with col1:
                    editar = st.form_submit_button("💾 Salvar Alterações")
                with col2:
                    excluir = st.form_submit_button("🗑️ Remover")

            if editar:
                df.at[idx, "data"] = nova_data.strftime("%Y-%m-%d")
                df.at[idx, "data_pag"] = nova_data_pag.strftime("%Y-%m-%d")
                df.at[idx, "cliente"] = novo_cliente
                df.at[idx, "descricao"] = nova_descricao
                df.at[idx, "carro"] = novo_carro
                df.at[idx, "placa"] = nova_placa
                df.at[idx, "motivo"] = novo_motivo
                df.at[idx, "form"] = nova_forma
                df.at[idx, "valor"] = novo_valor
                df.at[idx, "status"] = novo_status

                salvar_dados(df)
                st.success("Lançamento atualizado com sucesso!")

            if excluir:
                df = df.drop(idx).reset_index(drop=True)
                salvar_dados(df)
                st.success("Lançamento removido com sucesso!")


with aba4:
    st.subheader("📊 Resumen Financeiro")
    
    # Cargar y preparar datos
    df = carregar_dados()
    
    # Asegurar que los datos están limpios
    df["status"] = df["status"].str.strip().str.lower()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    
    # Filtrar y calcular totales
    total_entrada = df[df["status"] == "entrada"]["valor"].sum()
    total_saida = df[df["status"] == "saida"]["valor"].sum()
    total_pendente = df[df["status"] == "pendente"]["valor"].sum()
    saldo = total_entrada - total_saida
    
    # Mostrar métricas con formato correcto
    def formatar_valor(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🟢 Entradas", formatar_valor(total_entrada))
    col2.metric("🔴 Saídas", formatar_valor(total_saida))
    col3.metric("🟡 Pendentes", formatar_valor(total_pendente))
    col4.metric("💰 Saldo", formatar_valor(saldo))
    
    # Gráfico
    df_grafico = pd.DataFrame({
        "Tipo": ["Entradas", "Saídas", "Pendentes"],
        "Valor": [total_entrada, total_saida, total_pendente]
    })
    
    fig = px.bar(df_grafico, x="Tipo", y="Valor", text_auto=".2s", color="Tipo",
                 color_discrete_map={"Entradas": "green", "Saídas": "red", "Pendentes": "orange"})
    fig.update_layout(title="Totais por Tipo", xaxis_title="", yaxis_title="R$")
    st.plotly_chart(fig, use_container_width=True)
