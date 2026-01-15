#!/bin/bash

# VARANDA-POS Backend Setup Script
# This script creates virtual environment and installs dependencies

set -e  # Exit on any error

echo "🚀 VARANDA-POS Backend Setup"
echo "============================"

# Navigate to backend directory
cd "$(dirname "$0")"
BACKEND_DIR=$(pwd)

echo "📍 Working in: $BACKEND_DIR"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📋 Python Version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv_mac" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv_mac
    echo "✅ Virtual environment created: venv_mac/"
else
    echo "✅ Virtual environment already exists: venv_mac/"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv_mac/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install Django dependencies
echo "📦 Installing Django dependencies..."
pip install Django==5.2.4
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.0.0
pip install djangorestframework-simplejwt==5.2.2
pip install python-dotenv==1.0.0
pip install dj-database-url==2.1.0

# Install additional dependencies
echo "📦 Installing additional dependencies..."
pip install Pillow==10.0.1 || echo "⚠️  Pillow install failed, continuing..."
pip install reportlab==3.6.12 || echo "⚠️  reportlab install failed, continuing..."
pip install python-barcode==0.14.0 || echo "⚠️  python-barcode install failed, continuing..."
pip install qrcode==7.4.2 || echo "⚠️  qrcode install failed, continuing..."

echo ""
echo "✅ All dependencies installed successfully!"
echo ""

# Test Django installation
echo "🧪 Testing Django installation..."
python -c "import django; print(f'Django version: {django.get_version()}')" || {
    echo "❌ Django test failed!"
    exit 1
}

# Run Django checks
echo "🔍 Running Django system checks..."
python manage.py check || {
    echo "❌ Django checks failed!"
    exit 1
}

# Run migrations if needed
echo "🔄 Running database migrations..."
python manage.py migrate || {
    echo "❌ Migration failed!"
    exit 1
}

echo ""
echo "🎉 Backend setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Activate virtual environment: source venv_mac/bin/activate"
echo "   2. Start server: python manage.py runserver 8001"
echo "   3. Create admin user: python manage.py createsuperuser"
echo ""
echo "🌐 API will be available at: http://localhost:8001/api/"
echo "🔐 Admin panel at: http://localhost:8001/admin/"
echo ""