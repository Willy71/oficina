import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuración
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SPREADSHEET_KEY = '1kiXS0qeiCpWcNpKI-jmbzVgiRKrxlec9t8YQLDaqwU4'
SHEET_NAME = 'stock'

columnas_ordenadas = ['id_prod', 'quant', 'descripcao', 'carro_peca', 'marca', 'codigo_fab', 'custo', 'porcentagem', 'valor_final']

# Autenticación y carga de hoja
def autenticar_gspread():
    credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    cliente = gspread.authorize(credentials)
    return cliente

def inicializar_hoja():
    try:
        cliente = autenticar_gspread()
        spreadsheet = cliente.open_by_key(SPREADSHEET_KEY)
        try:
            worksheet = spreadsheet.worksheet(SHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=100, cols=20)
            worksheet.append_row(columnas_ordenadas)
        return worksheet
    except Exception as e:
        st.error(f"Erro ao acessar planilha: {str(e)}")
        return None

def cargar_datos_desde_gsheet():
    worksheet = inicializar_hoja()
    if worksheet:
        try:
            # get_all_records devuelve una lista de diccionarios (sí es cacheable)
            records = worksheet.get_all_records()
            if not records:
                return pd.DataFrame(columns=columnas_ordenadas)
            else:
                return pd.DataFrame(records)
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            return pd.DataFrame(columns=columnas_ordenadas)
    else:
        return pd.DataFrame(columns=columnas_ordenadas)

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

columnas_ordenadas = [
    "id_prod", "quant", "descripcao", "carro_peca", "marca",
    "codigo_fab", "custo", "porcentagem", "valor_final"
]
# ---------------- INTERFAZ ----------------
st.title("📦 Controle de Estoque")

df = cargar_datos_desde_gsheet()

# Filtro por descrição ou código
filtro = st.text_input("🔍 Buscar por descrição ou código:")
if filtro:
    df_filtrado = df[df['descripcao'].str.contains(filtro, case=False, na=False) |
                     df['codigo_fab'].astype(str).str.contains(filtro)]
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
else:
    st.dataframe(df, use_container_width=True, hide_index=True)


# Formulario para adicionar novo produto
with st.expander("➕ Adicionar novo produto"):
    with st.form("form_novo_produto"):
        df2 = cargar_datos_desde_gsheet()
        id_prod = obtener_proximo_id(df2)
        quant = st.number_input("Quantidade", min_value=0, step=1)
        descripcao = st.text_input("Descrição")
        carro_peca = st.text_input("Carro / Peça")
        marca = st.text_input("Marca")
        codigo_fab = st.text_input("Código de Fabricante")
        custo = st.number_input("Custo (R$)", min_value=0.0, step=0.1)
        porcentagem = st.number_input("Margem (%)", min_value=0.0, max_value=100.0, step=0.1)
        valor_final = round(custo + (custo * porcentagem / 100), 2)

        st.markdown(f"💰 **Valor Final sugerido:** R$ {valor_final:.2f}")

        submitted = st.form_submit_button("Salvar")
        if submitted:
            nova_linha = [id_prod, quant, descripcao, carro_peca, marca, codigo_fab, custo, porcentagem, valor_final]
            try:
                worksheet = inicializar_hoja()
                worksheet.append_row(nova_linha)
                st.success("✅ Produto adicionado com sucesso!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erro ao adicionar produto: {str(e)}")

# ---------------- VENTAS ----------------
st.markdown("---")
st.header("🛒 Registrar Venda")

if not df.empty:
    # Ordenar el DataFrame por 'descripcao'
    #df_ordenado = df.sort_values(by="descripcao", ascending=True)
    # Crear la lista desplegable a partir del DataFrame ya ordenado
    produtos = df['descripcao'] + " | Código: " + df['id_prod'].astype(str)
    #produtos = df_ordenado['descripcao'] + " | Código: " + df['id_prod'].astype(str)
    produto_escolhido = st.selectbox("Produto", produtos)
    
 

    qtd_vendida = st.number_input("Quantidade Vendida", min_value=1, step=1)

    if st.button("Registrar Venda"):
        try:
            # Identificar ID do produto
            id_escolhido = produto_escolhido.split(" | Código: ")[1]
            
            # Encontrar a linha do produto na planilha
            worksheet = inicializar_hoja()  # Re-obtener worksheet por si expiró
            celda_id = worksheet.find(id_escolhido)
            linha = celda_id.row

            # Obtener valor actual da coluna "quant"
            idx_quant = columnas_ordenadas.index("quant") + 1  # +1 por ser 1-based en Sheets
            quant_atual = int(worksheet.cell(linha, idx_quant).value)

            if qtd_vendida > quant_atual:
                st.warning("⚠️ Estoque insuficiente para esta venda.")
            else:
                nova_quant = quant_atual - qtd_vendida
                worksheet.update_cell(linha, idx_quant, nova_quant)
                st.success(f"✅ Venda registrada! Novo estoque: {nova_quant}")
                st.experimental_rerun()

        except Exception as e:
            st.error(f"Erro ao registrar venda: {str(e)}")
else:
    st.info("ℹ️ Nenhum produto disponível para venda.")

