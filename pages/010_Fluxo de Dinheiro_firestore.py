import streamlit as st
import pandas as pd
from datetime import datetime, date
from firebase_config import db
from firebase_admin import firestore

st.set_page_config(page_title="Fluxo de Dinheiro", layout="wide")

# -----------------------------
# Utilidades
# -----------------------------

def parse_valor(valor):
    if valor is None:
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    try:
        s = str(valor).strip()
        s = s.replace("R$", "").replace("$", "").strip()

        if not s:
            return 0.0

        if "." in s and "," in s:
            if s.find(".") < s.find(","):
                s = s.replace(".", "").replace(",", ".")
            else:
                s = s.replace(",", "")
        elif "," in s:
            s = s.replace(",", ".")

        return float(s)
    except:
        return 0.0


def get_next_id():
    docs = (
        db.collection("fluxo")
        .order_by("ids", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    )
    for doc in docs:
        return int(doc.to_dict().get("ids", 0)) + 1
    return 1


def carregar_dados():
    registros = []
    for doc in db.collection("fluxo").stream():
        d = doc.to_dict()
        d["doc_id"] = doc.id
        registros.append(d)

    if not registros:
        return pd.DataFrame()

    df = pd.DataFrame(registros)

    for col in ["data", "data_pag"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "valor" in df.columns:
        df["valor"] = df["valor"].apply(parse_valor)

    return df.sort_values("ids", ascending=False)


# -----------------------------
# UI
# -----------------------------

st.title("📊 Fluxo de Dinheiro (Firestore)")

aba = st.sidebar.radio("Menu", ["➕ Novo Registro", "📋 Listar / Editar", "🔍 Buscar"])

df = carregar_dados()

# -----------------------------
# NOVO REGISTRO
# -----------------------------
if aba == "➕ Novo Registro":
    st.subheader("Novo Registro")

    col1, col2, col3 = st.columns(3)
    with col1:
        data = st.date_input("Data", value=date.today())
        cliente = st.text_input("Cliente")
        carro = st.text_input("Carro")
        placa = st.text_input("Placa")

    with col2:
        descricao = st.text_input("Descrição")
        categoria = st.text_input("Categoria")
        motivo = st.text_input("Motivo")

    with col3:
        forma = st.text_input("Forma de pagamento")
        valor = st.text_input("Valor", "0")
        status = st.selectbox("Status", ["pendente", "pago"])

    if st.button("Salvar"):
        novo_id = get_next_id()
        registro = {
            "ids": novo_id,
            "data": str(data),
            "data_pag": "",
            "cliente": cliente,
            "descricao": descricao,
            "categoria": categoria,
            "carro": carro,
            "placa": placa,
            "motivo": motivo,
            "form": forma,
            "valor": parse_valor(valor),
            "status": status,
        }

        db.collection("fluxo").add(registro)
        st.success(f"Registro #{novo_id} criado com sucesso.")
        st.rerun()

# -----------------------------
# LISTAR / EDITAR
# -----------------------------
elif aba == "📋 Listar / Editar":
    st.subheader("Registros")

    if df.empty:
        st.info("Nenhum registro encontrado.")
    else:
        selecionado = st.selectbox(
            "Seleccione un registro por ID",
            df["ids"].tolist()
        )

        linha = df[df["ids"] == selecionado].iloc[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            data = st.date_input("Data", value=linha["data"].date() if pd.notna(linha["data"]) else date.today())
            cliente = st.text_input("Cliente", linha.get("cliente", ""))
            carro = st.text_input("Carro", linha.get("carro", ""))
            placa = st.text_input("Placa", linha.get("placa", ""))

        with col2:
            descricao = st.text_input("Descrição", linha.get("descricao", ""))
            categoria = st.text_input("Categoria", linha.get("categoria", ""))
            motivo = st.text_input("Motivo", linha.get("motivo", ""))

        with col3:
            forma = st.text_input("Forma", linha.get("form", ""))
            valor = st.text_input("Valor", str(linha.get("valor", 0)))
            status = st.selectbox("Status", ["pendente", "pago"], index=0 if linha.get("status") == "pendente" else 1)

        if st.button("Actualizar"):
            update = {
                "data": str(data),
                "cliente": cliente,
                "carro": carro,
                "placa": placa,
                "descricao": descricao,
                "categoria": categoria,
                "motivo": motivo,
                "form": forma,
                "valor": parse_valor(valor),
                "status": status,
            }

            db.collection("fluxo").document(linha["doc_id"]).update(update)
            st.success("Registro actualizado.")
            st.rerun()

        if st.button("Eliminar"):
            db.collection("fluxo").document(linha["doc_id"]).delete()
            st.warning("Registro eliminado.")
            st.rerun()

# -----------------------------
# BUSCAR
# -----------------------------
elif aba == "🔍 Buscar":
    st.subheader("Buscar")

    termo = st.text_input("Buscar por cliente, placa, descrição o motivo").lower()

    if termo and not df.empty:
        filtro = (
            df["placa"].astype(str).str.lower().str.contains(termo) |
            df["descricao"].astype(str).str.lower().str.contains(termo) |
            df["cliente"].astype(str).str.lower().str.contains(termo) |
            df["motivo"].astype(str).str.lower().str.contains(termo)
        )
        resultados = df[filtro].sort_values("ids", ascending=False)

        if resultados.empty:
            st.info("Nenhum resultado encontrado.")
        else:
            st.dataframe(resultados.drop(columns=["doc_id"]), use_container_width=True)
    else:
        st.info("Digite um termo para buscar.")
