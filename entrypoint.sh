#!/bin/sh
set -e

mkdir -p /app/.streamlit

# Si la variable de entorno SECRETS_TOML contiene credenciales, crear el archivo
if [ -n "$SECRETS_TOML" ]; then
    printf "%s\n" "$SECRETS_TOML" > /app/.streamlit/secrets.toml
fi

# Iniciar la aplicación Streamlit
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0
