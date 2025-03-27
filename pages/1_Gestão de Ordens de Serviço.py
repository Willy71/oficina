
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

# Scopes necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Ruta al archivo de credenciales
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]

# Clave de la hoja de cálculo (la parte de la URL después de "/d/" y antes de "/edit")
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'  # Reemplaza con la clave de tu documento
SHEET_NAME = 'Hoja 1'  # Nombre de la hoja dentro del documento

# Cargar credenciales y autorizar
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

def inicializar_hoja():
    try:
        # Abrir la hoja de cálculo
        spreadsheet = gc.open_by_key(SPREADSHEET_KEY)
        
        # Intentar abrir la hoja específica
        try:
            worksheet = spreadsheet.worksheet(SHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            # Si la hoja no existe, crearla
            worksheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=100, cols=50)
            # Agregar los encabezados de las columnas
            worksheet.append_row(columnas_ordenadas)  # Asegúrate de definir `columnas_ordenadas`
        
        return worksheet
    except Exception as e:
        st.error(f"Erro ao acessar planilha: {str(e)}")
        return None

# Definir las columnas en el orden correcto
# Definir el esquema de columnas en el orden correcto
columnas_ordenadas = ['user_id', 'date_in', 'date_prev', 'date_out', 'carro', 'modelo', 'cor', 'placa', 'km', 'ano', 
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
                      '30_porc', 'total_valor_pecas', 'forma_de_pagamento', 'pagamento_parcial', 
                      'valor_pago_parcial', 'data_prox_pag', 'valor_prox_pag', 'pag_total', 'valor_pag_total'
                     ]

# Función para cargar datos desde Google Sheets
def cargar_datos(worksheet):
    try:
        records = worksheet.get_all_records()
        if not records:
            # Si no hay registros, crear un DataFrame vacío con las columnas necesarias
            return pd.DataFrame(columns=columnas_ordenadas)
        else:
            # Convertir los registros a DataFrame
            df = pd.DataFrame(records)
            # Asegurarse de que la columna 'user_id' sea numérica
            df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce').fillna(0).astype(int)
            return df
    except Exception as e:
        st.error(f"Erro ao cargar dados: {str(e)}")
        return pd.DataFrame(columns=columnas_ordenadas)


# Inicializar la hoja de cálculo
worksheet = inicializar_hoja()

# Cargar datos desde Google Sheets
existing_data = cargar_datos(worksheet)

#=============================================================================================================================
def obtener_proximo_id(df):
    if df.empty or 'user_id' not in df.columns:
        return 1
        
    try:
        # Filtramos solo IDs numéricos válidos
        valid_ids = pd.to_numeric(df['user_id'], errors='coerce').dropna()
        if valid_ids.empty:
            return 1
        return int(valid_ids.max()) + 1
    except Exception:
        return 1

def atualizar_ordem(vendor_to_update, updated_record):
    try:
        # 1. Conexión a la hoja
        worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
        
        # 2. Encontrar la fila EXACTA del registro
        cell = worksheet.find(str(int(vendor_to_update)))
        row_num = cell.row
        
        # 3. Preparar valores actualizados (en orden de columnas)
        new_values = []
        for col in columnas_ordenadas:
            if col in updated_record.columns:
                new_values.append(updated_record[col].values[0])
            else:
                # Mantener valor existente si no se está actualizando
                existing_value = worksheet.cell(row_num, columnas_ordenadas.index(col)+1).value
                new_values.append(existing_value)
        
        # 4. Actualizar SOLO ESA FILA (¡sin borrar nada más!)
        worksheet.update(
            f"A{row_num}",
            [new_values],
            value_input_option="USER_ENTERED"
        )
        
        # 5. Actualizar el DataFrame local
        for col in updated_record.columns:
            existing_data.loc[existing_data["user_id"] == vendor_to_update, col] = updated_record[col].values[0]
        
        st.success("✅ Registro atualizado sem reorganizar a planilha!")
        return True
        
    except Exception as e:
        st.error(f"Erro direto: {str(e)}")
        return False

