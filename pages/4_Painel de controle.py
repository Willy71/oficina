# 3_Dashboard.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuración de página (manteniendo tu estilo)
st.set_page_config(page_title="Dashboard Vehículos", page_icon="📊", layout="wide")
st.html("""<style>div[data-testid="stAppViewBlockContainer"]{padding-top:30px;}</style>""")
st.markdown(f"""<style>[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://i.postimg.cc/jdtSsJ9t/jr-korpa-H-BJWTh-ZRok-unsplash.jpg");
background-size: 180%; background-position: top left; background-repeat: repeat; 
background-attachment: local;}}</style>""", unsafe_allow_html=True)

# Conexión a Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPES)
gc = gspread.authorize(creds)

@st.cache_data(ttl=600)
def load_data():
    try:
        worksheet = gc.open_by_key('1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4').worksheet('Hoja 1')
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        
        # Conversión y formateo de fechas
        df['date_in'] = pd.to_datetime(df['date_in'], dayfirst=True, errors='coerce')  # día/mes/año
        df['date_prev'] = pd.to_datetime(df['date_prev'], dayfirst=True, errors='coerce')
        df['date_out'] = pd.to_datetime(df['date_out'], dayfirst=True, errors='coerce')
        
        # Filtrar solo vehículos activos (ajusta según tus criterios)
        df = df[df['date_out'].isna() | (df['estado'] != 'Entregado')]
        
        return df.sort_values('date_in', ascending=False)
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

# Título y carga de datos
st.title("📊 Painel de Controle de Veículos")
data = load_data()

if data.empty:
    st.warning("Nenhum dado do veículo encontrado")
else:
    # Sidebar con filtros mejorados
    with st.sidebar:
        st.header("Filtros")
        
        # Filtro por estado con conteo
        estados = data['estado'].value_counts().index.tolist()
        estado_opciones = ["Todos"] + estados
        estado_seleccion = st.selectbox(
            "Estado del vehículo",
            estado_opciones,
            format_func=lambda x: f"{x} ({len(data[data['estado']==x])})" if x != 'Todos' else x
        )
        
        # Filtro por fechas con valores por defecto
        min_date, max_date = data['date_in'].min().date(), data['date_in'].max().date()
        fecha_rango = st.date_input(
            "Rango de ingreso",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY"
        )
        
        # Búsqueda rápida
        placa_busqueda = st.text_input("Pesquisar por placa")

    # Aplicar filtros
    filtered_data = data.copy()
    
    if estado_seleccion != "Todos":
        filtered_data = filtered_data[filtered_data['estado'] == estado_seleccion]
    
    if len(fecha_rango) == 2:
        filtered_data = filtered_data[
            (filtered_data['date_in'].dt.date >= fecha_rango[0]) & 
            (filtered_data['date_in'].dt.date <= fecha_rango[1])
        ]
    
    if placa_busqueda:
        filtered_data = filtered_data[
            filtered_data['placa'].str.contains(placa_busqueda, case=False)
        ]

    # Función para formatear fechas
    def format_date(date_series):
        return date_series.dt.strftime('%d/%m/%Y').replace('NaT', '')
    
    # Mostrar conteo real
    st.markdown(f"**Veículos mostrados:** {len(filtered_data)} de {len(data)} totales")
    
    # Métricas resumidas
    st.subheader("Resumo Geral")
    cols = st.columns(5)
    metricas = [
        ("🚗 Total", len(data)),
        ("⏳ Pendientes", len(data[data['estado'] == "Em orçamento")),
        ("🛠️ Reparación", len(data[data['estado'] == "Em reparação")),
        ("✅ Listos", len(data[data['estado'] == "Concluido")),
        ("📅 Hoy", len(data[data['date_in'].dt.date == datetime.today().date()]))
    ]
    
    for col, (label, value) in zip(cols, metricas):
        col.metric(label, value)

    # Pestañas por estado con formato mejorado
    tabs = st.tabs(["📋 Todos", "⏳ Pendentes", "🛠️ Reparação", "✅ Prontos"])
    
    with tabs[0]:  # Todos
        show_data = filtered_data[['date_in', 'placa', 'carro', 'modelo', 'ano', 'estado', 'dono_empresa']].copy()
        show_data['date_in'] = format_date(show_data['date_in'])
        st.dataframe(
            show_data,
            column_config={
                "date_in": "Ingreso (D/M/A)",
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
        show_data = pendientes[['date_in', 'placa', 'carro', 'modelo', 'dono_empresa', 'date_prev']].copy()
        show_data['date_in'] = format_date(show_data['date_in'])
        show_data['date_prev'] = format_date(show_data['date_prev'])
        st.dataframe(
            show_data,
            column_config={
                "date_in": "Ingreso (D/M/A)",
                "placa": "Placa",
                "carro": "Marca",
                "modelo": "Modelo",
                "dono_empresa": "Cliente",
                "date_prev": "Previsto (D/M/A)"
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tabs[2]:  # En Reparación
        en_reparacion = filtered_data[filtered_data['estado'] == "Em reparação"]
        show_data = en_reparacion[['date_in', 'placa', 'carro', 'modelo', 'dono_empresa', 'date_prev']].copy()
        show_data['date_in'] = format_date(show_data['date_in'])
        show_data['date_prev'] = format_date(show_data['date_prev'])
        st.dataframe(
            show_data,
            hide_index=True,
            use_container_width=True
        )
    
    with tabs[3]:  # Listos
        listos = filtered_data[filtered_data['estado'] == "Concluido"]
        show_data = listos[['date_in', 'placa', 'carro', 'modelo', 'dono_empresa', 'date_out']].copy()
        show_data['date_in'] = format_date(show_data['date_in'])
        show_data['date_out'] = format_date(show_data['date_out'])
        st.dataframe(
            show_data,
            column_config={
                "date_out": "Terminado (D/M/A)"
            },
            hide_index=True,
            use_container_width=True
        )
    
    # Gráfico mejorado
    st.subheader("Distribuição por Estado")
    estado_counts = data['estado'].value_counts()
    st.bar_chart(estado_counts)
