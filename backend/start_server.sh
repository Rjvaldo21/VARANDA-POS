#!/bin/bash

# Start Django Server Script for VARANDA-POS

echo "🚀 Starting VARANDA-POS Backend Server..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install -q django djangorestframework djangorestframework-simplejwt django-cors-headers dj-database-url python-dotenv 2>/dev/null || {
    echo "⚠️  Some dependencies might be missing. Installing..."
    pip3 install django djangorestframework djangorestframework-simplejwt django-cors-headers dj-database-url python-dotenv
}

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is in use. Using port 8001 instead..."
    PORT=8001
else
    PORT=8000
fi

echo "✅ Starting Django server on port $PORT..."
echo "📍 API will be available at: http://localhost:$PORT/api/"
echo "🔐 Admin panel at: http://localhost:$PORT/admin/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Django development server
python3 manage.py runserver $PORT