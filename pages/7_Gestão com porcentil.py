
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
    page_title="Gestão de ordens",
    page_icon="🚗",
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
SHEET_NAME = 'Hoja 2'  # Nombre de la hoja dentro del documento

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
                      'item_serv_12', 'desc_ser_12', 'valor_serv_12', 'total_serviço', 'porcentaje_adicional',
                      'quant_peca_1', 'desc_peca_1', 'valor_peca_1', 'sub_tota_peca_1', 'valor_total_peca_1', 
                      'quant_peca_2', 'desc_peca_2', 'valor_peca_2', 'sub_tota_peca_2','valor_total_peca_2',
                      'quant_peca_3', 'desc_peca_3', 'valor_peca_3', 'sub_tota_peca_3', 'valor_total_peca_3',
                      'quant_peca_4', 'desc_peca_4', 'valor_peca_4', 'sub_tota_peca_4', 'valor_total_peca_4',
                      'quant_peca_5', 'desc_peca_5', 'valor_peca_5', 'sub_tota_peca_5', 'valor_total_peca_5',
                      'quant_peca_6', 'desc_peca_6', 'valor_peca_6', 'sub_tota_peca_6', 'valor_total_peca_6',
                      'quant_peca_7', 'desc_peca_7', 'valor_peca_7', 'sub_tota_peca_7', 'valor_total_peca_7',
                      'quant_peca_8', 'desc_peca_8', 'valor_peca_8', 'sub_tota_peca_8', 'valor_total_peca_8',
                      'quant_peca_9', 'desc_peca_9', 'valor_peca_9', 'sub_tota_peca_9', 'valor_total_peca_9',
                      'quant_peca_10', 'desc_peca_10', 'valor_peca_10', 'sub_tota_peca_10', 'valor_total_peca_10',
                      'quant_peca_11', 'desc_peca_11', 'valor_peca_11', 'sub_tota_peca_11', 'valor_total_peca_11',
                      'quant_peca_12', 'desc_peca_12', 'valor_peca_12', 'sub_tota_peca_12', 'valor_total_peca_12',
                      'quant_peca_13', 'desc_peca_13', 'valor_peca_13', 'sub_tota_peca_13', 'valor_total_peca_13',
                      'quant_peca_14', 'desc_peca_14', 'valor_peca_14', 'sub_tota_peca_14', 'valor_total_peca_14',
                      'quant_peca_15', 'desc_peca_15', 'valor_peca_15', 'sub_tota_peca_15', 'valor_total_peca_15',
                      'quant_peca_16', 'desc_peca_16', 'valor_peca_16', 'sub_tota_peca_16', 'valor_total_peca_16',
                      'total_costo_inicial', 'total_costo_final', 'forma_de_pagamento', 'pagamento_parcial', 
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
# Función para obtener el próximo ID disponible
def obtener_proximo_id(df):
    if df.empty or 'user_id' not in df.columns:
        return 1  # Si no hay datos, el primer ID es 1
    try:
        # Calcular el máximo ID y sumar 1
        return int(df['user_id'].max()) + 1
    except (ValueError, TypeError):
        # Si hay algún error (por ejemplo, valores no numéricos), retornar 1
        return 1

# Función para actualizar una orden de servicio
def atualizar_ordem(vendor_to_update, updated_record):
    try:
        # Obtener la hoja de cálculo
        worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
        
        # Limpiar la hoja existente antes de actualizar
        worksheet.clear()
        
        # Agregar los encabezados primero
        worksheet.append_row(columnas_ordenadas)
        
        # Actualizar el DataFrame existente
        existing_data.loc[existing_data["user_id"] == vendor_to_update, updated_record.columns] = updated_record.values
        
        # Agregar los datos fila por fila
        for row in existing_data.values.tolist():
            worksheet.append_row(row)
        
        st.success("Ordem de serviço atualizada com sucesso")
    except Exception as e:
        st.error(f"Erro ao atualizar planilha: {str(e)}")

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


# 1. Inicialización de variables
if 'subtotales' not in st.session_state:
    st.session_state.subtotales = {'costo_final_1': 0}

