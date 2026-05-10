#!/bin/sh
# Docker entrypoint: ensure required config files exist on first run

CONFIG_FILE="/app/config.yaml"
DATA_FILE="/app/data.yaml"
CONFIG_EXAMPLE="/app/config.yaml.example"

# Docker bind-mount creates a directory if the host file doesn't exist — clean it up
if [ -d "$CONFIG_FILE" ]; then
    echo "[INIT] Removing empty config.yaml directory created by Docker bind mount..."
    rm -rf "$CONFIG_FILE"
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "[INIT] config.yaml not found, copying from example..."
    cp "$CONFIG_EXAMPLE" "$CONFIG_FILE"
    echo "[INIT] Please edit config.yaml with your Telegram api_id and api_hash"
fi

if [ ! -f "$DATA_FILE" ]; then
    echo "[INIT] Creating empty data.yaml..."
    touch "$DATA_FILE"
fi

exec python -u media_downloader.py "$@"
