import streamlit as st
import pandas as pd
import webbrowser
from datetime import datetime

# Colocar nome na pagina, icone e ampliar a tela
st.set_page_config(
    page_title="Contact",
    page_icon=":house",
    layout="wide"
)

# We reduced the empty space at the beginning of the streamlit
reduce_space ="""
            <style type="text/css">
            /* Remueve el espacio en el encabezado por defecto de las apps de Streamlit */
            div[data-testid="stAppViewBlockContainer"]{
                padding-top:30px;
            }
            </style>
            """
# We load reduce_space
st.html(reduce_space)

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://i.postimg.cc/jdtSsJ9t/jr-korpa-H-BJWTh-ZRok-unsplash.jpg");
background-size: 180%;
background-position: top left;
background-repeat: repeat;
background-attachment: local;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}

[data-testid="stSidebar"] {{
background: rgba(0,0,0,0);
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


def centrar_imagen(imagen, ancho):
    # Aplicar estilo CSS para centrar la imagen con Markdown
    st.markdown(
        f'<div style="display: flex; justify-content: center;">'
        f'<img src="{imagen}" width="{ancho}">'
        f'</div>',
        unsafe_allow_html=True
    )

def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>",
                unsafe_allow_html=True)

def photo_link(alt_text, img_url, link_url, img_width):
    markdown_code = f'<a href="{link_url}" target="_blank"><img src="{img_url}" alt="{alt_text}" width="{img_width}"></a>'
    st.markdown(markdown_code, unsafe_allow_html=True)
    

with st.container():    
    col00, col01, col02, col03, col04, col05 = st.columns(6)
    with col02:
        photo_link("Facebook", "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/2023_Facebook_icon.svg/50px-2023_Facebook_icon.svg.png", "https://www.facebook.com/guillermo.cerato", "50px")
    with col03:
        centrar_texto("Facebook", 4, "white")
        
with st.container():    
    col10, col11, col12, col13, col14, col15 = st.columns(6)
    with col12:
        photo_link("Instagram", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Instagram_logo_2022.svg/150px-Instagram_logo_2022.svg.png", "https://www.instagram.com/willycerato", "50px")
    with col13:
        centrar_texto("Instagram", 4, "white")

with st.container():    
    col20, col21, col22, col23, col24, col25 = st.columns(6)
    with col22:
        photo_link("Linkedin", "https://img.freepik.com/vetores-premium/logotipo-quadrado-do-linkedin-isolado-no-fundo-branco_469489-892.jpg", "https://www.linkedin.com/in/willycerato", "50px")
    with col23:
        centrar_texto("Linkedin", 4, "white")
        
with st.container():    
    col30, col31, col32, col33, col34, col35 = st.columns(6)
    with col32:
        photo_link("Whatsapp", "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/120px-WhatsApp.svg.png", "https://wa.me/5542991657847", "50px")
    with col33:
        centrar_texto("Whatsapp", 4, "white")

with st.container():    
    col40, col41, col42, col43, col44, col45 = st.columns(6)
    with col42:
        photo_link("Kaggle", "https://cdn4.iconfinder.com/data/icons/logos-and-brands/512/189_Kaggle_logo_logos-512.png", "https://www.kaggle.com/willycerato", "50px")
    with col43:
        centrar_texto("Kaggle", 4, "white")

with st.container():    
    col50, col51, col52, col53, col54, col55 = st.columns(6)
    with col52:
        photo_link("Github", "https://cdn.pixabay.com/photo/2022/01/30/13/33/github-6980894_1280.png", "https://github.com/Willy71", "50px")
    with col53:
        centrar_texto("GitHub", 4, "white")

