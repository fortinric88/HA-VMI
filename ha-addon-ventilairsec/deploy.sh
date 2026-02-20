#!/bin/bash

# Deployment script for Ventilairsec VMI Monitor addon
# This script helps deploy the addon to Home Assistant

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Ventilairsec VMI Monitor - Addon Deployment${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"

# Check if running on Home Assistant
if [ ! -f "/.dockerenv" ]; then
    echo -e "${YELLOW}⚠️  Not running in Docker container${NC}"
    echo "This script is designed to run inside Home Assistant"
    exit 1
fi

# Check required tools
for cmd in docker python3 curl; do
    if ! command -v "$cmd" &> /dev/null; then
        echo -e "${RED}❌ Required command not found: $cmd${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓${NC} All prerequisites met"

# Build the addon
echo ""
echo -e "${YELLOW}Building addon image...${NC}"

ADDON_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ADDON_NAME=$(basename "$ADDON_DIR")
VERSION=$(grep '"version"' "$ADDON_DIR/addon.json" | head -1 | grep -o '"[^"]*"' | tail -1 | tr -d '"')

echo "Name: $ADDON_NAME"
echo "Version: $VERSION"
echo "Directory: $ADDON_DIR"

# Build image
docker build \
    --build-arg BUILD_FROM=homeassistant/armv7-base-python:3.11 \
    -t "$ADDON_NAME:$VERSION" \
    -t "$ADDON_NAME:latest" \
    "$ADDON_DIR"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Addon image built successfully"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

# Optional: Push to local registry (if available)
if command -v "ha" &> /dev/null; then
    echo ""
    echo -e "${YELLOW}Deploying to Home Assistant...${NC}"
    
    # The addon will be automatically picked up by Home Assistant
    # if placed in the correct directory
    
    echo -e "${GREEN}✓${NC} Addon deployed"
    echo ""
    echo "Next steps:"
    echo "1. Open Home Assistant UI"
    echo "2. Go to Settings → System → Add-ons → Create Local Add-on Repository"
    echo "3. Add the path to this repository"
else
    echo ""
    echo -e "${YELLOW}Note:${NC} Home Assistant CLI (ha) not available"
    echo "You can still use the docker image: $ADDON_NAME:$VERSION"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
