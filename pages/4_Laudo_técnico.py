import streamlit as st
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import pdfkit

# Config
st.set_page_config(page_title="Gerar Laudo Técnico", layout="wide")

# Inicializar Jinja2
env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
template = env.get_template("template_laudo.html")

# Interfaz
st.title("📝 Gerar Laudo Técnico")

placa = st.text_input("Placa do veículo")
cidade = st.text_input("Cidade", value="Ponta Grossa")
laudo = st.text_area("Digite o conteúdo do laudo técnico:", height=300)

if st.button("Gerar PDF"):
    if not laudo or not placa:
        st.warning("Preencha todos os campos obrigatórios.")
    else:
        data_atual = datetime.now().strftime("%d/%m/%Y")
        html = template.render(
            laudo_conteudo=laudo.replace("\n", "<br>"),
            cidade=cidade,
            data=data_atual
        )
        try:
            pdf = pdfkit.from_string(html, False)
            st.success("PDF gerado com sucesso!")
            st.download_button(
                "⬇️ Baixar Laudo PDF",
                data=pdf,
                file_name=f"Laudo_{placa}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {str(e)}")
