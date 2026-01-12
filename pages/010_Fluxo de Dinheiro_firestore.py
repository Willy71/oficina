import streamlit as st
import pandas as pd
from firebase_config import db
import uuid
from datetime import datetime, date
from calendar import monthrange
import calendar

# Conexão com Google Sheets

client = gspread.authorize(credentials)

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
        # si tiene solo punto, ya está ok

        return float(str_valor)
    except Exception as e:
        print(f"Error convertiendo valor: '{valor}'. Error: {e}")
        return 0.0


# En la función cargar_dados():

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
        df["data_pag"] = pd.to_datetime(df["data_pag"], dayfirst=True, errors="coerce")
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    if "valor" in df.columns:
        df["valor"] = df["valor"].apply(safe_float)
    return df
        st.info("Digite um termo para buscar nos registros.")
