import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pdfkit
from jinja2 import Environment, FileSystemLoader, select_autoescape

st.set_page_config(page_title="Laudo Técnico", layout="wide")
st.title("📄 Gerar Laudo Técnico")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'
SHEET_NAME = 'Hoja 1'

credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)
worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
dados = pd.DataFrame(worksheet.get_all_records())

env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
template = env.get_template("template_laudo_final.html")

placa = st.text_input("Digite a placa:", "").strip().upper()

if placa:
    veiculo = dados[dados['placa'].str.upper().str.strip() == placa]
    if not veiculo.empty:
        veiculo_dict = veiculo.iloc[-1].to_dict()
        carro = veiculo_dict.get('carro', '')
        modelo = veiculo_dict.get('modelo', '')
        ano = veiculo_dict.get('ano', '')
        cor = veiculo_dict.get('cor', '')
        dono_empresa = veiculo_dict.get('dono_empresa', '')
        date_in = veiculo_dict.get('date_in', '')
        
        st.success("✅ Veículo encontrado:")
        st.markdown(f"**{carro} {modelo} {ano} - {cor}**")
        st.markdown(f"**Dono:** {dono_empresa} | **Data entrada:** {date_in}")
    else:
        st.warning("❌ Veículo não encontrado.")
        carro = modelo = ano = cor = dono_empresa = date_in = ""
else:
    carro = modelo = ano = cor = dono_empresa = date_in = ""

cidade = st.text_input("Cidade", value="Ponta Grossa")
laudo = st.text_area("Digite o Laudo Técnico:", height=300)

if st.button("Gerar PDF"):
    if not laudo or not placa:
        st.warning("Por favor, preencha todos os campos.")
    else:
        html = template.render(
            placa=placa,
            carro=carro,
            modelo=modelo,
            ano=ano,
            cor=cor,
            dono_empresa=dono_empresa,
            date_in=date_in,
            laudo_conteudo=laudo.replace("\\n", "<br>"),
            cidade=cidade,
            data=datetime.now().strftime("%d/%m/%Y")
        )
        try:
            pdf = pdfkit.from_string(html, False)
            st.download_button(
                "⬇️ Baixar PDF",
                data=pdf,
                file_name=f"Laudo_{placa}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {str(e)}")
