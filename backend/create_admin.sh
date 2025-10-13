#!/bin/bash

echo "🚀 Creating admin user for VARANDA POS..."
echo "==============================================="
echo

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
elif [ -d "env" ]; then
    echo "🐍 Activating virtual environment..."
    source env/bin/activate
elif [ -d "venv_mac" ]; then
    echo "🐍 Activating virtual environment..."
    source venv_mac/bin/activate
fi

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found! Please install Python first."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🐍 Using Python: $PYTHON_CMD"

# Check if Django is available
$PYTHON_CMD -c "import django" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Django not found! Installing dependencies..."
    echo "💡 Running: pip install -r requirements.txt"
    pip install -r requirements.txt
    
    # Check again
    $PYTHON_CMD -c "import django" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Django. Please install manually."
        exit 1
    fi
fi

echo "✅ Django found"
echo

# Run database migrations first
echo "🔄 Running database migrations..."
$PYTHON_CMD manage.py migrate

# Create admin user using Django management command
echo "👤 Creating admin user..."
$PYTHON_CMD manage.py create_admin_user --email admin@gmail.com --password "12345!" --force

echo
echo "✨ Script completed!"
echo "🌐 You can now access the admin panel at: http://localhost:8000/admin/"
echo "📧 Email: admin@gmail.com"
echo "🔑 Password: 12345!"