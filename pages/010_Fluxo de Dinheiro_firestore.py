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
		df = df.dropna(subset=["data"])
		df["data"] = df["data"].dt.date
		df_tipo = df.copy()  # valor por defecto
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

#==============================================================================================================================================================
with aba4:
    st.subheader("📊 Resumo Financeiro")

    df = carregar_dados()

    # Limpieza robusta de datas
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["valor"] = df["valor"].apply(safe_float)

    df["data_pag"] = pd.to_datetime(df["data_pag"], dayfirst=True, errors='coerce')
    df = df.dropna(subset=["data_pag"])
    df["data_pag"] = df["data_pag"].dt.date

    #df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors='coerce')
    #df = df.dropna(subset=["data"])
    #df["data"] = df["data"].dt.date  # solo fecha, sin hora

    if df.empty:
        st.warning("Não há dados com datas válidas.")
    else:
        data_min = min(df["data_pag"])
        data_max = max(df["data_pag"])

        # Mostrar valores reales de rango de fechas
        st.caption(f"📅 Datas disponíveis: de {data_min.strftime('%d/%m/%Y')} até {data_max.strftime('%d/%m/%Y')}")
	#======================================================
        # Seleção de mês e ano
        col_mes, col_ano = st.columns(2)
        meses = {
            0: "Todos os períodos...",
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        mes_selecionado = col_mes.selectbox("Mês", options=list(meses.keys()), format_func=lambda x: meses[x], index=0)
        ano_atual = date.today().year
        ano_selecionado = col_ano.selectbox("Ano", options=list(range(ano_atual, ano_atual - 6, -1)))
        
        # 1) Caso “por mês/ano”
        if mes_selecionado != 0:
            # filtra diretamente pelo ano e mês
            df_filtrado = df[
                (df["data_pag"].map(lambda x: x.year)  == ano_selecionado) &
                (df["data_pag"].map(lambda x: x.month) == mes_selecionado)
            ]

        # 2) Caso “todos os períodos” (mês 0)
        else:
            # inputs de intervalo livre
            col1, col2 = st.columns(2)
            with col1:
                data_inicio = st.date_input(
                    "Data início", 
                    value=data_min,
                    min_value=data_min,
                    max_value=data_max,
                    key="inicio_resumo"
                )
            with col2:
                data_fim = st.date_input(
                    "Data fim", 
                    value=data_max,
                    min_value=data_min,
                    max_value=data_max,
                    key="fim_resumo"
                )
            df_filtrado = df[(df["data_pag"] >= data_inicio) & (df["data_pag"] <= data_fim)]

        # Se não há dados:
        if df_filtrado.empty:
            st.warning("⚠️ Nenhum lançamento encontrado para o período selecionado.")
            st.stop()

        # Cálculo de métricas
        total_entrada = df_filtrado[df_filtrado["status"] == "entrada"]["valor"].sum()
        total_saida   = df_filtrado[df_filtrado["status"] == "saida"]["valor"].sum()
        total_pendente= df_filtrado[df_filtrado["status"] == "pendente"]["valor"].sum()
        saldo         = total_entrada - total_saida

        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🟢 Entradas", formatar_real(total_entrada))
        col2.metric("🔴 Saídas", formatar_real(total_saida))
        col3.metric("🟡 Pendentes", formatar_real(total_pendente))
        col4.metric("💰 Saldo", formatar_real(saldo))

        st.markdown("---")
        st.markdown("### 📋 Filtrar lançamentos por tipo")

        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([3.5,0.5,3.5,0.5,3.5,0.5,3.5,1,1,1])
        mostrar_tipo = None
        with col1:
            if st.button("🟢 Entradas", key="btn_resumo_entradas", use_container_width=True):
                mostrar_tipo = "entrada"
        with col3:
            if st.button("🔴 Saídas", key="btn_resumo_saidas", use_container_width=True):
                mostrar_tipo = "saida"
        with col5:
            if st.button("🟡 Pendentes", key="btn_resumo_pendentes", use_container_width=True):
                mostrar_tipo = "pendente"
        with col7:
            if st.button("📋 Todos", key="btn_resumo_todos", use_container_width=True):
                mostrar_tipo = "todos"


        if mostrar_tipo:
            if mostrar_tipo == "todos":
                df_tipo = df_filtrado
                st.markdown("#### 📋 Todos os lançamentos")
            else:
                df_tipo = df_filtrado[df_filtrado["status"] == mostrar_tipo]
                cor = {"entrada": "🟢", "saida": "🔴", "pendente": "🟡"}[mostrar_tipo]
                titulo = {"entrada": "Entradas", "saida": "Saídas", "pendente": "Pendentes"}[mostrar_tipo]
                st.markdown(f"#### {cor} {titulo}")
                
            st.dataframe(df_tipo.sort_values("data_pag", ascending=False), use_container_width=True, hide_index=True)

		# --- NOVA TABELA DE RESUMO ANUAL ---
        st.markdown("---")
        if ano_selecionado:
            st.markdown(f"### Resumo Anual para {ano_selecionado}")
            df_ano = df[df['data_pag'].map(lambda x: x.year) == ano_selecionado]
            
            dados_anuais = []
            for mes_num in range(1, 13):
                df_mes = df_ano[df_ano['data_pag'].map(lambda x: x.month) == mes_num]
                
                entradas = df_mes[df_mes['status'] == 'entrada']['valor'].sum()
                saidas = df_mes[df_mes['status'] == 'saida']['valor'].sum()
                pendentes = df_mes[df_mes['status'] == 'pendente']['valor'].sum()
                lucro = entradas - saidas
                
                dados_anuais.append({
                    "Mês": meses[mes_num],
                    "Ano": ano_selecionado,
                    "Entradas": entradas,
                    "Saídas": saidas,
                    "Pendentes": pendentes,
                    "Lucro Mensal": lucro
                })
            
            tabela_anual = pd.DataFrame(dados_anuais)
            tabela_anual['Entradas'] = tabela_anual['Entradas'].apply(formatar_real)
            tabela_anual['Saídas'] = tabela_anual['Saídas'].apply(formatar_real)
            tabela_anual['Pendentes'] = tabela_anual['Pendentes'].apply(formatar_real)
            tabela_anual['Lucro Mensal'] = tabela_anual['Lucro Mensal'].apply(formatar_real)
            st.dataframe(tabela_anual, use_container_width=True, hide_index=True)
        # --- FIM DA NOVA TABELA ---

	

#==============================================================================================================================================================

with aba5:
    st.subheader("📈 Análise de Gastos por Categoria")

    df = carregar_dados()
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["valor"] = df["valor"].apply(safe_float)
    df["data_pag"] = pd.to_datetime(df["data_pag"], dayfirst=True, errors='coerce')
    df = df.dropna(subset=["data_pag"])
    df["data_pag"] = df["data_pag"].dt.date

    # Filtrar sólo saídas
    df_gastos = df[df["status"] == "saida"]

    if df_gastos.empty:
        st.warning("Não há registros de saída para análise.")
        st.stop()

    # --- Filtro por mês/ano ou todos períodos ---
    data_min = df_gastos["data_pag"].min()
    data_max = df_gastos["data_pag"].max()

    col_mes, col_ano = st.columns(2)
    meses = {
        0: "Todos os períodos...",
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    mes_selecionado = col_mes.selectbox(
    "Mês",
    list(meses.keys()),
    format_func=lambda x: meses[x],
    index=0,
    key="mes_gastos"     # <--- clave única
	)

    ano_atual = date.today().year
    ano_selecionado = col_ano.selectbox(
    "Ano",
    list(range(ano_atual, ano_atual - 6, -1)),
    key="ano_gastos"     # <--- clave única
	)

    if mes_selecionado != 0:
        df_filtrado = df_gastos[
            (df_gastos["data_pag"].map(lambda x: x.year) == ano_selecionado) &
            (df_gastos["data_pag"].map(lambda x: x.month) == mes_selecionado)
        ]
    else:
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data início", data_min, min_value=data_min, max_value=data_max)
        with col2:
            data_fim = st.date_input("Data fim", data_max, min_value=data_min, max_value=data_max)

        df_filtrado = df_gastos[
            (df_gastos["data_pag"] >= data_inicio) &
            (df_gastos["data_pag"] <= data_fim)
        ]

    if df_filtrado.empty:
        st.info("Nenhum gasto encontrado no período selecionado.")
        st.stop()

    # --- Agrupamento por categoria ---
    agrupado = df_filtrado.groupby("categoria")["valor"].sum().sort_values(ascending=False).reset_index()
    total_geral = agrupado["valor"].sum()
    agrupado["percentual"] = ((agrupado["valor"] / total_geral) * 100).round(2)

    st.markdown("### 📊 Percentual por Categoria")
    st.bar_chart(agrupado.set_index("categoria")["valor"])

    st.markdown("### 📋 Tabela detalhada")
    agrupado["valor"] = agrupado["valor"].apply(formatar_real)
    st.dataframe(agrupado, use_container_width=True, hide_index=True)
#==============================================================================================================================================================

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