# 2. Función de cálculo (sin callback)
def calcular_subtotales():
    try:
        quant = float(st.session_state.quant_peca_1) if st.session_state.quant_peca_1 else 0
        valor = float(st.session_state.valor_peca_1) if st.session_state.valor_peca_1 else 0
        porcentaje = float(st.session_state.porcentaje_adicional) if 'porcentaje_adicional' in st.session_state else 30
        st.session_state.subtotales['costo_final_1'] = quant * valor * (1 + porcentaje/100)
    except:
        st.session_state.subtotales['costo_final_1'] = 0

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

        # En la sección "Nova ordem de serviço", antes de la sección de peças:
        centrar_texto("Configuración de Costos", 2, "yellow")

        with st.container():
            col_perc, col_empty = st.columns([2, 5])
            with col_perc:
                porcentaje_adicional = st.number_input(
                    "Porcentaje adicional para costos (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=30.0,  # Valor por defecto del 30%
                    step=0.5,
                    key="porcentaje_adicional"
                    on_change=calcular_subtotales
                )
                
        
        line(4, "blue")
        centrar_texto("Peças", 2, "yellow")

        with st.container():    
            col160, col161, col162, col163 = st.columns([1, 6, 1, 1])
            with col160:
                quant_peca_1 = st.text_input("2")
            with col161:
                desc_peca_1 = st.text_input("2 - Descriçao da peça")
            with col162:
                valor_peca_1 = st.text_input("2 - Custo")
            with col163:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_1 and valor_peca_1 and porcentaje_adicional:
                    try:
                        costo_final_1 = float(quant_peca_1) * float(valor_peca_1) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_1:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")

       
       
        



        with st.container():    
            col170, col171, col172, col173 = st.columns([1, 6, 1, 1])
            with col170:
                quant_peca_2 = st.text_input("2")
            with col171:
                desc_peca_2 = st.text_input("2 - Descriçao da peça")
            with col172:
                valor_peca_2 = st.text_input("2 - Custo")
            with col173:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_2 and valor_peca_2 and porcentaje_adicional:
                    try:
                        costo_final_2 = float(quant_peca_2) * float(valor_peca_2) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_2:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")

            

        with st.container():    
            col180, col181, col182, col183 = st.columns([1, 6, 1, 1])
            with col180:
                quant_peca_3 = st.text_input("3")
            with col181:
                desc_peca_3 = st.text_input("3 - Descriçao da peça")
            with col182:
                valor_peca_3 = st.text_input("3 - Custo")
            with col183:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_3 and valor_peca_3 and porcentaje_adicional:
                    try:
                        costo_final_3 = float(quant_peca_3) * float(valor_peca_3) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_3:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col190, col191, col192, col193 = st.columns([1, 6, 1, 1])
            with col190:
                quant_peca_4 = st.text_input("4")
            with col191:
                desc_peca_4 = st.text_input("4 - Descriçao da peça")
            with col192:
                valor_peca_4 = st.text_input("4 - Custo")
            with col193:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_4 and valor_peca_4 and porcentaje_adicional:
                    try:
                        costo_final_4 = float(quant_peca_4) * float(valor_peca_4) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_4:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col200, col201, col202, col203 = st.columns([1, 6, 1, 1])
            with col200:
                quant_peca_5 = st.text_input("5")
            with col201:
                desc_peca_5 = st.text_input("5 - Descriçao da peça")
            with col202:
                valor_peca_5 = st.text_input("5 - Custo")
            with col203:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_5 and valor_peca_5 and porcentaje_adicional:
                    try:
                        costo_final_5 = float(quant_peca_5) * float(valor_peca_5) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_5:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col210, col211, col212, col213 = st.columns([1, 6, 1, 1])
            with col210:
                quant_peca_6 = st.text_input("6")
            with col211:
                desc_peca_6 = st.text_input("6 - Descriçao da peça")
            with col212:
                valor_peca_6 = st.text_input("6 - Custo")
            with col213:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_6 and valor_peca_6 and porcentaje_adicional:
                    try:
                        costo_final_6 = float(quant_peca_6) * float(valor_peca_6) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_6:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
                
        
        with st.container():    
            col220, col221, col222, col223 = st.columns([1, 6, 1, 1])
            with col220:
                quant_peca_7 = st.text_input("7")
            with col221:
                desc_peca_7 = st.text_input("7 - Descriçao da peça")
            with col222:
                valor_peca_7 = st.text_input("7 - Custo")
            with col223:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_7 and valor_peca_7 and porcentaje_adicional:
                    try:
                        costo_final_7 = float(quant_peca_7) * float(valor_peca_7) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_7:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col230, col231, col232, col233 = st.columns([1, 6, 1, 1])
            with col230:
                quant_peca_8 = st.text_input("8")
            with col231:
                desc_peca_8 = st.text_input("8 - Descriçao da peça")
            with col232:
                valor_peca_8 = st.text_input("8 - Custo")
            with col233:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_8 and valor_peca_8 and porcentaje_adicional:
                    try:
                        costo_final_8 = float(quant_peca_8) * float(valor_peca_8) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_8:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col240, col241, col242, col243 = st.columns([1, 6, 1, 1])
            with col240:
                quant_peca_9 = st.text_input("9")
            with col241:
                desc_peca_9 = st.text_input("9 - Descriçao da peça")
            with col242:
                valor_peca_9 = st.text_input("9 - Custo")
            with col243:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_9 and valor_peca_9 and porcentaje_adicional:
                    try:
                        costo_final_9 = float(quant_peca_9) * float(valor_peca_9) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_9:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col250, col251, col252, col253 = st.columns([1, 6, 1, 1])
            with col250:
                quant_peca_10 = st.text_input("10")
            with col251:
                desc_peca_10 = st.text_input("10 - Descriçao da peça")
            with col252:
                valor_peca_10 = st.text_input("10 - Custo")
            with col253:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_10 and valor_peca_10 and porcentaje_adicional:
                    try:
                        costo_final_10 = float(quant_peca_10) * float(valor_peca_10) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_10:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col260, col261, col262, col263 = st.columns([1, 6, 1, 1])
            with col260:
                quant_peca_11 = st.text_input("11")
            with col261:
                desc_peca_11 = st.text_input("11 - Descriçao da peça")
            with col262:
                valor_peca_11 = st.text_input("11 - Custo")
            with col263:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_11 and valor_peca_11 and porcentaje_adicional:
                    try:
                        costo_final_11 = float(quant_peca_11) * float(valor_peca_11) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_11:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col270, col271, col272, col273 = st.columns([1, 6, 1, 1])
            with col270:
                quant_peca_12 = st.text_input("12")
            with col271:
                desc_peca_12 = st.text_input("12 - Descriçao da peça")
            with col272:
                valor_peca_12 = st.text_input("12 - Custo")
            with col273:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_12 and valor_peca_12 and porcentaje_adicional:
                    try:
                        costo_final_12 = float(quant_peca_12) * float(valor_peca_12) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_12:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col280, col281, col282, col283 = st.columns([1, 6, 1, 1])
            with col280:
                quant_peca_13 = st.text_input("13")
            with col281:
                desc_peca_13 = st.text_input("13 - Descriçao da peça")
            with col282:
                valor_peca_13 = st.text_input("13 - Custo")
            with col283:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_13 and valor_peca_13 and porcentaje_adicional:
                    try:
                        costo_final_13 = float(quant_peca_13) * float(valor_peca_13) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_13:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col290, col291, col292, col293 = st.columns([1, 6, 1, 1])
            with col290:
                quant_peca_14 = st.text_input("14")
            with col291:
                desc_peca_14 = st.text_input("14 - Descriçao da peça")
            with col292:
                valor_peca_14 = st.text_input("14 - Custo")
            with col293:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_14 and valor_peca_14 and porcentaje_adicional:
                    try:
                        costo_final_14 = float(quant_peca_14) * float(valor_peca_14) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_14:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col300, col301, col302, col303 = st.columns([1, 6, 1, 1])
            with col300:
                quant_peca_15 = st.text_input("15")
            with col301:
                desc_peca_15 = st.text_input("15 - Descriçao da peça")
            with col302:
                valor_peca_15 = st.text_input("15 - Custo")
            with col303:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_15 and valor_peca_15 and porcentaje_adicional:
                    try:
                        costo_final_15 = float(quant_peca_15) * float(valor_peca_15) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_15:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
        with st.container():    
            col310, col311, col312, col313 = st.columns([1, 6, 1, 1])
            with col310:
                quant_peca_16 = st.text_input("16")
            with col311:
                desc_peca_16 = st.text_input("16 - Descriçao da peça")
            with col312:
                valor_peca_16 = st.text_input("16 - Custo")
            with col313:
                # Mostrar costo final (con porcentaje aplicado)
                if quant_peca_16 and valor_peca_16 and porcentaje_adicional:
                    try:
                        costo_final_16 = float(quant_peca_16) * float(valor_peca_16) * (1 + porcentaje_adicional/100)
                        st.text(f"R$ {costo_final_16:.2f}")
                    except:
                        st.text("Valor")
                else:
                    st.text("Valor")
        
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
                    'porcentaje_adicional': porcentaje_adicional,
                    'quant_peca_1': quant_peca_1 if 'quant_peca_1' in locals() else None,
                    'desc_peca_1': desc_peca_1 if 'desc_peca_1' in locals() else None,
                    'valor_peca_1': valor_peca_1 if 'valor_peca_1' in locals() else None,
                    'sub_tota_peca_1': costo_inicial_1 if 'costo_inicial_1' in locals() else 0,
                    'valor_total_peca_1': costo_final_1 if 'costo_final_1' in locals() else 0,                
                    'quant_peca_2': quant_peca_2 if 'quant_peca_2' in locals() else None,
                    'desc_peca_2': desc_peca_2 if 'desc_peca_2' in locals() else None,
                    'valor_peca_2': valor_peca_2 if 'valor_peca_2' in locals() else None,
                    'sub_tota_peca_2': costo_inicial_2 if 'costo_inicial_2' in locals() else 0,
                    'valor_total_peca_2': costo_final_2 if 'costo_final_2' in locals() else 0,                   
                    'quant_peca_3': quant_peca_3 if 'quant_peca_3' in locals() else None,
                    'desc_peca_3': desc_peca_3 if 'desc_peca_3' in locals() else None,
                    'valor_peca_3': valor_peca_3 if 'valor_peca_3' in locals() else None,
                    'sub_tota_peca_3': costo_inicial_3 if 'costo_inicial_3' in locals() else 0,
                    'valor_total_peca_3': costo_final_3 if 'costo_final_3' in locals() else 0,                   
                    'quant_peca_4': quant_peca_4 if 'quant_peca_4' in locals() else None,
                    'desc_peca_4': desc_peca_4 if 'desc_peca_4' in locals() else None,
                    'valor_peca_4': valor_peca_4 if 'valor_peca_4' in locals() else None,
                    'sub_tota_peca_4': costo_inicial_4 if 'costo_inicial_4' in locals() else 0,
                    'valor_total_peca_4': costo_final_4 if 'costo_final_4' in locals() else 0,                    
                    'quant_peca_5': quant_peca_5 if 'quant_peca_5' in locals() else None,
                    'desc_peca_5': desc_peca_5 if 'desc_peca_5' in locals() else None,
                    'valor_peca_5': valor_peca_5 if 'valor_peca_5' in locals() else None,
                    'sub_tota_peca_5': costo_inicial_5 if 'costo_inicial_5' in locals() else 0,
                    'valor_total_peca_5': costo_final_5 if 'costo_final_5' in locals() else 0,                    
                    'quant_peca_6': quant_peca_6 if 'quant_peca_6' in locals() else None,
                    'desc_peca_6': desc_peca_6 if 'desc_peca_6' in locals() else None,
                    'valor_peca_6': valor_peca_6 if 'valor_peca_6' in locals() else None,
                    'sub_tota_peca_6': costo_inicial_6 if 'costo_inicial_6' in locals() else 0,
                    'valor_total_peca_6': costo_final_6 if 'costo_final_6' in locals() else 0,                      
                    'quant_peca_7': quant_peca_7 if 'quant_peca_7' in locals() else None,
                    'desc_peca_7': desc_peca_7 if 'desc_peca_7' in locals() else None,
                    'valor_peca_7': valor_peca_7 if 'valor_peca_7' in locals() else None,
                    'sub_tota_peca_7': costo_inicial_7 if 'costo_inicial_7' in locals() else 0,
                    'valor_total_peca_7': costo_final_7 if 'costo_final_7' in locals() else 0,                    
                    'quant_peca_8': quant_peca_8 if 'quant_peca_8' in locals() else None,
                    'desc_peca_8': desc_peca_8 if 'desc_peca_8' in locals() else None,
                    'valor_peca_8': valor_peca_8 if 'valor_peca_8' in locals() else None,
                    'sub_tota_peca_8': costo_inicial_8 if 'costo_inicial_8' in locals() else 0,
                    'valor_total_peca_8': costo_final_8 if 'costo_final_8' in locals() else 0,                   
                    'quant_peca_9': quant_peca_9 if 'quant_peca_9' in locals() else None,
                    'desc_peca_9': desc_peca_9 if 'desc_peca_9' in locals() else None,
                    'valor_peca_9': valor_peca_9 if 'valor_peca_9' in locals() else None,
                    'sub_tota_peca_9': costo_inicial_9 if 'costo_inicial_9' in locals() else 0,
                    'valor_total_peca_9': costo_final_9 if 'costo_final_9' in locals() else 0,                  
                    'quant_peca_10': quant_peca_10 if 'quant_peca_10' in locals() else None,
                    'desc_peca_10': desc_peca_10 if 'desc_peca_10' in locals() else None,
                    'valor_peca_10': valor_peca_10 if 'valor_peca_10' in locals() else None,
                    'sub_tota_peca_10': costo_inicial_10 if 'costo_inicial_10' in locals() else 0,
                    'valor_total_peca_10': costo_final_10 if 'costo_final_10' in locals() else 0,                 
                    'quant_peca_11': quant_peca_11 if 'quant_peca_11' in locals() else None,
                    'desc_peca_11': desc_peca_11 if 'desc_peca_11' in locals() else None,
                    'valor_peca_11': valor_peca_11 if 'valor_peca_11' in locals() else None,
                    'sub_tota_peca_11': costo_inicial_11 if 'costo_inicial_11' in locals() else 0,
                    'valor_total_peca_11': costo_final_11 if 'costo_final_11' in locals() else 0,                    
                    'quant_peca_12': quant_peca_12 if 'quant_peca_12' in locals() else None,
                    'desc_peca_12': desc_peca_12 if 'desc_peca_12' in locals() else None,
                    'valor_peca_12': valor_peca_12 if 'valor_peca_12' in locals() else None,
                    'sub_tota_peca_12': costo_inicial_12 if 'costo_inicial_12' in locals() else 0,
                    'valor_total_peca_12': costo_final_12 if 'costo_final_12' in locals() else 0,              
                    'quant_peca_13': quant_peca_13 if 'quant_peca_13' in locals() else None,
                    'desc_peca_13': desc_peca_13 if 'desc_peca_13' in locals() else None,
                    'valor_peca_13': valor_peca_13 if 'valor_peca_13' in locals() else None,
                    'sub_tota_peca_13': costo_inicial_13 if 'costo_inicial_13' in locals() else 0,
                    'valor_total_peca_13': costo_final_13 if 'costo_final_13' in locals() else 0,                 
                    'quant_peca_14': quant_peca_14 if 'quant_peca_14' in locals() else None,
                    'desc_peca_14': desc_peca_14 if 'desc_peca_14' in locals() else None,
                    'valor_peca_14': valor_peca_14 if 'valor_peca_14' in locals() else None,
                    'sub_tota_peca_14': costo_inicial_14 if 'costo_inicial_14' in locals() else 0,
                    'valor_total_peca_14': costo_final_14 if 'costo_final_14' in locals() else 0,                    
                    'quant_peca_15': quant_peca_15 if 'quant_peca_15' in locals() else None,
                    'desc_peca_15': desc_peca_15 if 'desc_peca_15' in locals() else None,
                    'valor_peca_15': valor_peca_15 if 'valor_peca_15' in locals() else None,
                    'sub_tota_peca_15': costo_inicial_15 if 'costo_inicial_15' in locals() else 0,
                    'valor_total_peca_15': costo_final_15 if 'costo_final_15' in locals() else 0,                  
                    'quant_peca_16': quant_peca_16 if 'quant_peca_16' in locals() else None,
                    'desc_peca_16': desc_peca_16 if 'desc_peca_16' in locals() else None,
                    'valor_peca_16': valor_peca_16 if 'valor_peca_16' in locals() else None,
                    'sub_tota_peca_16': costo_inicial_16 if 'costo_inicial_16' in locals() else 0,
                    'valor_total_peca_15': costo_final_16 if 'costo_final_16' in locals() else 0,                   
                    'total_costo_inicial': sum([v for k, v in locals().items() if k.startswith('costo_inicial_')]),
                    'total_costo_final': sum([v for k, v in locals().items() if k.startswith('costo_final_')]),
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