#==============================================================================================================================================================


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
    #st.markdown("Insira os detalhes da nova ordem de serviço")
    with st.form(key="ordem"):
        centrar_texto("Dados do carro", 2, "yellow")
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
        centrar_texto("Serviços", 2, "yellow")

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
        centrar_texto("Peças", 2, "yellow")

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

elif action == "Atualizar ordem existente":
    st.header("🔧 Atualizar Ordem Existente")
    
    # 1. Selección del registro a actualizar (versión mejorada)
    search_col, display_col = st.columns(2)
    
    with search_col:
        search_by = st.radio("Buscar por:", ["ID", "Placa"], horizontal=True)
        
        if search_by == "ID":
            selected_id = st.selectbox(
                "Selecione o ID:", 
                options=sorted(existing_data["user_id"].dropna().astype(int).unique())
            )
            record_to_update = existing_data[existing_data["user_id"] == selected_id].iloc[0]
        else:
            selected_placa = st.selectbox(
                "Selecione a Placa:", 
                options=sorted(existing_data["placa"].dropna().unique())
            )
            # Tomar el registro más reciente para esa placa
            record_to_update = existing_data[existing_data["placa"] == selected_placa] \
                             .sort_values("date_in", ascending=False) \
                             .iloc[0]
            selected_id = record_to_update["user_id"]
    
    with display_col:
        st.markdown(f"**Editando Ordem N°:** `{int(selected_id)}`")
        st.markdown(f"**Placa:** `{record_to_update['placa']}`")
        st.markdown(f"**Data de Entrada:** `{record_to_update['date_in']}`")


    # Mostrar el formulario con los datos actuales
    with st.form(key="update_form"):
        st.markdown("Atualize os detalhes da ordem de serviço")
        
        # Mostrar el ID como texto (no editable)
        st.text_input("ID da Ordem", value=vendor_to_update, disabled=True, key="display_user_id")
        
        # Resto del formulario (igual que antes)
        with st.container():    
            col00, col01, col02, col03, col04 = st.columns(5)
            with col00:
                placa = st.text_input("Placa", value=record_to_update["placa"], key="update_placa")
            with col02:
                data_entrada = st.text_input("Data de entrada", value=record_to_update["date_in"], key="update_data_entrada")
            with col03:
                previsao_entrega = st.text_input("Previsão de entrega", value=record_to_update["date_prev"], key="update_previsao_entrega")
            with col04:
                data_saida = st.text_input("Data de saida", value=record_to_update["date_out"], key="update_data_saida")
            
        with st.container():    
            col10, col11, col12, col13, col14 = st.columns(5)
            with col10:
                carro = st.text_input("Marca", value=record_to_update["carro"], key="update_carro")
            with col11:
                modelo = st.text_input("Modelo", value=record_to_update["modelo"], key="update_modelo")
            with col12:
                ano = st.text_input("Ano", value=record_to_update["ano"], key="update_ano")
            with col13:
                cor = st.text_input("Cor", value=record_to_update["cor"], key="update_cor")
            with col14:
                km = st.text_input("Km", value=record_to_update["km"], key="update_km")

        # Opciones para el desplegable
        opciones_estado = [
            "Entrada",
            "Em orçamento",
            "Aguardando aprovação",
            "Em reparação",
            "Concluido",
            "Entregado"
        ]
        with st.container():    
            col20, col21, col22 = st.columns(3)
            with col21:
                # Verificar si el estado actual está en opciones_estado
                estado_actual = vendor_data["estado"]
                if estado_actual in opciones_estado:
                    index_estado = opciones_estado.index(estado_actual)
                else:
                    index_estado = 0  # Usar el primer valor de opciones_estado como predeterminado
        
        estado = st.selectbox("Estado do serviço", opciones_estado, index=index_estado, key="update_estado")

        with st.container():    
            col30, col31, col32 = st.columns(3)
            with col30:
                dono_empresa = st.text_input("Dono / Empresa", value=record_to_update["dono_empresa"], key="update_dono_empresa")
            with col31:
                telefone = st.text_input("Telefone", value=record_to_update["telefone"], key="update_telefone")
            with col32:
                endereco = st.text_input("Endereço", value=record_to_update["endereco"], key="update_endereco")

        line(4, "blue")
        centrar_texto("Serviços", 2, "yellow")

        with st.container():    
            col40, col41, col42 = st.columns([1,5,2])
            with col40:
                item_serv_1 = st.text_input("1 - Item",  value=record_to_update["item_serv_1"], key="update_item_serv_1")
            with col41:
                desc_ser_1 = st.text_input("1 - Descriçao de serviço",  value=record_to_update["desc_ser_1"], key="update_desc_ser_1")
            with col42:
                valor_serv_1 = st.text_input("1 - Valor do serviço",  value=record_to_update["valor_serv_1"], key="update_valor_serv_1")
                
        with st.container():    
            col50, col51, col52 = st.columns([1,5,2])
            with col50:
                item_serv_2 = st.text_input("2 - Item",  value=record_to_update["item_serv_2"], key="update_item_serv_2")
            with col51:
                desc_ser_2 = st.text_input("2 -Descriçao de serviço",  value=record_to_update["desc_ser_2"], key="update_desc_ser_2")
            with col52:
                valor_serv_2 = st.text_input("2- Valor do serviço",  value=record_to_update["valor_serv_2"], key="update_valor_serv_2")

        with st.container():    
            col60, col61, col62 = st.columns([1,5,2])
            with col60:
                item_serv_3 = st.text_input("3 - Item",  value=record_to_update["item_serv_3"], key="update_item_serv_3")
            with col61:
                desc_ser_3 = st.text_input("3 -Descriçao de serviço",  value=record_to_update["desc_ser_3"], key="update_desc_ser_3")
            with col62:
                valor_serv_3 = st.text_input("3- Valor do serviço",  value=record_to_update["valor_serv_3"], key="update_valor_serv_3")

        with st.container():    
            col70, col71, col72 = st.columns([1,5,2])
            with col70:
                item_serv_4 = st.text_input("4 - Item",  value=record_to_update["item_serv_4"], key="update_item_serv_4")
            with col71:
                desc_ser_4 = st.text_input("4 -Descriçao de serviço",  value=record_to_update["desc_ser_4"], key="update_desc_ser_4")
            with col72:
                valor_serv_4 = st.text_input("4- Valor do serviço", value=record_to_update["valor_serv_4"], key="update_valor_serv_4")

        with st.container():    
            col80, col81, col82 = st.columns([1,5,2])
            with col80:
                item_serv_5 = st.text_input("5 - Item", value=record_to_update["item_serv_5"], key="update_item_serv_5")
            with col81:
                desc_ser_5 = st.text_input("5 - Descriçao de serviço", value=record_to_update["desc_ser_5"], key="update_desc_ser_5")
            with col82:
                valor_serv_5 = st.text_input("5 - Valor do serviço", value=record_to_update["valor_serv_5"], key="update_valor_serv_5")
        
        with st.container():    
            col90, col91, col92 = st.columns([1,5,2])
            with col90:
                item_serv_6 = st.text_input("6 - Item", value=record_to_update["item_serv_6"], key="update_item_serv_6")
            with col91:
                desc_ser_6 = st.text_input("6 - Descriçao de serviço", value=record_to_update["desc_ser_6"], key="update_desc_ser_6")
            with col92:
                valor_serv_6 = st.text_input("6 - Valor do serviço", value=record_to_update["valor_serv_6"], key="update_valor_serv_6")
        
        with st.container():    
            col100, col101, col102 = st.columns([1,5,2])
            with col100:
                item_serv_7 = st.text_input("7 - Item", value=record_to_update["item_serv_7"], key="update_item_serv_7")
            with col101:
                desc_ser_7 = st.text_input("7 - Descriçao de serviço", value=record_to_update["desc_ser_7"], key="update_desc_ser_7")
            with col102:
                valor_serv_7 = st.text_input("7 - Valor do serviço", value=record_to_update["valor_serv_7"], key="update_valor_serv_7")
        
        with st.container():    
            col110, col111, col112 = st.columns([1,5,2])
            with col110:
                item_serv_8 = st.text_input("8 - Item", value=record_to_update["item_serv_8"], key="update_item_serv_8")
            with col111:
                desc_ser_8 = st.text_input("8 - Descriçao de serviço", value=record_to_update["desc_ser_8"], key="update_desc_ser_8")
            with col112:
                valor_serv_8 = st.text_input("8 - Valor do serviço", value=record_to_update["valor_serv_8"], key="update_valor_serv_8")
        
        with st.container():    
            col120, col121, col122 = st.columns([1,5,2])
            with col120:
                item_serv_9 = st.text_input("9 - Item", value=record_to_update["item_serv_9"], key="update_item_serv_9")
            with col121:
                desc_ser_9 = st.text_input("9 - Descriçao de serviço", value=record_to_update["desc_ser_9"], key="update_desc_ser_9")
            with col122:
                valor_serv_9 = st.text_input("9 - Valor do serviço", value=record_to_update["valor_serv_9"], key="update_valor_serv_9")
        
        with st.container():    
            col130, col131, col132 = st.columns([1,5,2])
            with col130:
                item_serv_10 = st.text_input("10 - Item", value=record_to_update["item_serv_10"], key="update_item_serv_10")
            with col131:
                desc_ser_10 = st.text_input("10 - Descriçao de serviço", value=record_to_update["desc_ser_10"], key="update_desc_ser_10")
            with col132:
                valor_serv_10 = st.text_input("10 - Valor do serviço", value=record_to_update["valor_serv_10"], key="update_valor_serv_10")
        
        with st.container():    
            col140, col141, col142 = st.columns([1,5,2])
            with col140:
                item_serv_11 = st.text_input("11 - Item", value=record_to_update["item_serv_11"], key="update_item_serv_11")
            with col141:
                desc_ser_11 = st.text_input("11 - Descriçao de serviço", value=record_to_update["desc_ser_11"], key="update_desc_ser_11")
            with col142:
                valor_serv_11 = st.text_input("11 - Valor do serviço", value=record_to_update["valor_serv_11"], key="update_valor_serv_11")
        
        with st.container():    
            col150, col151, col152 = st.columns([1,5,2])
            with col150:
                item_serv_12 = st.text_input("12 - Item", value=record_to_update["item_serv_12"], key="update_item_serv_12")
            with col151:
                desc_ser_12 = st.text_input("12 - Descriçao de serviço", value=record_to_update["desc_ser_12"], key="update_desc_ser_12")
            with col152:
                valor_serv_12 = st.text_input("12 - Valor do serviço", value=record_to_update["valor_serv_12"], key="update_valor_serv_12")
                
        line(4, "blue")
        centrar_texto("Peças", 2, "yellow")

        with st.container():    
            col160, col161, col162 = st.columns([1,5,2])
            with col160:
                quant_peca_1 = st.text_input("1 - Quant.", value=record_to_update["quant_peca_1"], key="update_quant_peca_1")
            with col161:
                desc_peca_1 = st.text_input("1 - Descriçao da peça", value=record_to_update["desc_peca_1"], key="update_desc_peca_1")
            with col162:
                valor_peca_1 = st.text_input("1 - Valor de cada peça", value=record_to_update["valor_peca_1"], key="update_valor_peca_1")

        with st.container():    
            col170, col171, col172 = st.columns([1,5,2])
            with col170:
                quant_peca_2 = st.text_input("2 - Quant.", value=record_to_update["quant_peca_2"], key="update_quant_peca_2")
            with col171:
                desc_peca_2 = st.text_input("2 - Descriçao da peça", value=record_to_update["desc_peca_2"], key="update_desc_peca_2")
            with col172:
                valor_peca_2 = st.text_input("2 - Valor de cada peça", value=record_to_update["valor_peca_2"], key="update_valor_peca_2")

        with st.container():    
            col180, col181, col182 = st.columns([1,5,2])
            with col180:
                quant_peca_3 = st.text_input("3 - Quant.", value=record_to_update["quant_peca_3"], key="update_quant_peca_3")
            with col181:
                desc_peca_3 = st.text_input("3 - Descriçao da peça", value=record_to_update["desc_peca_3"], key="update_desc_peca_3")
            with col182:
                valor_peca_3 = st.text_input("3 - Valor de cada peça", value=record_to_update["valor_peca_3"], key="update_valor_peca_3")
        
        with st.container():    
            col190, col191, col192 = st.columns([1,5,2])
            with col190:
                quant_peca_4 = st.text_input("4 - Quant.", value=record_to_update["quant_peca_4"], key="update_quant_peca_4")
            with col191:
                desc_peca_4 = st.text_input("4 - Descriçao da peça", value=record_to_update["desc_peca_4"], key="update_desc_peca_4")
            with col192:
                valor_peca_4 = st.text_input("4 - Valor de cada peça", value=record_to_update["valor_peca_4"], key="update_valor_peca_4")
        
        with st.container():    
            col200, col201, col202 = st.columns([1,5,2])
            with col200:
                quant_peca_5 = st.text_input("5 - Quant.", value=record_to_update["quant_peca_5"], key="update_quant_peca_5")
            with col201:
                desc_peca_5 = st.text_input("5 - Descriçao da peça", value=record_to_update["desc_peca_5"], key="update_desc_peca_5")
            with col202:
                valor_peca_5 = st.text_input("5 - Valor de cada peça", value=record_to_update["valor_peca_5"], key="update_valor_peca_5")
        
        with st.container():    
            col210, col211, col212 = st.columns([1,5,2])
            with col210:
                quant_peca_6 = st.text_input("6 - Quant.", value=record_to_update["quant_peca_6"], key="update_quant_peca_6")
            with col211:
                desc_peca_6 = st.text_input("6 - Descriçao da peça", value=record_to_update["desc_peca_6"], key="update_desc_peca_6")
            with col212:
                valor_peca_6 = st.text_input("6 - Valor de cada peça", value=record_to_update["valor_peca_6"], key="update_valor_peca_6")
        
        with st.container():    
            col220, col221, col222 = st.columns([1,5,2])
            with col220:
                quant_peca_7 = st.text_input("7 - Quant.", value=record_to_update["quant_peca_7"], key="update_quant_peca_7")
            with col221:
                desc_peca_7 = st.text_input("7 - Descriçao da peça", value=record_to_update["desc_peca_7"], key="update_desc_peca_7")
            with col222:
                valor_peca_7 = st.text_input("7 - Valor de cada peça", value=record_to_update["valor_peca_7"], key="update_valor_peca_7")
        
        with st.container():    
            col230, col231, col232 = st.columns([1,5,2])
            with col230:
                quant_peca_8 = st.text_input("8 - Quant.", value=record_to_update["quant_peca_8"], key="update_quant_peca_8")
            with col231:
                desc_peca_8 = st.text_input("8 - Descriçao da peça", value=record_to_update["desc_peca_8"], key="update_desc_peca_8")
            with col232:
                valor_peca_8 = st.text_input("8 - Valor de cada peça", value=record_to_update["valor_peca_8"], key="update_valor_peca_8")
        
        with st.container():    
            col240, col241, col242 = st.columns([1,5,2])
            with col240:
                quant_peca_9 = st.text_input("9 - Quant.", value=record_to_update["quant_peca_9"], key="update_quant_peca_9")
            with col241:
                desc_peca_9 = st.text_input("9 - Descriçao da peça", value=record_to_update["desc_peca_9"], key="update_desc_peca_9")
            with col242:
                valor_peca_9 = st.text_input("9 - Valor de cada peça", value=record_to_update["valor_peca_9"], key="update_valor_peca_9")
        
        with st.container():    
            col250, col251, col252 = st.columns([1,5,2])
            with col250:
                quant_peca_10 = st.text_input("10 - Quant.", value=record_to_update["quant_peca_10"], key="update_quant_peca_10")
            with col251:
                desc_peca_10 = st.text_input("10 - Descriçao da peça", value=record_to_update["desc_peca_10"], key="update_desc_peca_10")
            with col252:
                valor_peca_10 = st.text_input("10 - Valor de cada peça", value=record_to_update["valor_peca_10"], key="update_valor_peca_10")
        
        with st.container():    
            col260, col261, col262 = st.columns([1,5,2])
            with col260:
                quant_peca_11 = st.text_input("11 - Quant.", value=record_to_update["quant_peca_11"], key="update_quant_peca_11")
            with col261:
                desc_peca_11 = st.text_input("11 - Descriçao da peça", value=record_to_update["desc_peca_11"], key="update_desc_peca_11")
            with col262:
                valor_peca_11 = st.text_input("11 - Valor de cada peça", value=record_to_update["valor_peca_11"], key="update_valor_peca_11")
        
        with st.container():    
            col270, col271, col272 = st.columns([1,5,2])
            with col270:
                quant_peca_12 = st.text_input("12 - Quant.", value=record_to_update["quant_peca_12"], key="update_quant_peca_12")
            with col271:
                desc_peca_12 = st.text_input("12 - Descriçao da peça", value=record_to_update["desc_peca_12"], key="update_desc_peca_12")
            with col272:
                valor_peca_12 = st.text_input("12 - Valor de cada peça", value=record_to_update["valor_peca_12"], key="update_valor_peca_12")
        
        with st.container():    
            col280, col281, col282 = st.columns([1,5,2])
            with col280:
                quant_peca_13 = st.text_input("13 - Quant.", value=record_to_update["quant_peca_13"], key="update_quant_peca_13")
            with col281:
                desc_peca_13 = st.text_input("13 - Descriçao da peça", value=record_to_update["desc_peca_13"], key="update_desc_peca_13")
            with col282:
                valor_peca_13 = st.text_input("13 - Valor de cada peça", value=record_to_update["valor_peca_13"], key="update_valor_peca_13")
        
        with st.container():    
            col290, col291, col292 = st.columns([1,5,2])
            with col290:
                quant_peca_14 = st.text_input("14 - Quant.", value=record_to_update["quant_peca_14"], key="update_quant_peca_14")
            with col291:
                desc_peca_14 = st.text_input("14 - Descriçao da peça", value=record_to_update["desc_peca_14"], key="update_desc_peca_14")
            with col292:
                valor_peca_14 = st.text_input("14 - Valor de cada peça", value=record_to_update["valor_peca_14"], key="update_valor_peca_14")
        
        with st.container():    
            col300, col301, col302 = st.columns([1,5,2])
            with col300:
                quant_peca_15 = st.text_input("15 - Quant.", value=record_to_update["quant_peca_15"], key="update_quant_peca_15")
            with col301:
                desc_peca_15 = st.text_input("15 - Descriçao da peça", value=record_to_update["desc_peca_15"], key="update_desc_peca_15")
            with col302:
                valor_peca_15 = st.text_input("15 - Valor de cada peça", value=record_to_update["valor_peca_15"], key="update_valor_peca_15")
        
        with st.container():    
            col310, col311, col312 = st.columns([1,5,2])
            with col310:
                quant_peca_16 = st.text_input("16 - Quant.", value=record_to_update["quant_peca_16"], key="update_quant_peca_16")
            with col311:
                desc_peca_16 = st.text_input("16 - Descriçao da peça", value=record_to_update["desc_peca_16"], key="update_desc_peca_16")
            with col312:
                valor_peca_16 = st.text_input("16 - Valor de cada peça", value=record_to_update["valor_peca_16"], key="update_valor_peca_16")     
        
        line(4, "blue")
        
        with st.container():
            col320, col321, col322, col323, col324 = st.columns([1.2, 1.2, 1, 1, 1])
            with col322:
                update_button = st.form_submit_button("Atualizar registro")

               if st.form_submit_button("Confirmar Atualização"):
                    try:
                        # Conexión a Google Sheets
                        gc = gspread.authorize(credentials)
                        spreadsheet = gc.open_by_key(SPREADSHEET_KEY)
                        worksheet = spreadsheet.worksheet(SHEET_NAME)
                        
                        # Encontrar la fila EXACTA que coincide con el ID
                        cell = worksheet.find(str(int(selected_id)))  # Busca el ID exacto
                        row_number = cell.row
                        
                        # Preparar los nuevos valores (en el ORDEN de las columnas)
                        new_values = []
                        for column in columnas_ordenadas:
                            if column == "user_id":
                                new_values.append(int(selected_id))  # Mantener el ID original
                            else:
                                # Usar el valor del formulario o el original si no existe
                                new_values.append(locals().get(column, record_to_update[column]))
                        
                        # Actualizar SOLO ESA FILA
                        worksheet.update(
                            f"A{row_number}",
                            [new_values],
                            value_input_option="USER_ENTERED"
                        )
                        
                        # Actualizar el DataFrame local
                        for i, col in enumerate(columnas_ordenadas):
                            existing_data.loc[existing_data["user_id"] == selected_id, col] = new_values[i]
                        
                        st.success("✅ Atualização concluída com sucesso!")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Erro crítico: {str(e)}")
                        st.error("Recomendo recarregar a página e tentar novamente.")
