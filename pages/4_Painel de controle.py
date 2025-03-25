# 3_Dashboard.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Dashboard Vehículos",
    page_icon="📊",
    layout="wide"
)

# Estilos (igual que en tus otras páginas)
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

# Conexión a Google Sheets (igual que en tus otras páginas)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'
SHEET_NAME = 'Hoja 1'

credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

@st.cache_data(ttl=600)  # Cache por 10 minutos
def load_data():
    try:
        worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        
        # Limpieza y conversión de datos
        df['date_in'] = pd.to_datetime(df['date_in'], errors='coerce')
        df = df.dropna(subset=['date_in'])
        
        # Ordenar por fecha de ingreso (más reciente primero)
        df = df.sort_values('date_in', ascending=False)
        
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

# Título del dashboard
st.title("📊 Dashboard de Vehículos en Taller")

# Cargar datos
data = load_data()

if data.empty:
    st.warning("No se encontraron datos de vehículos")
else:
    # Filtros en sidebar
    st.sidebar.header("Filtros")
    
    # Filtro por estado
    estados_disponibles = ["Todos"] + sorted(data['estado'].dropna().unique().tolist())
    estado_seleccionado = st.sidebar.selectbox("Estado del vehículo", estados_disponibles)
    
    # Filtro por fecha
    min_date = data['date_in'].min().date()
    max_date = data['date_in'].max().date()
    fecha_inicio, fecha_fin = st.sidebar.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Aplicar filtros
    filtered_data = data.copy()
    
    if estado_seleccionado != "Todos":
        filtered_data = filtered_data[filtered_data['estado'] == estado_seleccionado]
    
    filtered_data = filtered_data[
        (filtered_data['date_in'].dt.date >= fecha_inicio) & 
        (filtered_data['date_in'].dt.date <= fecha_fin)
    ]
    
    # Mostrar métricas generales
    st.subheader("Resumen General")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Vehículos en Taller", len(data))
    with col2:
        st.metric("Pendientes Orçamento", len(data[data['estado'] == "Em orçamento"]))
    with col3:
        st.metric("En Reparación", len(data[data['estado'] == "Em reparação"]))
    with col4:
        st.metric("Listos para Entrega", len(data[data['estado'] == "Concluido"]))
    
    # Mostrar datos por estado en tabs
    st.subheader("Detalle por Estado")
    
    tabs = st.tabs(["📋 Todos", "⏳ Pendientes", "🛠️ En Reparación", "✅ Listos", "🚗 Entregados"])
    
    with tabs[0]:  # Todos
        st.dataframe(
            filtered_data[['date_in', 'placa', 'carro', 'modelo', 'ano', 'estado', 'dono_empresa']],
            column_config={
                "date_in": "Fecha Ingreso",
                "placa": "Placa",
                "carro": "Marca",
                "modelo": "Modelo",
                "ano": "Año",
                "estado": "Estado",
                "dono_empresa": "Cliente"
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tabs[1]:  # Pendientes
        pendientes = filtered_data[filtered_data['estado'] == "Em orçamento"]
        st.dataframe(
            pendientes[['date_in', 'placa', 'carro', 'modelo', 'dono_empresa', 'date_prev']],
            column_config={
                "date_in": "Fecha Ingreso",
                "placa": "Placa",
                "carro": "Marca",
                "modelo": "Modelo",
                "dono_empresa": "Cliente",
                "date_prev": "Fecha Prevista"
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tabs[2]:  # En Reparación
        en_reparacion = filtered_data[filtered_data['estado'] == "Em reparação"]
        st.dataframe(
            en_reparacion[['date_in', 'placa', 'carro', 'modelo', 'dono_empresa', 'date_prev']],
            hide_index=True,
            use_container_width=True
        )
    
    with tabs[3]:  # Listos
        listos = filtered_data[filtered_data['estado'] == "Concluido"]
        st.dataframe(
            listos[['date_in', 'placa', 'carro', 'modelo', 'dono_empresa', 'date_out']],
            column_config={
                "date_out": "Fecha Terminado"
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tabs[4]:  # Entregados
        entregados = filtered_data[filtered_data['estado'] == "Entregado"]
        st.dataframe(
            entregados[['date_in', 'placa', 'carro', 'modelo', 'dono_empresa', 'date_out']],
            column_config={
                "date_out": "Fecha Entrega"
            },
            hide_index=True,
            use_container_width=True
        )
    
    # Gráfico de distribución por estado
    st.subheader("Distribución por Estado")
    estado_counts = data['estado'].value_counts()
    st.bar_chart(estado_counts)