# Código para actualizar una orden de servicio
elif action == "Atualizar ordem existente":
    centrar_texto("Selecione o ID ou PLACA da Ordem de serviço que deseja atualizar.", 6, "yellow")
    
     # Eliminar filas con NaN en la columna "user_id"
    existing_data = existing_data.dropna(subset=["user_id"])

    # Convertir la columna "user_id" a enteros
    existing_data["user_id"] = existing_data["user_id"].astype(int)

    with st.container():    
        col200, col201, col202, col203, col204 = st.columns([2, 1.5, 2, 1, 1])
        with col200:
            # Opción para buscar por ID o por placa
            search_option = st.radio("Buscar por:", ["ID", "Placa"])
            
            if search_option == "ID":
                with col201:
                    vendor_to_update = st.selectbox("Selecione o ID", options=existing_data["user_id"].tolist())
                    vendor_data = existing_data[existing_data["user_id"] == vendor_to_update].iloc[0]
            else:
                with col201:
                    placa_to_search = st.text_input("Digite um número de placa")
                    if placa_to_search:
                        vendor_data_filtered = existing_data[existing_data["placa"] == placa_to_search]
                        if not vendor_data_filtered.empty:
                            vendor_data = vendor_data_filtered.iloc[0]
                            vendor_to_update = vendor_data["user_id"]
                        else:
                            with col202:
                                st.warning("Nenhuma ordem de serviço encontrada com essa placa.")
                                st.stop()  # Detener la ejecución si no se encuentra la placa
                    else:
                        with col202:
                            st.warning("Digite um número de placa para buscar.")
                            st.stop()  # Detener la ejecución si no se ingresa una placa


    # Mostrar los campos del formulario con los valores actuales
    with st.form(key="update_form"):
        st.markdown("Atualize os detalhes da ordem de serviço")       
        with st.container():    
            col00, col01, col02, col03, col04 = st.columns(5)
            with col00:
                placa = st.text_input("Placa", value=vendor_data["placa"], key="update_placa")
            with col02:
                data_entrada = st.text_input("Data de entrada", value=vendor_data["date_in"], key="update_data_entrada")
            with col03:
                previsao_entrega = st.text_input("Previsão de entrega", value=vendor_data["date_prev"], key="update_previsao_entrega")
            with col04:
                data_saida = st.text_input("Data de saida", value=vendor_data["date_out"], key="update_data_saida")
            
        with st.container():    
            col10, col11, col12, col13, col14 = st.columns(5)
            with col10:
                carro = st.text_input("Marca", value=vendor_data["carro"], key="update_carro")
            with col11:
                modelo = st.text_input("Modelo", value=vendor_data["modelo"], key="update_modelo")
            with col12:
                ano = st.text_input("Ano", value=vendor_data["ano"], key="update_ano")
            with col13:
                cor = st.text_input("Cor", value=vendor_data["cor"], key="update_cor")
            with col14:
                km = st.text_input("Km", value=vendor_data["km"], key="update_km")

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
                dono_empresa = st.text_input("Dono / Empresa", value=vendor_data["dono_empresa"], key="update_dono_empresa")
            with col31:
                telefone = st.text_input("Telefone", value=vendor_data["telefone"], key="update_telefone")
            with col32:
                endereco = st.text_input("Endereço", value=vendor_data["endereco"], key="update_endereco")

        line(4, "blue")
        centrar_texto("Serviços", 2, "yellow")

        with st.container():    
            col40, col41, col42 = st.columns([1,5,2])
            with col40:
                item_serv_1 = st.text_input("1 - Item",  value=vendor_data["item_serv_1"], key="update_item_serv_1")
            with col41:
                desc_ser_1 = st.text_input("1 - Descriçao de serviço",  value=vendor_data["desc_ser_1"], key="update_desc_ser_1")
            with col42:
                valor_serv_1 = st.text_input("1 - Valor do serviço",  value=vendor_data["valor_serv_1"], key="update_valor_serv_1")
                
        with st.container():    
            col50, col51, col52 = st.columns([1,5,2])
            with col50:
                item_serv_2 = st.text_input("2 - Item",  value=vendor_data["item_serv_2"], key="update_item_serv_2")
            with col51:
                desc_ser_2 = st.text_input("2 -Descriçao de serviço",  value=vendor_data["desc_ser_2"], key="update_desc_ser_2")
            with col52:
                valor_serv_2 = st.text_input("2- Valor do serviço",  value=vendor_data["valor_serv_2"], key="update_valor_serv_2")

        with st.container():    
            col60, col61, col62 = st.columns([1,5,2])
            with col60:
                item_serv_3 = st.text_input("3 - Item",  value=vendor_data["item_serv_3"], key="update_item_serv_3")
            with col61:
                desc_ser_3 = st.text_input("3 -Descriçao de serviço",  value=vendor_data["desc_ser_3"], key="update_desc_ser_3")
            with col62:
                valor_serv_3 = st.text_input("3- Valor do serviço",  value=vendor_data["valor_serv_3"], key="update_valor_serv_3")

        with st.container():    
            col70, col71, col72 = st.columns([1,5,2])
            with col70:
                item_serv_4 = st.text_input("4 - Item",  value=vendor_data["item_serv_4"], key="update_item_serv_4")
            with col71:
                desc_ser_4 = st.text_input("4 -Descriçao de serviço",  value=vendor_data["desc_ser_4"], key="update_desc_ser_4")
            with col72:
                valor_serv_4 = st.text_input("4- Valor do serviço", value=vendor_data["valor_serv_4"], key="update_valor_serv_4")

        with st.container():    
            col80, col81, col82 = st.columns([1,5,2])
            with col80:
                item_serv_5 = st.text_input("5 - Item", value=vendor_data["item_serv_5"], key="update_item_serv_5")
            with col81:
                desc_ser_5 = st.text_input("5 - Descriçao de serviço", value=vendor_data["desc_ser_5"], key="update_desc_ser_5")
            with col82:
                valor_serv_5 = st.text_input("5 - Valor do serviço", value=vendor_data["valor_serv_5"], key="update_valor_serv_5")
        
        with st.container():    
            col90, col91, col92 = st.columns([1,5,2])
            with col90:
                item_serv_6 = st.text_input("6 - Item", value=vendor_data["item_serv_6"], key="update_item_serv_6")
            with col91:
                desc_ser_6 = st.text_input("6 - Descriçao de serviço", value=vendor_data["desc_ser_6"], key="update_desc_ser_6")
            with col92:
                valor_serv_6 = st.text_input("6 - Valor do serviço", value=vendor_data["valor_serv_6"], key="update_valor_serv_6")
        
        with st.container():    
            col100, col101, col102 = st.columns([1,5,2])
            with col100:
                item_serv_7 = st.text_input("7 - Item", value=vendor_data["item_serv_7"], key="update_item_serv_7")
            with col101:
                desc_ser_7 = st.text_input("7 - Descriçao de serviço", value=vendor_data["desc_ser_7"], key="update_desc_ser_7")
            with col102:
                valor_serv_7 = st.text_input("7 - Valor do serviço", value=vendor_data["valor_serv_7"], key="update_valor_serv_7")
        
        with st.container():    
            col110, col111, col112 = st.columns([1,5,2])
            with col110:
                item_serv_8 = st.text_input("8 - Item", value=vendor_data["item_serv_8"], key="update_item_serv_8")
            with col111:
                desc_ser_8 = st.text_input("8 - Descriçao de serviço", value=vendor_data["desc_ser_8"], key="update_desc_ser_8")
            with col112:
                valor_serv_8 = st.text_input("8 - Valor do serviço", value=vendor_data["valor_serv_8"], key="update_valor_serv_8")
        
        with st.container():    
            col120, col121, col122 = st.columns([1,5,2])
            with col120:
                item_serv_9 = st.text_input("9 - Item", value=vendor_data["item_serv_9"], key="update_item_serv_9")
            with col121:
                desc_ser_9 = st.text_input("9 - Descriçao de serviço", value=vendor_data["desc_ser_9"], key="update_desc_ser_9")
            with col122:
                valor_serv_9 = st.text_input("9 - Valor do serviço", value=vendor_data["valor_serv_9"], key="update_valor_serv_9")
        
        with st.container():    
            col130, col131, col132 = st.columns([1,5,2])
            with col130:
                item_serv_10 = st.text_input("10 - Item", value=vendor_data["item_serv_10"], key="update_item_serv_10")
            with col131:
                desc_ser_10 = st.text_input("10 - Descriçao de serviço", value=vendor_data["desc_ser_10"], key="update_desc_ser_10")
            with col132:
                valor_serv_10 = st.text_input("10 - Valor do serviço", value=vendor_data["valor_serv_10"], key="update_valor_serv_10")
        
        with st.container():    
            col140, col141, col142 = st.columns([1,5,2])
            with col140:
                item_serv_11 = st.text_input("11 - Item", value=vendor_data["item_serv_11"], key="update_item_serv_11")
            with col141:
                desc_ser_11 = st.text_input("11 - Descriçao de serviço", value=vendor_data["desc_ser_11"], key="update_desc_ser_11")
            with col142:
                valor_serv_11 = st.text_input("11 - Valor do serviço", value=vendor_data["valor_serv_11"], key="update_valor_serv_11")
        
        with st.container():    
            col150, col151, col152 = st.columns([1,5,2])
            with col150:
                item_serv_12 = st.text_input("12 - Item", value=vendor_data["item_serv_12"], key="update_item_serv_12")
            with col151:
                desc_ser_12 = st.text_input("12 - Descriçao de serviço", value=vendor_data["desc_ser_12"], key="update_desc_ser_12")
            with col152:
                valor_serv_12 = st.text_input("12 - Valor do serviço", value=vendor_data["valor_serv_12"], key="update_valor_serv_12")
                
        # En la sección "Atualizar ordem existente":

        line(4, "blue")
        centrar_texto("Configuración de Costos", 2, "yellow")
        
        with st.container():
            col_perc, col_empty = st.columns([2, 5])
            with col_perc:
                # Con esta versión más robusta:
                try:
                    porcentaje_default = float(vendor_data.get("porcentaje_adicional", 30.0))
                except (TypeError, ValueError):
                    porcentaje_default = 30.0  # Valor por defecto si hay error
                
                porcentaje_adicional = st.number_input(
                    "Porcentaje adicional para costos (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=porcentaje_default,
                    step=0.5,
                    key="update_porcentaje_adicional"
                )
        
        line(4, "blue")
        centrar_texto("Peças", 2, "yellow")

        with st.container():    
            col160, col161, col162, col163 = st.columns([1, 6, 1, 1])
            with col160:
                quant_peca_1 = st.text_input("1", value=vendor_data["quant_peca_1"], key="update_quant_peca_1")
            with col161:
                desc_peca_1 = st.text_input("1 - Descriçao da peça", value=vendor_data["desc_peca_1"], key="update_desc_peca_1")
            with col162:
                valor_peca_1 = st.text_input("1 - Custo", value=vendor_data["valor_peca_1"], key="update_valor_peca_1")
            with col163:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_1) if quant_peca_1 else 0
                    custo_unitario = float(valor_peca_1) if valor_peca_1 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )

        with st.container():    
            col170, col171, col172, col173 = st.columns([1, 6, 1, 1])
            with col170:
                quant_peca_2 = st.text_input("2", value=vendor_data["quant_peca_2"], key="update_quant_peca_2")
            with col171:
                desc_peca_2 = st.text_input("2 - Descriçao da peça", value=vendor_data["desc_peca_2"], key="update_desc_peca_2")
            with col172:
                valor_peca_2 = st.text_input("2 - Custo", value=vendor_data["valor_peca_2"], key="update_valor_peca_2")
            with col173:
                 # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_2) if quant_peca_2 else 0
                    custo_unitario = float(valor_peca_2) if valor_peca_2 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )

        with st.container():    
            col180, col181, col182, col183 = st.columns([1, 6, 1, 1])
            with col180:
                quant_peca_3 = st.text_input("3", value=vendor_data["quant_peca_3"], key="update_quant_peca_3")
            with col181:
                desc_peca_3 = st.text_input("3 - Descriçao da peça", value=vendor_data["desc_peca_3"], key="update_desc_peca_3")
            with col182:
                valor_peca_3 = st.text_input("3 - Custo", value=vendor_data["valor_peca_3"], key="update_valor_peca_3")
            with col183:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_3) if quant_peca_3 else 0
                    custo_unitario = float(valor_peca_3) if valor_peca_3 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        with st.container():    
            col190, col191, col192, col193 = st.columns([1, 6, 1, 1])
            with col190:
                quant_peca_4 = st.text_input("4", value=vendor_data["quant_peca_4"], key="update_quant_peca_4")
            with col191:
                desc_peca_4 = st.text_input("4 - Descriçao da peça", value=vendor_data["desc_peca_4"], key="update_desc_peca_4")
            with col192:
                valor_peca_4 = st.text_input("4 - Custo", value=vendor_data["valor_peca_4"], key="update_valor_peca_4")
            with col193:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_4) if quant_peca_4 else 0
                    custo_unitario = float(valor_peca_4) if valor_peca_4 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        with st.container():    
            col200, col201, col202, col203 = st.columns([1, 6, 1, 1])
            with col200:
                quant_peca_5 = st.text_input("5", value=vendor_data["quant_peca_5"], key="update_quant_peca_5")
            with col201:
                desc_peca_5 = st.text_input("5 - Descriçao da peça", value=vendor_data["desc_peca_5"], key="update_desc_peca_5")
            with col202:
                valor_peca_5 = st.text_input("5 - Custo", value=vendor_data["valor_peca_5"], key="update_valor_peca_5")
            with col203:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_5) if quant_peca_5 else 0
                    custo_unitario = float(valor_peca_5) if valor_peca_5 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        with st.container():    
            col210, col211, col212, col213 = st.columns([1, 6, 1, 1])
            with col210:
                quant_peca_6 = st.text_input("6", value=vendor_data["quant_peca_6"], key="update_quant_peca_6")
            with col211:
                desc_peca_6 = st.text_input("6 - Descriçao da peça", value=vendor_data["desc_peca_6"], key="update_desc_peca_6")
            with col212:
                valor_peca_6 = st.text_input("6 - Custo", value=vendor_data["valor_peca_6"], key="update_valor_peca_6")
            with col213:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_6) if quant_peca_6 else 0
                    custo_unitario = float(valor_peca_6) if valor_peca_6 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        with st.container():    
            col220, col221, col222, col223 = st.columns([1, 6, 1, 1])
            with col220:
                quant_peca_7 = st.text_input("7", value=vendor_data["quant_peca_7"], key="update_quant_peca_7")
            with col221:
                desc_peca_7 = st.text_input("7 - Descriçao da peça", value=vendor_data["desc_peca_7"], key="update_desc_peca_7")
            with col222:
                valor_peca_7 = st.text_input("7 - Custo", value=vendor_data["valor_peca_7"], key="update_valor_peca_7")
            with col223:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_7) if quant_peca_7 else 0
                    custo_unitario = float(valor_peca_7) if valor_peca_7 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        with st.container():    
            col230, col231, col232, col233 = st.columns([1, 6, 1, 1])
            with col230:
                quant_peca_8 = st.text_input("8", value=vendor_data["quant_peca_8"], key="update_quant_peca_8")
            with col231:
                desc_peca_8 = st.text_input("8 - Descriçao da peça", value=vendor_data["desc_peca_8"], key="update_desc_peca_8")
            with col232:
                valor_peca_8 = st.text_input("8 - Custo", value=vendor_data["valor_peca_8"], key="update_valor_peca_8")
            with col233:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_8) if quant_peca_8 else 0
                    custo_unitario = float(valor_peca_8) if valor_peca_8 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        with st.container():    
            col240, col241, col242, col243 = st.columns([1, 6, 1, 1])
            with col240:
                quant_peca_9 = st.text_input("9", value=vendor_data["quant_peca_9"], key="update_quant_peca_9")
            with col241:
                desc_peca_9 = st.text_input("9 - Descriçao da peça", value=vendor_data["desc_peca_9"], key="update_desc_peca_9")
            with col242:
                valor_peca_9 = st.text_input("9 - Custo", value=vendor_data["valor_peca_9"], key="update_valor_peca_9")
            with col243:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_9) if quant_peca_9 else 0
                    custo_unitario = float(valor_peca_9) if valor_peca_9 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )

            
        
        with st.container():    
            col250, col251, col252, col253 = st.columns([1, 6, 1, 1])
            with col250:
                quant_peca_10 = st.text_input("10", value=vendor_data["quant_peca_10"], key="update_quant_peca_10")
            with col251:
                desc_peca_10 = st.text_input("10 - Descriçao da peça", value=vendor_data["desc_peca_10"], key="update_desc_peca_10")
            with col252:
                valor_peca_10 = st.text_input("10 - Custo", value=vendor_data["valor_peca_10"], key="update_valor_peca_10")
            with col253:
                 # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_10) if quant_peca_10 else 0
                    custo_unitario = float(valor_peca_10) if valor_peca_10 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        with st.container():    
            col260, col261, col262, col263 = st.columns([1, 6, 1, 1])
            with col260:
                quant_peca_11 = st.text_input("11", value=vendor_data["quant_peca_11"], key="update_quant_peca_11")
            with col261:
                desc_peca_11 = st.text_input("11 - Descriçao da peça", value=vendor_data["desc_peca_11"], key="update_desc_peca_11")
            with col262:
                valor_peca_11 = st.text_input("11 - Custo", value=vendor_data["valor_peca_11"], key="update_valor_peca_11")
            with col263:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_11) if quant_peca_11 else 0
                    custo_unitario = float(valor_peca_11) if valor_peca_11 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        with st.container():    
            col270, col271, col272, col273 = st.columns([1, 6, 1, 1])
            with col270:
                quant_peca_12 = st.text_input("12", value=vendor_data["quant_peca_12"], key="update_quant_peca_12")
            with col271:
                desc_peca_12 = st.text_input("12 - Descriçao da peça", value=vendor_data["desc_peca_12"], key="update_desc_peca_12")
            with col272:
                valor_peca_12 = st.text_input("12 - Custo", value=vendor_data["valor_peca_12"], key="update_valor_peca_12")
            with col273:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_12) if quant_peca_12 else 0
                    custo_unitario = float(valor_peca_12) if valor_peca_12 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )

        
        with st.container():    
            col280, col281, col282, col283 = st.columns([1, 6, 1, 1])
            with col280:
                quant_peca_13 = st.text_input("13", value=vendor_data["quant_peca_13"], key="update_quant_peca_13")
            with col281:
                desc_peca_13 = st.text_input("13 - Descriçao da peça", value=vendor_data["desc_peca_13"], key="update_desc_peca_13")
            with col282:
                valor_peca_13 = st.text_input("13 - Custo", value=vendor_data["valor_peca_13"], key="update_valor_peca_13")
            with col283:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_13) if quant_peca_13 else 0
                    custo_unitario = float(valor_peca_13) if valor_peca_13 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )

        
        with st.container():    
            col290, col291, col292, col293 = st.columns([1, 6, 1, 1])
            with col290:
                quant_peca_14 = st.text_input("14", value=vendor_data["quant_peca_14"], key="update_quant_peca_14")
            with col291:
                desc_peca_14 = st.text_input("14 - Descriçao da peça", value=vendor_data["desc_peca_14"], key="update_desc_peca_14")
            with col292:
                valor_peca_14 = st.text_input("14 - Custo", value=vendor_data["valor_peca_14"], key="update_valor_peca_14")
            with col293:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_14) if quant_peca_14 else 0
                    custo_unitario = float(valor_peca_14) if valor_peca_14 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        with st.container():    
            col300, col301, col302, col303 = st.columns([1, 6, 1, 1])
            with col300:
                quant_peca_15 = st.text_input("15", value=vendor_data["quant_peca_15"], key="update_quant_peca_15")
            with col301:
                desc_peca_15 = st.text_input("15 - Descriçao da peça", value=vendor_data["desc_peca_15"], key="update_desc_peca_15")
            with col302:
                valor_peca_15 = st.text_input("15 - Custo", value=vendor_data["valor_peca_15"], key="update_valor_peca_15")
            with col303:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_15) if quant_peca_15 else 0
                    custo_unitario = float(valor_peca_15) if valor_peca_15 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        with st.container():    
            col310, col311, col312, col313 = st.columns([1, 6, 1, 1])
            with col310:
                quant_peca_16 = st.text_input("16", value=vendor_data["quant_peca_16"], key="update_quant_peca_16")
            with col311:
                desc_peca_16 = st.text_input("16 - Descriçao da peça", value=vendor_data["desc_peca_16"], key="update_desc_peca_16")
            with col312:
                valor_peca_16 = st.text_input("16 - Custo", value=vendor_data["valor_peca_16"], key="update_valor_peca_16") 
            with col313:
                # Cálculo directo usando el porcentaje_adicional ya definido
                try:
                    quantidade = float(quant_peca_16) if quant_peca_16 else 0
                    custo_unitario = float(valor_peca_16) if valor_peca_16 else 0
                    valor_final = quantidade * custo_unitario * (1 + porcentaje_adicional/100)
                    # Texto unificado con estilo
                    centrar_texto("", 7,"white")
                    st.markdown(
                        f'<div style="display: flex; align-items: center; height: 38px;">'
                        f'<span style="color: #FFD700; font-weight: bold;">R$ {valor_final:.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                except:
                    centrar_texto("", 7,"white")
                    st.markdown(
                        '<div style="display: flex; align-items: center; height: 38px;">'
                        '<span style="color: #FFD700; font-weight: bold;">R$ 0.00</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        
        line(4, "blue")
        
        with st.container():
            col320, col321, col322, col323, col324 = st.columns([1.2, 1.2, 1, 1, 1])
            with col322:
                update_button = st.form_submit_button("Atualizar")

            if update_button:
                # Crear un diccionario con los datos actualizados
                updated_record = {
                    'user_id': vendor_to_update,  # Mantener el mismo user_id
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
                    'porcentaje_adicional': porcentaje_adicional,
                    'quant_peca_1': quant_peca_1 if 'quant_peca_1' in locals() else None,
                    'desc_peca_1': desc_peca_1 if 'desc_peca_1' in locals() else None,
                    'valor_peca_1': costo_inicial_1 if 'costo_inicial_1' in locals() else 0,
                    'valor_total_peca_1': costo_final_1 if 'costo_final_1' in locals() else 0,                   
                    'quant_peca_2': quant_peca_2 if 'quant_peca_2' in locals() else None,
                    'desc_peca_2': desc_peca_2 if 'desc_peca_2' in locals() else None,
                    'valor_peca_2': costo_inicial_2 if 'costo_inicial_2' in locals() else 0,
                    'valor_total_peca_2': costo_final_2 if 'costo_final_2' in locals() else 0,                
                    'quant_peca_3': quant_peca_3 if 'quant_peca_3' in locals() else None,
                    'desc_peca_3': desc_peca_3 if 'desc_peca_3' in locals() else None,
                    'valor_peca_3': costo_inicial_3 if 'costo_inicial_3' in locals() else 0,
                    'valor_total_peca_3': costo_final_3 if 'costo_final_3' in locals() else 0,                   
                    'quant_peca_4': quant_peca_4 if 'quant_peca_4' in locals() else None,
                    'desc_peca_4': desc_peca_4 if 'desc_peca_4' in locals() else None,
                    'valor_peca_4': costo_inicial_4 if 'costo_inicial_4' in locals() else 0,
                    'valor_total_peca_4': costo_final_4 if 'costo_final_4' in locals() else 0,                    
                    'quant_peca_5': quant_peca_5 if 'quant_peca_5' in locals() else None,
                    'desc_peca_5': desc_peca_5 if 'desc_peca_5' in locals() else None,
                    'valor_peca_5': costo_inicial_5 if 'costo_inicial_5' in locals() else 0,
                    'valor_total_peca_5': costo_final_5 if 'costo_final_5' in locals() else 0,                    
                    'quant_peca_6': quant_peca_6 if 'quant_peca_6' in locals() else None,
                    'desc_peca_6': desc_peca_6 if 'desc_peca_6' in locals() else None,
                    'valor_peca_6': costo_inicial_6 if 'costo_inicial_6' in locals() else 0,
                    'valor_total_peca_6': costo_final_6 if 'costo_final_6' in locals() else 0,                    
                    'quant_peca_7': quant_peca_7 if 'quant_peca_7' in locals() else None,
                    'desc_peca_7': desc_peca_7 if 'desc_peca_7' in locals() else None,
                    'valor_peca_7': costo_inicial_7 if 'costo_inicial_7' in locals() else 0,
                    'valor_total_peca_7': costo_final_7 if 'costo_final_7' in locals() else 0,                    
                    'quant_peca_8': quant_peca_8 if 'quant_peca_8' in locals() else None,
                    'desc_peca_8': desc_peca_8 if 'desc_peca_8' in locals() else None,
                    'valor_peca_8': costo_inicial_8 if 'costo_inicial_8' in locals() else 0,
                    'valor_total_peca_8': costo_final_8 if 'costo_final_8' in locals() else 0,                    
                    'valor_peca_9': costo_inicial_9 if 'costo_inicial_9' in locals() else 0,
                    'valor_total_peca_9': costo_final_9 if 'costo_final_9' in locals() else 0,               
                    'quant_peca_10': quant_peca_10 if 'quant_peca_10' in locals() else None,
                    'desc_peca_10': desc_peca_10 if 'desc_peca_10' in locals() else None,
                    'valor_peca_10': costo_inicial_10 if 'costo_inicial_10' in locals() else 0,
                    'valor_total_peca_10': costo_final_10 if 'costo_final_10' in locals() else 0,                   
                    'quant_peca_11': quant_peca_11 if 'quant_peca_11' in locals() else None,
                    'desc_peca_11': desc_peca_11 if 'desc_peca_11' in locals() else None,
                    'valor_peca_11': costo_inicial_11 if 'costo_inicial_11' in locals() else 0,
                    'valor_total_peca_11': costo_final_11 if 'costo_final_11' in locals() else 0,                  
                    'quant_peca_12': quant_peca_12 if 'quant_peca_12' in locals() else None,
                    'desc_peca_12': desc_peca_12 if 'desc_peca_12' in locals() else None,
                    'valor_peca_12': costo_inicial_12 if 'costo_inicial_12' in locals() else 0,
                    'valor_total_peca_12': costo_final_12 if 'costo_final_12' in locals() else 0,             
                    'quant_peca_13': quant_peca_13 if 'quant_peca_13' in locals() else None,
                    'desc_peca_13': desc_peca_13 if 'desc_peca_13' in locals() else None,
                    'valor_peca_13': costo_inicial_13 if 'costo_inicial_13' in locals() else 0,
                    'valor_total_peca_13': costo_final_13 if 'costo_final_13' in locals() else 0,                   
                    'quant_peca_14': quant_peca_14 if 'quant_peca_14' in locals() else None,
                    'desc_peca_14': desc_peca_14 if 'desc_peca_14' in locals() else None,
                    'valor_peca_14': costo_inicial_14 if 'costo_inicial_14' in locals() else 0,
                    'valor_total_peca_14': costo_final_14 if 'costo_final_14' in locals() else 0,          
                    'quant_peca_15': quant_peca_15 if 'quant_peca_15' in locals() else None,
                    'desc_peca_15': desc_peca_15 if 'desc_peca_15' in locals() else None,
                    'valor_peca_15': costo_inicial_15 if 'costo_inicial_15' in locals() else 0,
                    'valor_total_peca_15': costo_final_15 if 'costo_final_15' in locals() else 0,
                    'quant_peca_16': quant_peca_16 if 'quant_peca_16' in locals() else None,
                    'desc_peca_16': desc_peca_16 if 'desc_peca_16' in locals() else None,
                    'valor_peca_16': costo_inicial_16 if 'costo_inicial_16' in locals() else 0,
                    'valor_total_peca_16': costo_final_16 if 'costo_final_16' in locals() else 0,
                    'total_costo_inicial': sum([v for k, v in locals().items() if k.startswith('costo_inicial_')]),
                    'total_costo_final': sum([v for k, v in locals().items() if k.startswith('costo_final_')]),
                    'forma_de_pagamento': None,
                    'pagamento_parcial': None,
                    'valor_pago_parcial': None,
                    'data_prox_pag': None,
                    'valor_prox_pag': None,
                    'pag_total': None,
                    'valor_pag_total': None
                }
                # Convertir el registro actualizado a DataFrame
                updated_record_df = pd.DataFrame([updated_record])

               # Actualizar el DataFrame existente
                existing_data.loc[existing_data["user_id"] == vendor_to_update, updated_record_df.columns] = updated_record_df.values
                
                try:
                    # Obtener la hoja de cálculo
                    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
                  
                    # Encontrar la fila que corresponde al user_id que se está actualizando
                    cell = worksheet.find(str(vendor_to_update))
                    row_index = cell.row

                    # Actualizar solo la fila correspondiente
                    worksheet.update(f"A{row_index}", [updated_record_df.values.tolist()[0]])
                    
                    st.success("Ordem de serviço atualizada com sucesso")
                
                except Exception as e:
                    st.error(f"Erro ao atualizar planilha: {str(e)}")

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
