#!/bin/sh
set -e

mkdir -p /app/.streamlit

# Si viene en Base64 (1 sola linea limpia para .env)
if [ -n "$SECRETS_BASE64" ]; then
    echo "$SECRETS_BASE64" | base64 -d > /app/.streamlit/secrets.toml
elif [ -n "$SECRETS_TOML" ]; then
    printf "%s\n" "$SECRETS_TOML" > /app/.streamlit/secrets.toml
fi

exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0

