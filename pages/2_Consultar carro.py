# 2_Consultar_carro.py
import pdfkit
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
from datetime import datetime

#====================================================================================================================================================
# Configuración de página (igual que tu código original)
st.set_page_config(
    page_title="Consultar Veículo",
    page_icon="🚗",
    layout="wide"
)

# Estilos CSS (copiados de tu código original)
reduce_space = """
<style type="text/css">
div[data-testid="stAppViewBlockContainer"]{
    padding-top:30px;
}
</style>
"""
st.markdown(reduce_space, unsafe_allow_html=True)

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://github.com/Willy71/oficina/blob/main/pictures/wallpaper%20black%20vintage.jpg?raw=true");
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

# Título de la página
st.title("🔍 Consultar Veículo por Placa")

##====================================================================================================================================================
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
credenciales_json = credentials


def autenticar_gspread():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    cliente = gspread.authorize(credentials)
    return cliente

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


# Función para buscar vehículo por placa
def buscar_por_placa(placa, df):
    if df.empty:
        return None
    
    # Buscar coincidencias exactas (ignorando mayúsculas/minúsculas y espacios)
    resultado = df[df['placa'].astype(str).str.upper().str.strip() == placa.upper().strip()]
    
    if not resultado.empty:
        return resultado.iloc[-1].to_dict()  # Tomar el último ingreso en lugar del primero
    return None
#====================================================================================================================================================

def safe_float(valor):
    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        return 0.0

def formatar_valor(valor, padrao=""):
    """
    Formatea valores para visualización segura
    
    Args:
        valor: Valor a formatear (str, float, int, None)
        padrao: Valor por defecto si no se puede formatear (default: "")
    
    Returns:
        str: Valor formateado o string vacío si es nulo/inválido
    """
    if pd.isna(valor) or valor in [None, '']:
        return padrao
    try:
        return str(valor).strip()
    except:
        return padrao

def formatar_real(valor, padrao="0,00"):
    """
    Formata valores para el estándar monetario brasileño (R$ 0,00)
    
    Args:
        valor: Valor a formatear (str, float, int o None)
        padrao: Valor por defecto si no se puede formatear (default: "0,00")
    
    Returns:
        str: Valor formateado con coma decimal (ej. "1.234,56")
    """
    try:
        # Convierte a string y limpia
        str_valor = str(valor).strip()
        
        # Verifica valores vacíos o inválidos
        if not str_valor or str_valor.lower() in ['nan', 'none', 'null', '']:
            return padrao
            
        # Reemplaza comas por puntos para conversión a float
        str_valor = str_valor.replace('.', '').replace(',', '.')
        
        # Formatea con 2 decimales y comas como separador decimal
        valor_float = float(str_valor)
        return f"{valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    except (ValueError, TypeError, AttributeError):
        return padrao
#====================================================================================================================================================
# Inicializar la hoja de cálculo
worksheet = inicializar_hoja()

# Cargar datos
dados = cargar_datos(worksheet)

env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
template = env.get_template("template_2.html")

#====================================================================================================================================================
# Inicialización (al inicio del script, fuera de cualquier función)
if 'veiculo' not in st.session_state:
    st.session_state.veiculo = None
    
# Interfaz de usuario
with st.container():
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        placa = st.text_input("Digite a placa do veículo:", "", key="placa_input").strip().upper()
    with col2:
        st.write("")  # Espaciador
        buscar = st.button("Buscar Veículo", key="buscar_btn")

if buscar:
    if not placa:
        st.warning("Por favor, digite uma placa para buscar")
    else:
        with st.spinner("Buscando veículo..."):
            veiculo = buscar_por_placa(placa, dados)
            
            if veiculo:
                st.success("✅ Veículo encontrado!")
                
                # Mostrar información principal en cards
                with st.container():
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Marca", formatar_valor(veiculo.get('carro')))
                    with cols[1]:
                        st.metric("Modelo", formatar_valor(veiculo.get('modelo')))
                    with cols[2]:
                        ano = veiculo.get('ano')
                        if isinstance(ano, float):
                            ano = int(ano)
                        st.metric("Ano", formatar_valor(ano))
                
                # Mostrar detalles del estado y fechas
                with st.container():
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Estado", formatar_valor(veiculo.get('estado')))
                    with cols[1]:
                        st.metric("Data Entrada", formatar_valor(veiculo.get('date_in')))
                    with cols[2]:
                        st.metric("Previsão Entrega", formatar_valor(veiculo.get('date_prev')))
                
                # Mostrar información del dueño
                with st.container():
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Proprietário", formatar_valor(veiculo.get('dono_empresa')))
                    with cols[1]:
                        st.metric("Telefone", formatar_valor(veiculo.get('telefone')))
                    with cols[2]:
                        st.metric("Endereço", formatar_valor(veiculo.get('endereco')))
#===================================================================================================================================================================
                with st.expander("📋 Serviços Realizados", expanded=False):
                    servicos = []
                    total_servicos = 0.0
                
                    for i in range(1, 13):
                        item = veiculo.get(f'item_serv_{i}', '')
                        desc = veiculo.get(f'desc_ser_{i}', '')
                        valor = veiculo.get(f'valor_serv_{i}', '')
                
                        if pd.notna(item) and pd.notna(desc) and pd.notna(valor):  # Filtrar solo los servicios con datos
                            valor_formatado = formatar_real(valor)
                            valor_float = safe_float(valor) if pd.notna(valor) else 0.0
                            total_servicos += valor_float
                
                            servicos.append({
                                'Item': item if pd.notna(item) else '',
                                'Descrição': desc if pd.notna(desc) else '',
                                'Valor (R$)': valor_formatado
                            })
                
                    if servicos:
                        df_servicos = pd.DataFrame(servicos)
                        st.dataframe(df_servicos, hide_index=True, use_container_width=True)
                        
                        # Mostrar total de servicios
                        st.markdown(f"**Total Serviços:** R$ {formatar_valor(total_servicos)}")
                    else:
                        st.info("Nenhum serviço registrado")

