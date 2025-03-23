
import streamlit as st
import pandas as pd
import re
import gspread
from google.oauth2.service_account import Credentials
import datetime
import numpy as np  # Asegúrate de importar numpy para manejar NaN
# Lista de prefijos telefónicos internacionales
import phonenumbers as pn
import pycountry

# ----------------------------------------------------------------------------------------------------------------------------------
# Colocar nome na pagina, icone e ampliar a tela
st.set_page_config(
    page_title="Carros na oficina",
    page_icon=":car",
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
# ----------------------------------------------------------------------------------------------------------------------------------
# Colocar background
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
# ----------------------------------------------------------------------------------------------------------------------------------
# Establecer conexion con Google Sheets
#conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
#existing_data = conn.read(worksheet="Hoja1", usecols=list(range(22)), ttl=5)
#existing_data = existing_data.dropna(how="all")

# df = st.dataframe(existing_data)
#=============================================================================================================================
# Conexion via gspread a traves de https://console.cloud.google.com/ y Google sheets

# Ruta al archivo de credenciales
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]

# Scopes necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales y autorizar
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

# Clave de la hoja de cálculo (la parte de la URL después de "/d/" y antes de "/edit")
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'  # Reemplaza con la clave de tu documento
SHEET_NAME = 'Hoja 1'  # Nombre de la hoja dentro del documento

def cargar_datos():
    try:
        # Intentar obtener la hoja de cálculo
        worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
        
        # Obtener todas las celdas y verificar si hay datos
        all_values = worksheet.get_all_values()
        
        if not all_values or len(all_values) == 0:
            st.warning("La hoja de cálculo está vacía o no contiene registros.")
            return pd.DataFrame(columns=['user_id'])  # Crear un DataFrame vacío con la columna 'user_id'
        else:
            # Cargar los registros en el DataFrame
            records = worksheet.get_all_records()
            if not records:
                st.warning("No hay registros en la hoja de cálculo.")
                return pd.DataFrame(columns=['user_id'])  # Crear un DataFrame vacío
            else:
                existing_data = pd.DataFrame(records)
                #st.write("Datos cargados correctamente:")
                #st.dataframe(existing_data)
                return existing_data

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"No se encontró la hoja de cálculo con la clave '{SPREADSHEET_KEY}'. Asegúrate de que la clave es correcta y que has compartido la hoja con el correo electrónico del cliente de servicio.")
        return pd.DataFrame(columns=['user_id'])  # Crear un DataFrame vacío en caso de error

    except gspread.exceptions.GSpreadException as e:
        st.error(f"Error al obtener los registros: {str(e)}")
        return pd.DataFrame(columns=['user_id'])  # Crear un DataFrame vacío si falla

existing_data = cargar_datos()



#=============================================================================================================================
# Función para obtener el próximo ID disponible
def obtener_proximo_id(df):
    """
    Obtiene el próximo ID disponible en la columna 'user_id'.
    Si el DataFrame está vacío o no tiene la columna 'user_id', retorna 1.
    """
    if df.empty or 'user_id' not in df.columns:
        return 1  # Si no hay datos, el primer ID es 1
    
    # Convertir la columna 'user_id' a numérica, manejando errores
    df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce')
    
    # Reemplazar NaN con 0 (en caso de que haya valores no numéricos)
    df['user_id'] = df['user_id'].fillna(0).astype(int)
    
    # Calcular el máximo ID y sumar 1
    return df['user_id'].max() + 1


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
    

def validar_email(email):
    # Expresión regular para validar direcciones de correo electrónico
    patron_email = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    if re.match(patron_email, email):
        return True
    else:
        return False


def validar_numero_telefono(numero):
    # Define una expresión regular para un número de teléfono
    patron = re.compile(r'^\d{11}$')  # Asumiendo un formato de 10 dígitos, ajusta según tus necesidades
    # Comprueba si el número coincide con el patrón
    if patron.match(numero):
        return True
    else:
        return False