#===================================================================================================================================================================
# --- Nueva Opción 3: Ver todas las órdenes ---
elif action == "Ver todos as ordens de serviço":
    st.header("📋 Lista completa de órdenes de servicio")
    
    # Mostrar el DataFrame con mejor formato
    st.dataframe(
        existing_data,
        use_container_width=True,  # Ajusta el ancho al contenedor
        hide_index=True,            # Oculta el índice numérico
        column_config={            # Personaliza columnas (opcional)
            "date_in": "Data de entrada",
            "placa": "Placa",
            "user_id": "N° Ordem"
        }
    )
    
    # Opción para exportar a CSV (opcional)
    if st.button("Exportar para CSV"):
        csv = existing_data.to_csv(index=False)
        st.download_button(
            label="Baixar arquivo",
            data=csv,
            file_name="ordens_de_servico.csv",
            mime="text/csv"
        )
#===================================================================================================================================================================
elif action == "Apagar ordem de serviço":
    st.header("🗑️ Apagar Ordem de Serviço")
    
    # 1. Selección por ID/Placa (tu código existente)
    search_option = st.radio("Buscar por:", ["ID", "Placa"], horizontal=True)
    
    if search_option == "ID":
        user_id_to_delete = st.selectbox(
            "Selecione o ID da ordem para apagar",
            options=existing_data["user_id"].astype(int).tolist()
        )
    else:
        placa_to_delete = st.selectbox(
            "Selecione a placa para apagar",
            options=existing_data["placa"].unique().tolist()
        )
        user_id_to_delete = existing_data[existing_data["placa"] == placa_to_delete]["user_id"].values[0]
    
    # 2. Mostrar detalles
    st.markdown("**Detalhes da ordem selecionada:**")
    ordem_to_delete = existing_data[existing_data["user_id"] == user_id_to_delete].iloc[0]
    st.json(ordem_to_delete.to_dict())
    
    # 3. Doble confirmación (FUNCIONA CORRECTAMENTE)
    st.warning("⚠️ Esta ação não pode ser desfeita!")
    
    # Usamos session_state para rastrear el checkbox
    if 'confirmado' not in st.session_state:
        st.session_state.confirmado = False
    
    # Checkbox que actualiza session_state
    confirmado = st.checkbox(
        "✅ Marque esta caixa para confirmar a exclusão",
        value=st.session_state.confirmado,
        key='confirm_checkbox'
    )
    
    # Actualizamos el estado cuando cambia el checkbox
    if confirmado != st.session_state.confirmado:
        st.session_state.confirmado = confirmado
        st.rerun()  # Fuerza la actualización
    
    # Botón que depende del estado
    if st.button(
        "CONFIRMAR EXCLUSÃO",
        type="primary",
        disabled=not st.session_state.confirmado
    ):
        # 4. Código de eliminación
        existing_data = existing_data[existing_data["user_id"] != user_id_to_delete]
        existing_data.reset_index(drop=True, inplace=True)
        
        try:
            conn.update(worksheet="Hoja1", data=existing_data)
            st.success("Ordem apagada com sucesso!")
            st.session_state.confirmado = False  # Resetear estado
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao atualizar planilha: {str(e)}")
    
    # 5. Mostrar datos actualizados
    st.markdown("### Ordens restantes:")
    st.dataframe(existing_data, hide_index=True, use_container_width=True)
