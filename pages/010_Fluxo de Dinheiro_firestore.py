# Create the full Firestore-based version of the file, preserving UI and logic,
# replacing only the persistence layer (Google Sheets -> Firestore).

import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, date
from calendar import monthrange
import calendar

# Firestore
from firebase_config import db

categorias = [
    "agua", "aluguel", "borracharia", "cartão de todos", "combustivel",
    "contadora", "credito celular", "devida", "energia", "ferramentas",
    "guincho", "internet", "limpeça", "marmitas", "mercearia", "outros",
    "papelaria", "peças", "redes sociais", "serviços outros",
    "transporte", "vales", "venda", "bombeiros"
]

def safe_float(valor):
    """Convierte cualquier valor a float de manera segura"""
    if pd.isna(valor) or valor in [None, '']:
        return 0.0
    
    if isinstance(valor, (int, float)):
        return float(valor)

    try:
        str_valor = str(valor).strip().replace('R$', '').replace('$', '').replace('"', '')
        
        # 🇧🇷 Caso: formato brasileiro "1.234,56"
        if '.' in str_valor and ',' in str_valor:
            str_valor = str_valor.replace('.', '').replace(',', '.')
        elif ',' in str_valor:  # "1234,56"
            str_valor = str_valor.replace(',', '.')

        return float(str_valor)
    except Exception as e:
        print(f"Error convertiendo valor: '{valor}'. Error: {e}")
        return 0.0


def carregar_dados():
    docs = db.collection("fluxo").stream()
    rows = []
    for d in docs:
        r = d.to_dict() or {}
        r["_doc_id"] = d.id
        rows.append(r)
    df = pd.DataFrame(rows)
    
    if df.empty:
        return df
    
    if "data_pag" in df.columns:
        df["data_pag"] = pd.to_datetime(df["data_pag"], dayfirst=True, errors="coerce").dt.date
        if "data" in df.columns:
            df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.date
            df["data_pag"] = df["data_pag"].fillna(df["data"])

    if "valor" in df.columns:
        df["valor"] = df["valor"].apply(safe_float)
    return df

def obter_proximo_id(df):
    if df.empty or 'ids' not in df.columns:
        return 1
    try:
        return int(df['ids'].max()) + 1
    except:
        return 1

def adicionar_lancamento(status, data, data_pag, cliente, descricao, categoria, carro, placa, motivo, forma, valor):
    df = carregar_dados()
    novo_id = obter_proximo_id(df)

    data_fmt = pd.to_datetime(data).strftime("%d/%m/%Y")
    data_pag_fmt = pd.to_datetime(data_pag if data_pag else data).strftime("%d/%m/%Y")

    doc = {
        "ids": int(novo_id),
        "data": data_fmt,
        "data_pag": data_pag_fmt,
        "cliente": cliente,
        "descricao": descricao,
        "categoria": categoria,
        "carro": carro,
        "placa": placa,
        "motivo": motivo,
        "form": forma,
        "valor": float(valor),
        "status": status
    }
    db.collection("fluxo").add(doc)
    return novo_id

def atualizar_linha_por_id(id_alvo, novos_dados):
    q = db.collection("fluxo").where("ids", "==", int(id_alvo)).limit(1).get()
    if not q:
        return False
    ref = q[0].reference
    payload = {
        "ids": int(novos_dados[0]),
        "data": novos_dados[1],
        "data_pag": novos_dados[2],
        "cliente": novos_dados[3],
        "descricao": novos_dados[4],
        "carro": novos_dados[5],
        "placa": novos_dados[6],
        "motivo": novos_dados[7],
        "form": novos_dados[8],
        "valor": safe_float(novos_dados[9]),
        "status": novos_dados[10],
    }
    ref.update(payload)
    return True

def excluir_linha_por_id(id_alvo):
    q = db.collection("fluxo").where("ids", "==", int(id_alvo)).limit(1).get()
    if not q:
        return False
    q[0].reference.delete()
    return True

def formatar_dos(valor):
    try:
        valor_float = float(valor)
        return f"{valor_float:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except (ValueError, TypeError):
        return "0,00"

def formatar_real(valor, padrao="0,00"):
    try:
        if pd.isna(valor) or valor in [None, '']:
            return f"R$ {padrao}"
        if isinstance(valor, str):
            valor = valor.replace("R$", "").replace(".", "").replace(",", ".")
        valor_float = float(valor)
        return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"R$ {padrao}"

# Interface (idéntica al original)
st.set_page_config(page_title="💰 Fluxo de Caixa", page_icon="💰", layout="wide")
st.title("💰 Fluxo de Caixa")

aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "➕ Novo Lançamento", 
    "📋 Lançamentos", 
    "🛠️ Editar / Remover", 
    "📊 Resumo Financeiro",
    "📈 Análise de Gastos",
    "🔍 Buscar Gastos"
])