#==============================================================================================================================================================


                # Mostrar peças con expanders
                with st.expander("🔧 Peças Utilizadas", expanded=False):
                    pecas = []
                    total_pecas = 0.0
                    total_pecas_final = 0.0
                    
                    for i in range(1, 17):
                        quant = veiculo.get(f'quant_peca_{i}', '')  # Cantidad
                        desc = veiculo.get(f'desc_peca_{i}', '')  # Descripción
                        valor = veiculo.get(f'valor_peca_{i}', '')  # Costo unitario
                        porcentaje = veiculo.get('porcentaje_adicional', 0)  # Porcentaje adicional

                        if pd.notna(quant) and pd.notna(desc) and pd.notna(valor):  
                            quant_float = safe_float(quant)
                            valor_float = safe_float(valor)
                            # Calcular el costo total de la pieza
                            valor_total_peca = quant_float * valor_float     
                            # Aplicar el porcentaje adicional
                            valor_total_final = valor_total_peca * (1 + safe_float(porcentaje) / 100)           
                            total_pecas += valor_total_peca  # Sumar costo total de piezas (sin adicional)
                            total_pecas_final += valor_total_final  # Sumar costo final con adicional
                            
                            pecas.append({
                                'Quant.': quant if pd.notna(quant) else '',
                                'Descrição': desc if pd.notna(desc) else '',
                                'Custo Unit. (R$)': formatar_valor_br(
                                    valor,
                                    decimal_places=2,
                                    padrao="0,00"
                                ),
                                '% Adicional': f"{porcentaje}%" if pd.notna(porcentaje) else "0%",
                                'Valor Final (R$)': f"{formatar_valor(valor_total_final):.2f}"
                            })
                    
                    if pecas:
                        df_pecas = pd.DataFrame(pecas)
                        st.dataframe(df_pecas, hide_index=True, use_container_width=True)
                        
                        # Mostrar totales
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Total Costo Peças:** R$ {formatar_valor(total_pecas):.2f}")
                        with col2:
                            st.markdown(f"**Total Final Peças:** R$ {formatar_valor(total_pecas_final):.2f}")
                    else:
                        st.info("Nenhuma peça registrada")
                

                # Mostrar el gran total después de ambas secciones
                if 'total_servicos' in locals() and 'total_pecas' in locals():
                    total_geral = total_servicos + total_pecas_final
                    st.success(f"**TOTAL GERAL (Serviços + Peças):** R$ {formatar_valor(total_geral):.2f}")

# Mostrar resultados y PDF
if st.session_state.veiculo:
    veiculo = st.session_state.veiculo
#===========================================================================================================================================================
    if st.button("Gerar PDF"):
        html = template.render(
            placa=veiculo['placa'],
            carro=veiculo['carro'],
            modelo=veiculo['modelo'],
            ano=veiculo['ano'],
            date_in=veiculo['date_in']
        )
        pdf = pdfkit.from_string(html, False)
        st.download_button(
            "⬇️ Download PDF",
            data=pdf,
            file_name="carro.pdf",
            mime="application/octet-stream"
        )

#==========================================================================================================================================================
# Opción para buscar por otros criterios
with st.expander("🔎 Busca Avançada", expanded=False):
    with st.form(key="busca_avancada"):
        col1, col2 = st.columns(2)
        with col1:
            marca = st.text_input("Marca (opcional)", "")
        with col2:
            modelo = st.text_input("Modelo (opcional)", "")
        
        col3, col4 = st.columns(2)
        with col3:
            estado_options = ["Todos"] + dados['estado'].dropna().unique().tolist() if not dados.empty else []
            estado = st.selectbox("Estado (opcional)", estado_options)
        with col4:
            ano = st.text_input("Ano (opcional)", "")
        
        buscar_avancado = st.form_submit_button("Buscar")
        
        if buscar_avancado:
            filtrados = dados.copy()
            
            if marca:
                filtrados = filtrados[filtrados['carro'].astype(str).str.contains(marca, case=False)]
            if modelo:
                filtrados = filtrados[filtrados['modelo'].astype(str).str.contains(modelo, case=False)]
            if estado and estado != "Todos":
                filtrados = filtrados[filtrados['estado'] == estado]
            if ano:
                filtrados = filtrados[filtrados['ano'].astype(str).str.contains(ano)]
            
            if not filtrados.empty:
                st.success(f"🚙 {len(filtrados)} veículos encontrados")    
                for _, row in filtrados.iterrows():
                    veiculo_str = f"🚗 {row['carro']}    {row['modelo']}        🏷️ {row['placa']}        🎨 {row.get('cor', 'Sem cor')}        📅 Entrada: {row.get('date_in', 'Sem data')}        👤 Dono: {row.get('dono_empresa', 'Desconhecido')}" 
                    st.markdown(f"- {veiculo_str}")
            else:
                st.warning("Nenhum veículo encontrado com os critérios especificados")
