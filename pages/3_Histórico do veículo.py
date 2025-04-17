import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Config página
st.set_page_config(page_title="Histórico do Veículo", page_icon="📋", layout="wide")

# Estilos y fondo oscuro
st.markdown("""
<style>
[data-testid="stAppViewContainer"] > .main {
    background-color: #00001a;
}
[data-testid="stHeader"], [data-testid="stSidebar"] {
    background: rgba(0,0,0,0);
}
[data-testid="stToolbar"] {
    right: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Autenticación y conexión
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'
SHEET_NAME = 'Hoja 1'
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)
worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)

# Funciones
def cargar_datos():
    records = worksheet.get_all_records()
    return pd.DataFrame(records) if records else pd.DataFrame()

def buscar_por_placa(placa, df):
    if df.empty:
        return None
    resultado = df[df['placa'].astype(str).str.upper().str.strip() == placa.upper().strip()]
    if not resultado.empty:
        return resultado
    return pd.DataFrame()

# Inicialización de estado
if "buscar_historico" not in st.session_state:
    st.session_state.buscar_historico = False

st.markdown("<h2 style='color: gold;'>📋 Histórico de Veículo</h2>", unsafe_allow_html=True)

# Interfaz con input + botón
with st.container():
    col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 2])
    with col1:
        placa_input = st.text_input("Digite a placa do veículo:", key="placa_hist_input").strip().upper()
    with col2:
        st.write("")  # Espaciador
        st.write("")  # Espaciador
        buscar = st.button("Buscar", key="buscar_historico_btn")

if buscar:
    st.session_state.buscar_historico = True

# Procesar búsqueda si fue activada
if st.session_state.buscar_historico and placa_input:
    df = cargar_datos()
    historico = buscar_por_placa(placa_input, df)

    if historico.empty:
        st.warning("Nenhum histórico encontrado para essa placa.")
    else:
        historico = historico.sort_values(by="date_in")

        # Mostrar info principal del vehículo
        veiculo = historico.iloc[-1]
        st.markdown(f"""
        <div style='background-color: #262730; padding: 20px; border-radius: 10px;'>
            <h4 style='color: gold;'>🚗 Dados do Veículo</h4>
            <p style='color: white;'>Placa: <strong>{veiculo['placa']}</strong></p>
            <p style='color: white;'>Marca: {veiculo['carro']} | Modelo: {veiculo['modelo']}</p>
            <p style='color: white;'>Ano: {veiculo['ano']} | Cor: {veiculo['cor']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Mostrar historial
        for _, row in historico.iterrows():
            st.markdown(f"""
            <div style='background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h5 style='color: gold;'>🛠️ Visita em {row['date_in']} - Estado: {row['estado']}</h5>
            """, unsafe_allow_html=True)

            st.markdown("<h6 style='color: #00ffcc;'>🔧 Serviços:</h6>", unsafe_allow_html=True)
            for n in range(1, 13):
                desc = row.get(f'desc_ser_{n}')
                val = row.get(f'valor_serv_{n}')
                if desc and str(desc).strip():
                    st.markdown(f"<p style='color:white;'>• {desc} — <strong>R$ {val}</strong></p>", unsafe_allow_html=True)

            st.markdown("<h6 style='color: #00ffcc;'>🧩 Peças utilizadas:</h6>", unsafe_allow_html=True)
            for n in range(1, 17):
                desc = row.get(f'desc_peca_{n}')
                val = row.get(f'valor_total_peca_{n}')
                if desc and str(desc).strip() and val and float(val) > 0:
                    st.markdown(f"<p style='color:white;'>• {desc} — <strong>R$ {val}</strong></p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

#========================================================================================================================================================
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
            estado_options = ["Todos"] + df['estado'].dropna().unique().tolist() if not df.empty else []
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