with aba1:
    st.subheader("➕ Novo Registro")
    with st.form("form_novo_lancamento"):
        cols = st.columns(3)
        with cols[0]:
            tipo = st.selectbox("Tipo", ["entrada", "saida", "pendente"])
        with cols[1]:
            data = st.date_input("Data do lançamento")
        with cols[2]:
            data_pag = st.date_input("Data de pagamento prevista", value=None) if tipo == "pendente" else None

        cols = st.columns(3)
        with cols[1]:
            cliente = st.text_input("Cliente")

        descricao = st.text_input("Descrição")
        categoria = st.selectbox("Categoria", categorias)

        cols = st.columns(4)
        with cols[1]:
            carro = st.text_input("Carro")
        with cols[2]:
            placa = st.text_input("Placa")

        motivo = st.text_input("Fornecedor")

        cols = st.columns(4)
        with cols[1]:
            forma = st.selectbox("Forma de pagamento", ["Dinheiro", "PIX", "Debito", "Credito", "C6", "TON", "Boleto", "outro"])
        with cols[2]:
            valor = st.number_input("Valor", min_value=0.0, format="%.2f")

        submit = st.form_submit_button("Salvar Registro")

        if submit:
            adicionar_lancamento(tipo, data, data_pag, cliente, descricao, categoria, carro, placa, motivo, forma, valor)
            st.success("Registro salvo com sucesso!")
            st.rerun()

with aba2:
    st.subheader("📋 Lançamentos")
    df = carregar_dados()
    if not df.empty:
        df["status"] = df["status"].astype(str).str.strip().str.lower()
        df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors='coerce').dt.date
        # Orden y columnas
        col_order = [
            "ids", "data", "data_pag", "cliente", "descricao", "categoria",
            "carro", "placa", "motivo", "forma", "valor", "status", "migrado"
        ]
        
        # Asegurar columnas existentes
        for c in col_order:
            if c not in df_tipo.columns:
                df_tipo[c] = ""
        
        df_tipo = df_tipo[col_order]
        
        # Ordenar por ID descendente
        df_tipo = df_tipo.sort_values("ids", ascending=False)
        
        st.dataframe(df_tipo, use_container_width=True, hide_index=True)

    else:
        st.info("Nenhum registro.")

with aba3:
    st.subheader("🛠️ Editar ou Remover Lançamento por ID")
    df = carregar_dados()
    if df.empty:
        st.info("Nenhum lançamento encontrado.")
    else:
        df["ids"] = df["ids"].astype(int)
        ids_disponiveis = df["ids"].sort_values(ascending=False).tolist()
        id_escolhido = st.selectbox("Selecione o ID do lançamento", ids_disponiveis)
        lancamento = df[df["ids"] == id_escolhido].iloc[0]

        with st.form("form_edicao_id"):
            nova_data = st.date_input("Data", pd.to_datetime(lancamento["data"], dayfirst=True))
            nova_data_pag = st.date_input("Data Pagamento", pd.to_datetime(lancamento["data_pag"], dayfirst=True))
            novo_cliente = st.text_input("Cliente", lancamento["cliente"])
            nova_descricao = st.text_input("Descrição", lancamento["descricao"])
            novo_carro = st.text_input("Carro", lancamento["carro"])
            nova_placa = st.text_input("Placa", lancamento["placa"])
            novo_motivo = st.text_input("Motivo", lancamento["motivo"])
            nova_forma = st.text_input("Forma", lancamento["forma"])
            novo_valor = st.number_input("Valor", value=float(lancamento["valor"]))
            novo_status = st.selectbox("Status", ["entrada", "saida", "pendente"], index=["entrada","saida","pendente"].index(lancamento["status"]))

            col1, col2 = st.columns(2)
            with col1:
                editar = st.form_submit_button("💾 Salvar Alterações")
            with col2:
                excluir = st.form_submit_button("🗑️ Remover")

        if editar:
            novos_dados = [
                id_escolhido,
                nova_data.strftime("%d/%m/%Y"),
                nova_data_pag.strftime("%d/%m/%Y"),
                novo_cliente,
                nova_descricao,
                novo_carro,
                nova_placa,
                novo_motivo,
                nova_forma,
                novo_valor,
                novo_status
            ]
            if atualizar_linha_por_id(id_escolhido, novos_dados):
                st.success("Atualizado!")
                st.rerun()

        if excluir:
            if excluir_linha_por_id(id_escolhido):
                st.success("Removido!")
                st.rerun()

with aba4:
    st.subheader("📊 Resumo Financeiro")
    df = carregar_dados()
    if df.empty:
        st.info("Sem dados.")
    else:
        df["status"] = df["status"].astype(str).str.lower()
        df["valor"] = df["valor"].apply(safe_float)
        total_entrada = df[df["status"]=="entrada"]["valor"].sum()
        total_saida = df[df["status"]=="saida"]["valor"].sum()
        saldo = total_entrada - total_saida
        c1,c2,c3 = st.columns(3)
        c1.metric("Entradas", formatar_real(total_entrada))
        c2.metric("Saídas", formatar_real(total_saida))
        c3.metric("Saldo", formatar_real(saldo))

with aba5:
    st.subheader("📈 Análise de Gastos")
    df = carregar_dados()
    if not df.empty:
        df = df[df["status"]=="saida"]
        if not df.empty:
            agrupado = df.groupby("categoria")["valor"].sum().sort_values(ascending=False)
            st.bar_chart(agrupado)

with aba6:
    st.subheader("🔍 Buscar Gastos")
    df = carregar_dados()
    termo = st.text_input("Buscar").strip().lower()
    if termo and not df.empty:
        filtro = (
            df["carro"].astype(str).str.lower().str.contains(termo) |
            df["placa"].astype(str).str.lower().str.contains(termo) |
            df["descricao"].astype(str).str.lower().str.contains(termo) |
            df["cliente"].astype(str).str.lower().str.contains(termo) |
            df["motivo"].astype(str).str.lower().str.contains(termo)
        )
        resultados = df[filtro]
        st.dataframe(resultados, use_container_width=True, hide_index=True)

