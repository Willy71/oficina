# Usar una imagen oficial de Python
FROM python:3.10-slim

# Crear el directorio de trabajo
WORKDIR /app

# Copiar los archivos
COPY . .

# Instalar dependencias
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Exponer el puerto
EXPOSE 8080

# Comando de ejecución
CMD ["streamlit", "run", "Home.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false"]
