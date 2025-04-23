import streamlit as st
import pandas as pd
import gspread
import uuid
from google.oauth2.service_account import Credentials
from datetime import datetime
import plotly.express as px

# Conexão com Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SPREADSHEET_KEY = "1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4"
SHEET_NAME = "fluxo"

credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)

def carregar_dados():
    """Carga y limpia los datos de forma robusta"""
    try:
        # Obtener datos crudos
        all_data = sheet.get_all_values()
        
        if len(all_data) < 2:
            return pd.DataFrame(columns=['ids', 'data', 'data_pag', 'cliente', 'descricao', 
                                      'carro', 'placa', 'motivo', 'form', 'valor', 'status'])
        
        # Crear DataFrame
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        
        # Limpieza de valores NA/NaN
        df = df.replace(['', 'NA', 'N/A', 'None', 'null'], pd.NA)
        
        # Conversión segura de valores numéricos
        if 'valor' in df.columns:
            df['valor'] = (
                df['valor']
                .astype(str)
                .str.replace(',', '.', regex=False)
                .apply(pd.to_numeric, errors='coerce')
                .fillna(0)
            )
        
        # Normalización de status
        if 'status' in df.columns:
            df['status'] = (
                df['status']
                .astype(str)
                .str.strip()
                .str.lower()
                .replace({'nan': pd.NA, 'none': pd.NA})
            )
        
        return df
    
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()
        
def adicionar_lancamento(status, data, data_pag, cliente, descricao, carro, placa, motivo, forma, valor):
    """Añade nuevo registro con formato numérico correcto"""
    novo_id = str(uuid.uuid4())
    # Asegurar formato americano para el valor
    valor_americano = float(str(valor).replace(',', ''))
    
    nova_linha = [
        novo_id, 
        str(data),
        str(data_pag) if data_pag else "",
        str(cliente).strip(),
        str(descricao).strip(),
        str(carro).strip(),
        str(placa).strip(),
        str(motivo).strip(),
        str(forma).strip().lower(),
        valor_americano,  # Usamos el valor con punto decimal
        str(status).strip().lower()
    ]
    sheet.append_row(nova_linha)
    return novo_id

def atualizar_linha_por_id(id_alvo, novos_dados):
    df = carregar_dados()
    if id_alvo in df["ids"].values:
        linha = df[df["ids"] == id_alvo].index[0] + 2  # +2 por cabeçalho e índice 0-based
        for i, valor in enumerate(novos_dados):
            sheet.update_cell(linha, i + 1, valor)
        return True
    return False

def excluir_linha_por_id(id_alvo):
    df = carregar_dados()
    if id_alvo in df["ids"].values:
        linha = df[df["ids"] == id_alvo].index[0] + 2
        sheet.delete_rows(linha)
        return True
    return False

def salvar_dados(df):
    sheet.clear()
    sheet.append_row(df.columns.tolist())  # Encabezados
    for _, row in df.iterrows():
        sheet.append_row(row.tolist())

def safe_get(obj, key, default=None):
    """Obtiene valores de forma segura de diccionarios o Series"""
    try:
        if pd.isna(obj.get(key, default)):
            return default
        return obj.get(key, default)
    except:
        return default

def safe_convert(value, to_type=float, default=0):
    """Conversión segura de tipos"""
    try:
        if pd.isna(value):
            return default
        return to_type(value)
    except:
        return default

# Interface
st.set_page_config("Fluxo de Caixa", layout="wide")
st.title("💰 Fluxo de Caixa")

aba1, aba2, aba3, aba4 = st.tabs(["➕ Novo Lançamento", "📋 Lançamentos", "🛠️ Editar / Remover", "📊 Resumo Financeiro"])

with aba1:
    st.subheader("➕ Novo Registro")
    tipo = st.selectbox("Tipo", ["entrada", "saida", "pendente"])
    data = st.date_input("Data do lançamento")
    data_pag = st.date_input("Data de pagamento prevista", value=None) if tipo == "pendente" else None
    cliente = st.text_input("Cliente")
    descricao = st.text_input("Descrição")
    carro = st.text_input("Carro")
    placa = st.text_input("Placa")
    motivo = st.text_input("Motivo")
    forma = st.selectbox("Forma de pagamento", ["dinheiro", "pix", "cartão", "boleto", "outro"])
    
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    if st.button("Salvar Registro"):
        adicionar_lancamento(tipo, data, data_pag, cliente, descricao, carro, placa, motivo, forma, valor)
        st.success("Registro salvo com sucesso!")

