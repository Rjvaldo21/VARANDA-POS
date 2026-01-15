# VARANDA-POS Cross-Platform Setup Guide

This guide will help you set up VARANDA-POS on Windows, Mac, and Linux with automatic virtual environment detection.

## 🖥️ Supported Platforms

- ✅ **Windows** 10/11 (x64)
- ✅ **macOS** 10.15+ (Intel & Apple Silicon)
- ✅ **Linux** Ubuntu 18.04+ / Debian 10+ / CentOS 8+

## 📋 Prerequisites

### All Platforms:
- **Node.js** 16+ (LTS recommended)
- **Python** 3.8+ 
- **Git** (for cloning repository)

### Platform-Specific:

#### Windows:
```powershell
# Install Python from python.org or via winget
winget install Python.Python.3.11

# Install Node.js
winget install OpenJS.NodeJS.LTS

# Install Git
winget install Git.Git
```

#### macOS:
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install requirements
brew install python@3.11 node git
```

#### Linux (Ubuntu/Debian):
```bash
# Update package list
sudo apt update

# Install requirements
sudo apt install python3 python3-pip python3-venv nodejs npm git

# Install build tools (if needed)
sudo apt install build-essential
```

## 🚀 Quick Setup (Recommended)

### Option 1: Automated Setup
```bash
# Clone repository
git clone <repository-url>
cd VARANDA-POS

# Run automated setup (installs frontend + backend)
npm run setup
```

### Option 2: Manual Setup
```bash
# 1. Clone and install frontend
git clone <repository-url>
cd VARANDA-POS
npm install

# 2. Setup backend virtual environment
npm run setup-backend

# 3. Run application
npm run dev
```

## 🔧 Virtual Environment Auto-Detection

The application automatically detects and uses the appropriate virtual environment:

### Detection Priority:

**Windows:**
1. `backend/venv/Scripts/python.exe`
2. `backend/env/Scripts/python.exe`
3. System `python.exe`
4. System `python`

**macOS:**
1. `backend/venv_mac/bin/python`
2. `backend/venv/bin/python`
3. `backend/env/bin/python`
4. System `python3`
5. System `python`

**Linux:**
1. `backend/venv/bin/python`
2. `backend/env/bin/python`
3. System `python3`
4. System `python`

## 📂 Directory Structure After Setup

```
VARANDA-POS/
├── backend/
│   ├── venv/                # Windows virtual environment
│   ├── venv_mac/            # macOS virtual environment  
│   ├── start_backend.bat    # Windows startup script
│   ├── start_backend.sh     # Mac/Linux startup script
│   ├── VENV_INFO.md         # Virtual environment info
│   └── setup_venv.js        # Cross-platform setup script
├── src/                     # Vue.js frontend
├── electron/                # Electron main process
└── package.json             # NPM scripts
```

## 🎯 NPM Scripts Reference

### Development:
```bash
npm run dev              # Start full application (Vite + Electron + Django)
npm run vite             # Start Vite dev server only
npm run electron         # Start Electron only
```

### Backend Management:
```bash
npm run setup-backend    # Setup virtual environment
npm run backend:start    # Start Django server manually
npm run clean           # Remove all virtual environments
```

### Building:
```bash
npm run build           # Build frontend for production
npm run electron:build  # Build desktop installer
npm run preview         # Preview production build
```

## 🛠️ Manual Backend Setup (Alternative)

If automated setup fails, you can set up the backend manually:

### Windows:
```batch
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

### Mac/Linux:
```bash
cd backend
python3 -m venv venv_mac  # or just 'venv'
source venv_mac/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

## 🔐 Default Login Credentials

After setup, use these credentials:

- **Email/Username**: `admin@gmail.com`
- **Password**: `admin12345!`

## 🐛 Troubleshooting

### Common Issues:

#### 1. Python Not Found:
```bash
# Windows: Add Python to PATH or reinstall
# Mac: Install via Homebrew: brew install python@3.11
# Linux: sudo apt install python3 python3-pip
```

#### 2. Virtual Environment Creation Failed:
```bash
# Make sure you have venv module
# Windows: python -m pip install --user virtualenv
# Mac/Linux: python3 -m pip install --user virtualenv
```

#### 3. Permission Denied (Mac/Linux):
```bash
chmod +x backend/start_backend.sh
# Or run with sudo if needed
```

#### 4. Port Already in Use:
```bash
# Check what's using port 8000/5173
# Windows: netstat -ano | findstr :8000
# Mac/Linux: lsof -i :8000

# Kill process if needed
# Windows: taskkill /PID <PID> /F
# Mac/Linux: kill -9 <PID>
```

#### 5. Django Dependencies Missing:
```bash
# Reinstall requirements
cd backend
# Activate venv first, then:
pip install -r requirements.txt
```

### Debug Information:

The application provides detailed logging:

#### Electron Console:
```
✅ Found Python at: backend/venv_mac/bin/python
🔄 Django Migrate: Operations to perform...
✅ Django migrate completed with code 0
📡 Django: Starting development server at http://127.0.0.1:8000/
🔗 Trying to load: http://localhost:5173
✅ Successfully loaded: http://localhost:5173
```

#### Check Virtual Environment:
```bash
# Check which Python is being used
cd backend

# Windows:
venv\Scripts\python.exe --version

# Mac/Linux:
venv_mac/bin/python --version
```

## 🚀 Development Workflow

### Starting Development:
1. **Terminal 1**: `npm run dev` (starts everything)
2. **Or manually**:
   - **Terminal 1**: `npm run backend:start`
   - **Terminal 2**: `npm run vite`
   - **Terminal 3**: `npm run electron`

### Making Changes:
- **Frontend**: Hot reload automatic (Vite)
- **Backend**: Restart Django server
- **Electron**: Restart application

### Building for Production:
```bash
# Build installer for current platform
npm run electron:build

# Build for specific platform (requires setup)
npm run electron:build -- --win   # Windows
npm run electron:build -- --mac   # macOS
npm run electron:build -- --linux # Linux
```

## 📊 Platform-Specific Notes

### Windows:
- Uses `.bat` files for startup scripts
- Virtual environment in `backend/venv/`
- Executable: `python.exe`

### macOS:
- Uses `.sh` files for startup scripts  
- Virtual environment in `backend/venv_mac/`
- Executable: `python`
- May require Xcode Command Line Tools

### Linux:
- Uses `.sh` files for startup scripts
- Virtual environment in `backend/venv/`
- May require additional build dependencies
- Some distributions need `python3-dev` package

## ✅ Verification

After setup, verify everything works:

1. **Backend**: http://localhost:8000/admin/
2. **Frontend**: http://localhost:5173/ (dev) or Electron app
3. **API**: http://localhost:8000/api/
4. **Login**: Use default credentials above

## 🎉 Ready to Go!

Your VARANDA-POS application is now set up for cross-platform development. The system will automatically detect your OS and use the appropriate Python virtual environment.

For support, check the console logs or create an issue in the repository.