#!/bin/bash

# POS System Installer for Linux/Mac
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Restaurant POS System Installer${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher from https://python.org"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo -e "${RED}Error: Python 3.8 or higher is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
python3 -m venv pos-venv
source pos-venv/bin/activate

# Install requirements
echo -e "${BLUE}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create data directory
mkdir -p data

echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""
echo -e "${BLUE}To start the POS system:${NC}"
echo "  source pos-venv/bin/activate"
echo "  python app.py"
echo ""
echo -e "${BLUE}Or run directly:${NC}"
echo "  ./run.sh"
echo ""
echo -e "${BLUE}Default login PIN: 0000 (Admin)${NC}"