with aba2:
    st.subheader("📋 Lançamentos - Con Diagnóstico")
    df = carregar_dados()
    
    if df.empty:
        st.error("No se cargaron datos. Verifique:")
        st.write("1. Que la hoja existe y tiene datos")
        st.write("2. Que la cuenta de servicio tiene permisos")
        st.write("3. Que el ID de la hoja es correcto")
    else:
        # Mostrar DataFrame con formato
        st.dataframe(
            df.style.format({
                'valor': lambda x: f'R$ {x:,.2f}' if pd.notnull(x) else 'N/A'
            }),
            height=500
        )
        
        # Panel de diagnóstico avanzado
        with st.expander("🚨 Diagnóstico Avanzado", expanded=True):
            st.write("### Información de Columnas")
            st.write(f"Columnas encontradas: {list(df.columns)}")
            st.write(f"Tipos de datos: {df.dtypes.to_dict()}")
            
            st.write("### Muestra de Datos")
            st.write("Primera fila:", df.iloc[0].to_dict() if not df.empty else "N/A")
            
            st.write("### Información de Valor")
            if 'valor' in df.columns:
                st.write("Tipo de 'valor':", type(df['valor'].iloc[0]))
                st.write("Valores únicos:", df['valor'].unique()[:5])
                st.write("Estadísticas:")
                st.write(df['valor'].describe())
            else:
                st.error("No existe columna 'valor'")
            
            st.write("### Datos Crudos")
            st.write(st.session_state.get('diagnostico', 'No disponible'))

with aba3:
    st.subheader("🛠️ Editar ou Remover Lançamento")
    
    df = carregar_dados()
    
    if df.empty:
        st.info("Nenhum lançamento encontrado.")
    else:
        # Crear opciones seguras para el selectbox
        opcoes = (
            df['descricao'].fillna('Sem descrição') + " | " +
            df['cliente'].fillna('Sem cliente') + " | " +
            "R$ " + df['valor'].apply(lambda x: f"{x:.2f}") + " | " +
            df['status'].fillna('Sem status')
        )
        
        # Selección con manejo de NA
        escolha = st.selectbox(
            "Selecione um lançamento para editar ou remover:",
            options=opcoes,
            index=0
        )
        
        if escolha and not pd.isna(escolha):  # Verificación segura
            try:
                idx = opcoes[opcoes == escolha].index[0]
                lancamento = df.loc[idx].fillna('')
                
                # Resto del formulario de edición...
                
            except Exception as e:
                st.error(f"Erro ao cargar lançamento: {str(e)}")


with aba4:
    st.subheader("📊 Resumo Financeiro - Con Validación")
    df = carregar_dados()
    
    if df.empty:
        st.error("No hay datos para generar el resumen")
    else:
        # Validación estricta
        if 'valor' not in df.columns:
            st.error("Columna 'valor' no encontrada")
            st.write("Columnas disponibles:", df.columns.tolist())
        elif 'status' not in df.columns:
            st.error("Columna 'status' no encontrada")
        else:
            try:
                # Cálculos protegidos
                df['status'] = df['status'].str.strip().str.lower()
                
                mask_entrada = df['status'] == 'entrada'
                mask_saida = df['status'] == 'saida'
                mask_pendente = df['status'] == 'pendente'
                
                total_entrada = df.loc[mask_entrada, 'valor'].sum()
                total_saida = df.loc[mask_saida, 'valor'].sum()
                total_pendente = df.loc[mask_pendente, 'valor'].sum()
                saldo = total_entrada - total_saida
                
                # Formateo indestructible
                def safe_format(value):
                    try:
                        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    except:
                        return "Formato inválido"
                
                # Mostrar métricas con verificación
                cols = st.columns(4)
                cols[0].metric("🟢 Entradas", safe_format(total_entrada))
                cols[1].metric("🔴 Saídas", safe_format(total_saida))
                cols[2].metric("🟡 Pendentes", safe_format(total_pendente))
                cols[3].metric("💰 Saldo", safe_format(saldo))
                
                # Gráfico con validación
                try:
                    fig_data = pd.DataFrame({
                        'Tipo': ['Entradas', 'Saídas', 'Pendentes'],
                        'Valor': [total_entrada, total_saida, total_pendente]
                    })
                    
                    fig = px.bar(
                        fig_data,
                        x='Tipo',
                        y='Valor',
                        text='Valor',
                        color='Tipo',
                        color_discrete_sequence=['#28a745', '#dc3545', '#ffc107']
                    )
                    fig.update_traces(
                        texttemplate='%{text:.2f}',
                        textposition='outside'
                    )
                    fig.update_layout(
                        title='Resumo Financeiro',
                        xaxis_title='',
                        yaxis_title='Valor (R$)',
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as graph_error:
                    st.error(f"Error al generar gráfico: {str(graph_error)}")
                    
            except Exception as calc_error:
                st.error(f"Error en cálculos: {str(calc_error)}")
                st.write("Estado actual del DataFrame:")
                st.write(df)
