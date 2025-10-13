@echo off
echo 🚀 Creating admin user for VARANDA POS...
echo ===============================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo 🐍 Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist "env\Scripts\activate.bat" (
    echo 🐍 Activating virtual environment...
    call env\Scripts\activate.bat
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo 🐍 Using Python: 
python --version

REM Check if Django is available
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo ❌ Django not found! Installing dependencies...
    echo 💡 Running: pip install -r requirements.txt
    pip install -r requirements.txt
    
    REM Check again
    python -c "import django" >nul 2>&1
    if errorlevel 1 (
        echo ❌ Failed to install Django. Please install manually.
        pause
        exit /b 1
    )
)

echo ✅ Django found
echo.

REM Run database migrations first
echo 🔄 Running database migrations...
python manage.py migrate

REM Create admin user using Django management command
echo 👤 Creating admin user...
python manage.py create_admin_user --email admin@gmail.com --password "12345!" --force

echo.
echo ✨ Script completed!
echo 🌐 You can now access the admin panel at: http://localhost:8000/admin/
echo 📧 Email: admin@gmail.com
echo 🔑 Password: 12345!
echo.
echo Press any key to continue...
pause >nul