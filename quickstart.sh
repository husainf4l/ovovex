#!/bin/bash

# ============================================================================
# Ovovex Accounting System - Quick Start Script
# ============================================================================
# This script automates the initial setup process
# ============================================================================

set -e  # Exit on error

echo ""
echo "========================================================================"
echo "🚀 OVOVEX ACCOUNTING SYSTEM - QUICK START"
echo "========================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Check if requirements are installed
if ! python -c "import django" 2>/dev/null; then
    echo "📦 Installing dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your database credentials${NC}"
    echo -e "${YELLOW}   Especially: DB_PASSWORD, SECRET_KEY${NC}"
    echo ""
    read -p "Press Enter to continue after editing .env (or press Ctrl+C to exit)..."
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

echo ""

# Initialize database
echo "🗄️  Initializing database..."
python manage.py init_db

echo ""
echo "========================================================================"
echo "✅ SETUP COMPLETE!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Change admin password:"
echo "   python manage.py changepassword admin"
echo ""
echo "2. Start development server:"
echo "   python manage.py runserver"
echo ""
echo "3. Access the application:"
echo "   http://localhost:8000"
echo ""
echo "4. Login with:"
echo "   Username: admin"
echo "   Password: changeme123 (change immediately!)"
echo ""
echo "For more information, see README.md and SETUP.md"
echo ""
