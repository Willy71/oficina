# 2_Consultar_carro.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------------------
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

# Título de la página
st.title("🔍 Consultar Veículo por Placa")

# ----------------------------------------------------------------------------------------------------------------------------------
# Conexión a Google Sheets (mismo método que usas)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'
SHEET_NAME = 'Hoja 1'

# Cargar credenciales y autorizar
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

def cargar_datos():
    try:
        worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        # Reemplazar NaN con cadena vacía
        df = df.fillna("")
        
        # Asegurar que la columna 'placa' existe y tiene datos
        if 'placa' not in df.columns:
            st.error("A coluna 'placa' não foi encontrada na planilha.")
            return pd.DataFrame()
            
        # Limpiar datos - reemplazar strings vacíos con NaN
        df.replace('', np.nan, inplace=True)
        return df
    except Exception as e:
        st.error(f"Erro ao cargar dados: {str(e)}")
        return pd.DataFrame()

# Cargar datos
dados = cargar_datos()

# ----------------------------------------------------------------------------------------------------------------------------------
# Función para buscar vehículo por placa
def buscar_por_placa(placa, df):
    if df.empty:
        return None
    
    # Buscar coincidencias exactas (ignorando mayúsculas/minúsculas y espacios)
    resultado = df[df['placa'].astype(str).str.upper().str.strip() == placa.upper().strip()]
    
    if not resultado.empty:
        return resultado.iloc[0].to_dict()
    return None

# ----------------------------------------------------------------------------------------------------------------------------------
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
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("Placa", veiculo.get('placa', 'N/A'))
                    with cols[1]:
                        st.metric("Marca", veiculo.get('carro', 'N/A'))
                    with cols[2]:
                        st.metric("Modelo", veiculo.get('modelo', 'N/A'))
                    with cols[3]:
                        st.metric("Ano", veiculo.get('ano', 'N/A'))
                
                # Mostrar detalles del estado y fechas
                with st.container():
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Estado", veiculo.get('estado', 'N/A'))
                    with cols[1]:
                        st.metric("Data Entrada", veiculo.get('date_in', 'N/A'))
                    with cols[2]:
                        st.metric("Previsão Entrega", veiculo.get('date_prev', 'N/A'))
                
                # Mostrar información del dueño
                with st.container():
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Proprietário", veiculo.get('dono_empresa', 'N/A'))
                    with cols[1]:
                        st.metric("Telefone", veiculo.get('telefone', 'N/A'))
                    with cols[2]:
                        st.metric("Endereço", veiculo.get('endereco', 'N/A'))
                
                             # Función para formatear valores numéricos
                def formatar_valor(valor):
                    try:
                        # Convertir a float, redondear a 2 decimales y formatear con coma como separador decimal
                        valor_float = float(valor)
                        return f"{valor_float:,.2f}".replace(".", "X").replace(",", ".").replace("X", ",")
                    except (ValueError, TypeError):
                        return "0,00"

                # Mostrar servicios con expanders
                with st.expander("📋 Serviços Realizados", expanded=False):
                    servicos = []
                    total_servicos = 0.0
                    
                    for i in range(1, 13):
                        item = veiculo.get(f'item_serv_{i}', '')
                        desc = veiculo.get(f'desc_ser_{i}', '')
                        valor = veiculo.get(f'valor_serv_{i}', '')
                        
                        if pd.notna(item) or pd.notna(desc) or pd.notna(valor):
                            valor_formatado = formatar_valor(valor) if pd.notna(valor) else "0,00"
                            valor_float = float(valor) if pd.notna(valor) else 0.0
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
                
                # Mostrar peças com expanders
                with st.expander("🔧 Peças Utilizadas", expanded=False):
                    pecas = []
                    total_pecas = 0.0
                    
                    for i in range(1, 17):
                        quant = veiculo.get(f'quant_peca_{i}', '')
                        desc = veiculo.get(f'desc_peca_{i}', '')
                        valor = veiculo.get(f'valor_peca_{i}', '')
                        
                        if pd.notna(quant) or pd.notna(desc) or pd.notna(valor):
                            valor_formatado = formatar_valor(valor) if pd.notna(valor) else "0,00"
                            valor_float = float(valor) if pd.notna(valor) else 0.0
                            total_pecas += valor_float
                            
                            pecas.append({
                                'Quant.': quant if pd.notna(quant) else '',
                                'Descrição': desc if pd.notna(desc) else '',
                                'Valor Unit. (R$)': valor_formatado
                            })
                    
                    if pecas:
                        df_pecas = pd.DataFrame(pecas)
                        st.dataframe(df_pecas, hide_index=True, use_container_width=True)
                        
                        # Mostrar total de piezas
                        st.markdown(f"**Total Peças:** R$ {formatar_valor(total_pecas)}")
                    else:
                        st.info("Nenhuma peça registrada")

                # Mostrar el gran total después de ambas secciones
                if 'total_servicos' in locals() and 'total_pecas' in locals():
                    total_geral = total_servicos + total_pecas
                    st.success(f"**TOTAL GERAL (Serviços + Peças):** R$ {formatar_valor(total_geral)}")
                
                # Mostrar todos los datos en formato JSON
                #with st.expander("📄 Ver todos os dados técnicos", expanded=False):
                    #st.json(veiculo)
            else:
                st.warning("Nenhum veículo encontrado com esta placa")
# ----------------------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------------------
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
                st.dataframe(
                    filtrados[['placa', 'carro', 'modelo', 'ano', 'estado']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("Nenhum veículo encontrado com os critérios especificados")
