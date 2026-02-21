#!/bin/bash

set -e

# Configuration
CONFIG_PATH=/config/ventilairsec
ADDON_PATH=/app

# Create necessary directories
mkdir -p "$CONFIG_PATH"/logs
mkdir -p "$CONFIG_PATH"/db

# Copy default configs if they don't exist
if [ ! -f "$CONFIG_PATH/config.json" ]; then
    cp "$ADDON_PATH/rootfs/app/config.default.json" "$CONFIG_PATH/config.json"
fi

# Start the main application
cd "$ADDON_PATH/rootfs/app"
python3 main.py --config "$CONFIG_PATH/config.json" --db "$CONFIG_PATH/db" --logs "$CONFIG_PATH/logs"
