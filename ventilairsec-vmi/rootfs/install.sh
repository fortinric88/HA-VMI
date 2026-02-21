#!/bin/bash

# Installation script for the addon
# Executed during addon installation

set -e

echo "Installing Ventilairsec VMI Monitor addon..."

# Install system dependencies if needed
if command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y --no-install-recommends \
        python3-dev \
        gcc \
        libffi-dev
fi

echo "✓ Installation complete"
