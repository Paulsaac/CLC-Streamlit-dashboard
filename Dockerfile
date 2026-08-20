# Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y forzar buffer directo a stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema mínimas requeridas (curl para healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar primero requirements.txt para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Copiar script de arranque y dar permisos
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Exponer el puerto por defecto de Streamlit
EXPOSE 8501

# Healthcheck para verificar que la aplicación esté respondiendo correctamente
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando para iniciar la aplicación Streamlit
ENTRYPOINT ["/app/entrypoint.sh"]

