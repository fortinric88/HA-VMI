#!/bin/bash

# Test script for the addon
# Validates the addon structure and configuration

set -e

ADDON_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "═══════════════════════════════════════════════════════════"
echo "Ventilairsec VMI Monitor - Addon Validation"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check required files
check_file() {
    local file=$1
    local required=$2
    
    if [ -f "$ADDON_DIR/$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        if [ "$required" = "required" ]; then
            echo -e "${RED}✗${NC} $file (REQUIRED)"
            ((ERRORS++))
        else
            echo -e "${YELLOW}⚠${NC} $file"
            ((WARNINGS++))
        fi
    fi
}

echo "Checking required files..."
check_file "addon.json" "required"
check_file "Dockerfile" "required"
check_file "run.sh" "required"
check_file "requirements.txt" "required"
check_file "README.md" "required"
check_file "rootfs/app/main.py" "required"
check_file "rootfs/app/enocean_handler.py" "required"
check_file "rootfs/app/data_parser.py" "required"
check_file "rootfs/app/database.py" "required"
check_file "rootfs/app/templates/index.html" "required"
check_file ".gitignore" "optional"
check_file "TECHNICAL.md" "optional"
check_file "DEVELOPER.md" "optional"
check_file "repository.json" "optional"

echo ""
echo "Checking JSON validity..."

# Check addon.json
if python3 -m json.tool "$ADDON_DIR/addon.json" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} addon.json is valid JSON"
else
    echo -e "${RED}✗${NC} addon.json is invalid JSON"
    ((ERRORS++))
fi

# Check repository.json if exists
if [ -f "$ADDON_DIR/repository.json" ]; then
    if python3 -m json.tool "$ADDON_DIR/repository.json" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} repository.json is valid JSON"
    else
        echo -e "${RED}✗${NC} repository.json is invalid JSON"
        ((ERRORS++))
    fi
fi

echo ""
echo "Checking Python code quality..."

# Check Python syntax
for py_file in "$ADDON_DIR"/rootfs/app/*.py; do
    if python3 -m py_compile "$py_file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $(basename "$py_file") - OK"
    else
        echo -e "${RED}✗${NC} $(basename "$py_file") - Syntax error"
        ((ERRORS++))
    fi
done

echo ""
echo "Checking Docker configuration..."

# Check Dockerfile
if grep -q "FROM" "$ADDON_DIR/Dockerfile"; then
    echo -e "${GREEN}✓${NC} Dockerfile has FROM statement"
else
    echo -e "${RED}✗${NC} Dockerfile missing FROM statement"
    ((ERRORS++))
fi

if grep -q "ENTRYPOINT\|CMD" "$ADDON_DIR/Dockerfile"; then
    echo -e "${GREEN}✓${NC} Dockerfile has entry point"
else
    echo -e "${YELLOW}⚠${NC} Dockerfile may be missing entry point"
    ((WARNINGS++))
fi

echo ""
echo "Checking run.sh..."

if grep -q "python3 main.py" "$ADDON_DIR/run.sh"; then
    echo -e "${GREEN}✓${NC} run.sh calls main.py"
else
    echo -e "${YELLOW}⚠${NC} run.sh may not call main.py correctly"
    ((WARNINGS++))
fi

echo ""
echo "Checking requirements.txt..."

required_packages=(
    "flask"
    "flask-cors"
    "requests"
    "python-enocean"
)

for package in "${required_packages[@]}"; do
    if grep -q "$package" "$ADDON_DIR/requirements.txt"; then
        echo -e "${GREEN}✓${NC} $package found"
    else
        echo -e "${YELLOW}⚠${NC} $package not found in requirements.txt"
        ((WARNINGS++))
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Validation Results"
echo "═══════════════════════════════════════════════════════════"
echo -e "Errors:   ${RED}$ERRORS${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Addon structure is valid!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Test locally: ./deploy.sh"
    echo "2. Push to GitHub"
    echo "3. Add repository to Home Assistant"
    exit 0
else
    echo -e "${RED}✗ Addon validation failed!${NC}"
    echo "Please fix the errors above."
    exit 1
fi