# Función para reemplazar NaN con None
def replace_nan_with_none(df):
    return df.replace({np.nan: None})

def line(size, color):
    st.markdown(
        f"<hr style='height:{size}px;border:none;color:{color};background-color:{color};' />",
        unsafe_allow_html=True
    )
    
# ----------------------------------------------------------------------------------------------------------------------------------
# Constantes
prefijos = {c.alpha_2: pn.country_code_for_region(c.alpha_2) for c in pycountry.countries}

# Función para obtener el prefijo seleccionado
def obtener_prefijo(pais):
    return prefijos.get(pais, '')
# ----------------------------------------------------------------------------------------------------------------------------------
# Titulo de la pagina
centrar_texto("Gestão de Ordens de Serviço", 1, "white")
    
# ----------------------------------------------------------------------------------------------------------------------------------
# Seleccion de la opcion de CRUD
action = st.selectbox(
    "Escolha uma ação",
    [
        "Nova ordem de serviço", # Insert
        "Atualizar ordem existente", # Update
        "Ver todos as ordens de serviço", # View
        "Apagar ordem de serviço", # Delete
    ],
)
# ----------------------------------------------------------------------------------------------------------------------------------
# Formulario

vendor_to_update = None  # Establecer un valor predeterminado

if action == "Nova ordem de serviço":
    st.markdown("Insira os detalhes da nova ordem de serviço")
    with st.form(key="ordem"):
        with st.container():    
            col00, col01, col02, col03, col04 = st.columns(5)
            with col00:
                placa = st.text_input("Placa")
            with col02:
                data_entrada = st.text_input("Data de entrada")
            with col03:
                previsao_entrega = st.text_input("Previsão de entrega")
            with col04:
                data_saida= st.text_input("Data de saida")
            
                
        with st.container():    
            col10, col11, col12, col13, col14 = st.columns(5)
            with col10:
                carro = st.text_input("Marca")
            with col11:
                modelo = st.text_input("Modelo")
            with col12:
                ano = st.text_input("Ano")
            with col13:
                cor = st.text_input("Cor")
            with col14:
                km = st.text_input("Km")

        # Opciones para el desplegable
        opciones_estado = [
            "Entrada",
            "Em orçamento",
            "Aguardando aprovação",
            "Em reparação",
            "Concluido",
            "Entregado"
        ]

        centrar_texto("Dados do carro", 3, "yellow")
        
        with st.container():    
            col20, col21, col22= st.columns(3)
            with col21:
                estado = st.selectbox("Estado do serviço", opciones_estado)

        with st.container():    
            col30, col31, col32 = st.columns(3)
            with col30:
                dono_empresa = st.text_input("Dono / Empresa")
            with col31:
                telefone = st.text_input("Telefone")
            with col32:
                endereco = st.text_input("Endereço")

        line(4, "blue")

        with st.container():    
            col40, col41, col42 = st.columns([1,5,2])
            with col40:
                item_serv_1 = st.text_input("1 - Item")
            with col41:
                desc_ser_1 = st.text_input("1 - Descriçao de serviço")
            with col42:
                valor_serv_1 = st.text_input("1 - Valor do serviço")
                
        with st.container():    
            col50, col51, col52 = st.columns([1,5,2])
            with col50:
                item_serv_2 = st.text_input("2 - Item")
            with col51:
                desc_ser_2 = st.text_input("2 -Descriçao de serviço")
            with col52:
                valor_serv_2 = st.text_input("2- Valor do serviço")

        with st.container():    
            col60, col61, col62 = st.columns([1,5,2])
            with col60:
                item_serv_3 = st.text_input("3 - Item")
            with col61:
                desc_ser_3 = st.text_input("3 -Descriçao de serviço")
            with col62:
                valor_serv_3 = st.text_input("3- Valor do serviço")

        with st.container():    
            col70, col71, col72 = st.columns([1,5,2])
            with col70:
                item_serv_4 = st.text_input("4 - Item")
            with col71:
                desc_ser_4 = st.text_input("4 -Descriçao de serviço")
            with col72:
                valor_serv_4 = st.text_input("4- Valor do serviço")

        with st.container():    
            col80, col81, col82 = st.columns([1,5,2])
            with col80:
                item_serv_5 = st.text_input("5 - Item")
            with col81:
                desc_ser_5 = st.text_input("5 - Descriçao de serviço")
            with col82:
                valor_serv_5 = st.text_input("5 - Valor do serviço")
        
        with st.container():    
            col90, col91, col92 = st.columns([1,5,2])
            with col90:
                item_serv_6 = st.text_input("6 - Item")
            with col91:
                desc_ser_6 = st.text_input("6 - Descriçao de serviço")
            with col92:
                valor_serv_6 = st.text_input("6 - Valor do serviço")
        
        with st.container():    
            col100, col101, col102 = st.columns([1,5,2])
            with col100:
                item_serv_7 = st.text_input("7 - Item")
            with col101:
                desc_ser_7 = st.text_input("7 - Descriçao de serviço")
            with col102:
                valor_serv_7 = st.text_input("7 - Valor do serviço")
        
        with st.container():    
            col110, col111, col112 = st.columns([1,5,2])
            with col110:
                item_serv_8 = st.text_input("8 - Item")
            with col111:
                desc_ser_8 = st.text_input("8 - Descriçao de serviço")
            with col112:
                valor_serv_8 = st.text_input("8 - Valor do serviço")
        
        with st.container():    
            col120, col121, col122 = st.columns([1,5,2])
            with col120:
                item_serv_9 = st.text_input("9 - Item")
            with col121:
                desc_ser_9 = st.text_input("9 - Descriçao de serviço")
            with col122:
                valor_serv_9 = st.text_input("9 - Valor do serviço")
        
        with st.container():    
            col130, col131, col132 = st.columns([1,5,2])
            with col130:
                item_serv_10 = st.text_input("10 - Item")
            with col131:
                desc_ser_10 = st.text_input("10 - Descriçao de serviço")
            with col132:
                valor_serv_10 = st.text_input("10 - Valor do serviço")
        
        with st.container():    
            col140, col141, col142 = st.columns([1,5,2])
            with col140:
                item_serv_11 = st.text_input("11 - Item")
            with col141:
                desc_ser_11 = st.text_input("11 - Descriçao de serviço")
            with col142:
                valor_serv_11 = st.text_input("11 - Valor do serviço")
        
        with st.container():    
            col150, col151, col152 = st.columns([1,5,2])
            with col150:
                item_serv_12 = st.text_input("12 - Item")
            with col151:
                desc_ser_12 = st.text_input("12 - Descriçao de serviço")
            with col152:
                valor_serv_12 = st.text_input("12 - Valor do serviço")
                
        line(4, "blue")

        with st.container():    
            col160, col161, col162 = st.columns([1,5,2])
            with col160:
                quant_peca_1 = st.text_input("1 - Quant.")
            with col161:
                desc_peca_1 = st.text_input("1 - Descriçao da peça")
            with col162:
                valor_peca_1 = st.text_input("1 - Valor de cada peça")

        with st.container():    
            col170, col171, col172 = st.columns([1,5,2])
            with col170:
                quant_peca_2 = st.text_input("2 - Quant.")
            with col171:
                desc_peca_2 = st.text_input("2 - Descriçao da peça")
            with col172:
                valor_peca_2 = st.text_input("2 - Valor de cada peça")

        with st.container():    
            col180, col181, col182 = st.columns([1,5,2])
            with col180:
                quant_peca_3 = st.text_input("3 - Quant.")
            with col181:
                desc_peca_3 = st.text_input("3 - Descriçao da peça")
            with col182:
                valor_peca_3 = st.text_input("3 - Valor de cada peça")
        
        with st.container():    
            col190, col191, col192 = st.columns([1,5,2])
            with col190:
                quant_peca_4 = st.text_input("4 - Quant.")
            with col191:
                desc_peca_4 = st.text_input("4 - Descriçao da peça")
            with col192:
                valor_peca_4 = st.text_input("4 - Valor de cada peça")
        
        with st.container():    
            col200, col201, col202 = st.columns([1,5,2])
            with col200:
                quant_peca_5 = st.text_input("5 - Quant.")
            with col201:
                desc_peca_5 = st.text_input("5 - Descriçao da peça")
            with col202:
                valor_peca_5 = st.text_input("5 - Valor de cada peça")
        
        with st.container():    
            col210, col211, col212 = st.columns([1,5,2])
            with col210:
                quant_peca_6 = st.text_input("6 - Quant.")
            with col211:
                desc_peca_6 = st.text_input("6 - Descriçao da peça")
            with col212:
                valor_peca_6 = st.text_input("6 - Valor de cada peça")
        
        with st.container():    
            col220, col221, col222 = st.columns([1,5,2])
            with col220:
                quant_peca_7 = st.text_input("7 - Quant.")
            with col221:
                desc_peca_7 = st.text_input("7 - Descriçao da peça")
            with col222:
                valor_peca_7 = st.text_input("7 - Valor de cada peça")
        
        with st.container():    
            col230, col231, col232 = st.columns([1,5,2])
            with col230:
                quant_peca_8 = st.text_input("8 - Quant.")
            with col231:
                desc_peca_8 = st.text_input("8 - Descriçao da peça")
            with col232:
                valor_peca_8 = st.text_input("8 - Valor de cada peça")
        
        with st.container():    
            col240, col241, col242 = st.columns([1,5,2])
            with col240:
                quant_peca_9 = st.text_input("9 - Quant.")
            with col241:
                desc_peca_9 = st.text_input("9 - Descriçao da peça")
            with col242:
                valor_peca_9 = st.text_input("9 - Valor de cada peça")
        
        with st.container():    
            col250, col251, col252 = st.columns([1,5,2])
            with col250:
                quant_peca_10 = st.text_input("10 - Quant.")
            with col251:
                desc_peca_10 = st.text_input("10 - Descriçao da peça")
            with col252:
                valor_peca_10 = st.text_input("10 - Valor de cada peça")
        
        with st.container():    
            col260, col261, col262 = st.columns([1,5,2])
            with col260:
                quant_peca_11 = st.text_input("11 - Quant.")
            with col261:
                desc_peca_11 = st.text_input("11 - Descriçao da peça")
            with col262:
                valor_peca_11 = st.text_input("11 - Valor de cada peça")
        
        with st.container():    
            col270, col271, col272 = st.columns([1,5,2])
            with col270:
                quant_peca_12 = st.text_input("12 - Quant.")
            with col271:
                desc_peca_12 = st.text_input("12 - Descriçao da peça")
            with col272:
                valor_peca_12 = st.text_input("12 - Valor de cada peça")
        
        with st.container():    
            col280, col281, col282 = st.columns([1,5,2])
            with col280:
                quant_peca_13 = st.text_input("13 - Quant.")
            with col281:
                desc_peca_13 = st.text_input("13 - Descriçao da peça")
            with col282:
                valor_peca_13 = st.text_input("13 - Valor de cada peça")
        
        with st.container():    
            col290, col291, col292 = st.columns([1,5,2])
            with col290:
                quant_peca_14 = st.text_input("14 - Quant.")
            with col291:
                desc_peca_14 = st.text_input("14 - Descriçao da peça")
            with col292:
                valor_peca_14 = st.text_input("14 - Valor de cada peça")
        
        with st.container():    
            col300, col301, col302 = st.columns([1,5,2])
            with col300:
                quant_peca_15 = st.text_input("15 - Quant.")
            with col301:
                desc_peca_15 = st.text_input("15 - Descriçao da peça")
            with col302:
                valor_peca_15 = st.text_input("15 - Valor de cada peça")
        
        with st.container():    
            col310, col311, col312 = st.columns([1,5,2])
            with col310:
                quant_peca_16 = st.text_input("16 - Quant.")
            with col311:
                desc_peca_16 = st.text_input("16 - Descriçao da peça")
            with col312:
                valor_peca_16 = st.text_input("16 - Valor de cada peça")        
        
        line(4, "blue")

        # Definir el esquema de columnas en el orden correcto
        columnas_ordenadas = [
            'user_id', 'date_in', 'date_prev', 'date_out', 'carro', 'modelo', 'cor', 'placa', 'km', 'ano',
            'estado', 'dono_empresa', 'telefone', 'endereco', 'item_serv_1', 'desc_ser_1', 'valor_serv_1',
            'item_serv_2', 'desc_ser_2', 'valor_serv_2', 'item_serv_3', 'desc_ser_3', 'valor_serv_3',
            'item_serv_4', 'desc_ser_4', 'valor_serv_4', 'item_serv_5', 'desc_ser_5', 'valor_serv_5',
            'item_serv_6', 'desc_ser_6', 'valor_serv_6', 'item_serv_7', 'desc_ser_7', 'valor_serv_7',
            'item_serv_8', 'desc_ser_8', 'valor_serv_8', 'item_serv_9', 'desc_ser_9', 'valor_serv_9',
            'item_serv_10', 'desc_ser_10', 'valor_serv_10', 'item_serv_11', 'desc_ser_11', 'valor_serv_11',
            'item_serv_12', 'desc_ser_12', 'valor_serv_12', 'total_serviço', 
            'quant_peca_1', 'desc_peca_1', 'valor_peca_1', 'valor_total_peca_1', 
            'quant_peca_2', 'desc_peca_2', 'valor_peca_2', 'valor_total_peca_2',
            'quant_peca_3', 'desc_peca_3', 'valor_peca_3', 'valor_total_peca_3',
            'quant_peca_4', 'desc_peca_4', 'valor_peca_4', 'valor_total_peca_4',
            'quant_peca_5', 'desc_peca_5', 'valor_peca_5', 'valor_total_peca_5',
            'quant_peca_6', 'desc_peca_6', 'valor_peca_6', 'valor_total_peca_6',
            'quant_peca_7', 'desc_peca_7', 'valor_peca_7', 'valor_total_peca_7',
            'quant_peca_8', 'desc_peca_8', 'valor_peca_8', 'valor_total_peca_8',
            'quant_peca_9', 'desc_peca_9', 'valor_peca_9', 'valor_total_peca_9',
            'quant_peca_10', 'desc_peca_10', 'valor_peca_10', 'valor_total_peca_10',
            'quant_peca_11', 'desc_peca_11', 'valor_peca_11', 'valor_total_peca_11',
            'quant_peca_12', 'desc_peca_12', 'valor_peca_12', 'valor_total_peca_12',
            'quant_peca_13', 'desc_peca_13', 'valor_peca_13', 'valor_total_peca_13',
            'quant_peca_14', 'desc_peca_14', 'valor_peca_14', 'valor_total_peca_14',
            'quant_peca_15', 'desc_peca_15', 'valor_peca_15', 'valor_total_peca_15',
            'quant_peca_16', 'desc_peca_16', 'valor_peca_16', 'valor_total_peca_16',
            '30_porc', 'total_valor_pecas',
            'forma_de_pagamento', 'pagamento_parcial', 'valor_pago_parcial', 'data_prox_pag', 'valor_prox_pag',
            'pag_total', 'valor_pag_total']
        
        # Asegurar que el DataFrame existente tenga todas las columnas en el orden correcto
        existing_data = existing_data.reindex(columns=columnas_ordenadas)
     
        with st.container():
            col320, col321, col322, col323, col324 = st.columns([1.2, 1.2, 1, 1, 1])
            with col322:
                submit_button = st.form_submit_button("Enviar")
            if submit_button:
                # Crear un nuevo registro con los datos del formulario
                new_record = {
                    'user_id': obtener_proximo_id(existing_data),
                    'date_in': data_entrada,
                    'date_prev': previsao_entrega,
                    'date_out': data_saida,
                    'carro': carro,
                    'modelo': modelo,
                    'cor': cor,
                    'placa': placa,
                    'km': km,
                    'ano': ano,
                    'estado': estado,
                    'dono_empresa': dono_empresa,
                    'telefone': telefone,
                    'endereco': endereco,
                    'item_serv_1': item_serv_1 if 'item_serv_1' in locals() else None,
                    'desc_ser_1': desc_ser_1 if 'desc_ser_1' in locals() else None,
                    'valor_serv_1': valor_serv_1 if 'valor_serv_1' in locals() else None,
                    'item_serv_2': item_serv_2 if 'item_serv_2' in locals() else None,
                    'desc_ser_2': desc_ser_2 if 'desc_ser_2' in locals() else None,
                    'valor_serv_2': valor_serv_2 if 'valor_serv_2' in locals() else None,
                    'item_serv_3': item_serv_3 if 'item_serv_3' in locals() else None,
                    'desc_ser_3': desc_ser_3 if 'desc_ser_3' in locals() else None,
                    'valor_serv_3': valor_serv_3 if 'valor_serv_3' in locals() else None,
                    'item_serv_4': item_serv_4 if 'item_serv_4' in locals() else None,
                    'desc_ser_4': desc_ser_4 if 'desc_ser_4' in locals() else None,
                    'valor_serv_4': valor_serv_4 if 'valor_serv_4' in locals() else None,
                    'item_serv_5': item_serv_5 if 'item_serv_5' in locals() else None,
                    'desc_ser_5': desc_ser_5 if 'desc_ser_5' in locals() else None,
                    'valor_serv_5': valor_serv_5 if 'valor_serv_5' in locals() else None,
                    'item_serv_6': item_serv_6 if 'item_serv_6' in locals() else None,
                    'desc_ser_6': desc_ser_6 if 'desc_ser_6' in locals() else None,
                    'valor_serv_6': valor_serv_6 if 'valor_serv_6' in locals() else None,
                    'item_serv_7': item_serv_7 if 'item_serv_7' in locals() else None,
                    'desc_ser_7': desc_ser_7 if 'desc_ser_7' in locals() else None,
                    'valor_serv_7': valor_serv_7 if 'valor_serv_7' in locals() else None,
                    'item_serv_8': item_serv_8 if 'item_serv_8' in locals() else None,
                    'desc_ser_8': desc_ser_8 if 'desc_ser_8' in locals() else None,
                    'valor_serv_8': valor_serv_8 if 'valor_serv_8' in locals() else None,
                    'item_serv_9': item_serv_9 if 'item_serv_9' in locals() else None,
                    'desc_ser_9': desc_ser_9 if 'desc_ser_9' in locals() else None,
                    'valor_serv_9': valor_serv_9 if 'valor_serv_9' in locals() else None,
                    'item_serv_10': item_serv_10 if 'item_serv_10' in locals() else None,
                    'desc_ser_10': desc_ser_10 if 'desc_ser_10' in locals() else None,
                    'valor_serv_10': valor_serv_10 if 'valor_serv_10' in locals() else None,
                    'item_serv_11': item_serv_11 if 'item_serv_11' in locals() else None,
                    'desc_ser_11': desc_ser_11 if 'desc_ser_11' in locals() else None,
                    'valor_serv_11': valor_serv_11 if 'valor_serv_11' in locals() else None,
                    'item_serv_12': item_serv_12 if 'item_serv_12' in locals() else None,
                    'desc_ser_12': desc_ser_12 if 'desc_ser_12' in locals() else None,
                    'valor_serv_12': valor_serv_12 if 'valor_serv_12' in locals() else None,
                    'total_serviço': None,
                    'quant_peca_1': quant_peca_1 if 'quant_peca_1' in locals() else None,
                    'desc_peca_1': desc_peca_1 if 'desc_peca_1' in locals() else None,
                    'valor_peca_1': valor_peca_1 if 'valor_peca_1' in locals() else None,
                    'valor_total_peca_1': valor_total_peca_1 if 'valor_total_peca_1' in locals() else None,
                    'quant_peca_2': quant_peca_2 if 'quant_peca_2' in locals() else None,
                    'desc_peca_2': desc_peca_2 if 'desc_peca_2' in locals() else None,
                    'valor_peca_2': valor_peca_2 if 'valor_peca_2' in locals() else None,
                    'valor_total_peça_2': valor_total_peça_2 if 'valor_total_peça_2' in locals() else None,
                    'quant_peca_3': quant_peca_3 if 'quant_peca_3' in locals() else None,
                    'desc_peca_3': desc_peca_3 if 'desc_peca_3' in locals() else None,
                    'valor_peca_3': valor_peca_3 if 'valor_peca_3' in locals() else None,
                    'valor_total_peça_3': valor_total_peça_3 if 'valor_total_peça_3' in locals() else None,
                    'quant_peca_4': quant_peca_4 if 'quant_peca_4' in locals() else None,
                    'desc_peca_4': desc_peca_4 if 'desc_peca_4' in locals() else None,
                    'valor_peca_4': valor_peca_4 if 'valor_peca_4' in locals() else None,
                    'valor_total_peça_4': valor_total_peça_4 if 'valor_total_peça_4' in locals() else None,
                    'quant_peca_5': quant_peca_5 if 'quant_peca_5' in locals() else None,
                    'desc_peca_5': desc_peca_5 if 'desc_peca_5' in locals() else None,
                    'valor_peca_5': valor_peca_5 if 'valor_peca_5' in locals() else None,
                    'valor_total_peça_5': valor_total_peça_5 if 'valor_total_peça_5' in locals() else None,
                    'quant_peca_6': quant_peca_6 if 'quant_peca_6' in locals() else None,
                    'desc_peca_6': desc_peca_6 if 'desc_peca_6' in locals() else None,
                    'valor_peca_6': valor_peca_6 if 'valor_peca_6' in locals() else None,
                    'valor_total_peça_6': valor_total_peça_6 if 'valor_total_peça_6' in locals() else None,
                    'quant_peca_7': quant_peca_7 if 'quant_peca_7' in locals() else None,
                    'desc_peca_7': desc_peca_7 if 'desc_peca_7' in locals() else None,
                    'valor_peca_7': valor_peca_7 if 'valor_peca_7' in locals() else None,
                    'valor_total_peça_7': valor_total_peça_7 if 'valor_total_peça_7' in locals() else None,
                    'quant_peca_8': quant_peca_8 if 'quant_peca_8' in locals() else None,
                    'desc_peca_8': desc_peca_8 if 'desc_peca_8' in locals() else None,
                    'valor_peca_8': valor_peca_8 if 'valor_peca_8' in locals() else None,
                    'valor_total_peça_8': valor_total_peça_8 if 'valor_total_peça_8' in locals() else None,
                    'quant_peca_9': quant_peca_9 if 'quant_peca_9' in locals() else None,
                    'desc_peca_9': desc_peca_9 if 'desc_peca_9' in locals() else None,
                    'valor_peca_9': valor_peca_9 if 'valor_peca_9' in locals() else None,
                    'valor_total_peça_9': valor_total_peça_9 if 'valor_total_peça_9' in locals() else None,
                    'quant_peca_10': quant_peca_10 if 'quant_peca_10' in locals() else None,
                    'desc_peca_10': desc_peca_10 if 'desc_peca_10' in locals() else None,
                    'valor_peca_10': valor_peca_10 if 'valor_peca_10' in locals() else None,
                    'valor_total_peça_10': valor_total_peça_10 if 'valor_total_peça_10' in locals() else None,
                    'quant_peca_11': quant_peca_11 if 'quant_peca_11' in locals() else None,
                    'desc_peca_11': desc_peca_11 if 'desc_peca_11' in locals() else None,
                    'valor_peca_11': valor_peca_11 if 'valor_peca_11' in locals() else None,
                    'valor_total_peça_11': valor_total_peça_11 if 'valor_total_peça_11' in locals() else None,
                    'quant_peca_12': quant_peca_12 if 'quant_peca_12' in locals() else None,
                    'desc_peca_12': desc_peca_12 if 'desc_peca_12' in locals() else None,
                    'valor_peca_12': valor_peca_12 if 'valor_peca_12' in locals() else None,
                    'valor_total_peça_12': valor_total_peça_12 if 'valor_total_peça_12' in locals() else None,
                    'quant_peca_13': quant_peca_13 if 'quant_peca_13' in locals() else None,
                    'desc_peca_13': desc_peca_13 if 'desc_peca_13' in locals() else None,
                    'valor_peca_13': valor_peca_13 if 'valor_peca_13' in locals() else None,
                    'valor_total_peça_13': valor_total_peça_13 if 'valor_total_peça_13' in locals() else None,
                    'quant_peca_14': quant_peca_14 if 'quant_peca_14' in locals() else None,
                    'desc_peca_14': desc_peca_14 if 'desc_peca_14' in locals() else None,
                    'valor_peca_14': valor_peca_14 if 'valor_peca_14' in locals() else None,
                    'valor_total_peça_14': valor_total_peça_14 if 'valor_total_peça_14' in locals() else None,
                    'quant_peca_15': quant_peca_15 if 'quant_peca_15' in locals() else None,
                    'desc_peca_15': desc_peca_15 if 'desc_peca_15' in locals() else None,
                    'valor_peca_15': valor_peca_15 if 'valor_peca_15' in locals() else None,
                    'valor_total_peça_15': valor_total_peça_15 if 'valor_total_peça_15' in locals() else None,
                    'quant_peca_16': quant_peca_16 if 'quant_peca_16' in locals() else None,
                    'desc_peca_16': desc_peca_16 if 'desc_peca_16' in locals() else None,
                    'valor_peca_16': valor_peca_16 if 'valor_peca_16' in locals() else None,
                    'valor_total_peça_16': valor_total_peça_16 if 'valor_total_peça_16' in locals() else None,
                    '30_porc': None,
                    'total_valor_pecas': None,
                    'forma_de_pagamento': None,
                    'pagamento_parcial': None,
                    'valor_pago_parcial': None,
                    'data_prox_pag': None,
                    'valor_prox_pag': None,
                    'pag_total': None,
                    'valor_pag_total': None
                }
            
                # Convertir el nuevo registro a DataFrame
                new_record_df = pd.DataFrame([new_record])
            
                # Asegurar que el nuevo registro tenga todas las columnas en el orden correcto
                new_record_df = new_record_df.reindex(columns=columnas_ordenadas)
            
                # Reemplazar NaN con None en el nuevo registro
                new_record_df = replace_nan_with_none(new_record_df)
            
                try:
                    # Obtener la hoja de cálculo
                    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
                    
                    # Agregar el nuevo registro al final de la hoja
                    worksheet.append_row(new_record_df.values.tolist()[0])
                    
                    st.success("Ordem de serviço adicionada com sucesso")
                    
                    # Actualizar la variable existing_data con los datos actualizados
                    existing_data = pd.concat([existing_data, new_record_df], ignore_index=True)
            
                except Exception as e:
                    st.error(f"Erro ao atualizar planilha: {str(e)}")
            
            # Mostrar la tabla actualizada
            st.dataframe(existing_data, hide_index=True)

# ____________________________________________________________________________________________________________________________________
