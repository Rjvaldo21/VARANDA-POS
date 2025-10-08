#!/bin/bash

echo "🚀 Starting VARANDA POS Development Environment..."
echo ""

# Function to kill process on port
kill_port() {
    lsof -ti:$1 | xargs kill -9 2>/dev/null
}

# Clean up ports if needed
echo "🧹 Cleaning up ports..."
kill_port 8000
kill_port 5173

# Start Django in background
echo "📡 Starting Django Backend Server..."
cd backend

# Run migrations
echo "🔄 Running database migrations..."
python3 manage.py migrate --noinput

# Start Django server in background
echo "✅ Starting Django server on port 8000..."
python3 manage.py runserver 127.0.0.1:8000 &
DJANGO_PID=$!

cd ..

# Wait for Django to start
echo "⏳ Waiting for Django to start..."
sleep 3

# Start frontend
echo ""
echo "🎨 Starting Vite + Electron frontend..."
npm run dev

# Cleanup on exit
trap "kill $DJANGO_PID 2>/dev/null; kill_port 8000; kill_port 5173" EXIT