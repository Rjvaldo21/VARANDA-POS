# VARANDA-POS Running Guide

## 📋 Prerequisites

Sebelum menjalankan aplikasi, pastikan Anda telah menginstall:

- **Node.js** (v16 atau lebih baru)
- **Python** (v3.8 atau lebih baru)
- **Git** (untuk cloning repository)

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd VARANDA-POS
```

### 2. Install Dependencies

#### Frontend Dependencies
```bash
# Install npm packages untuk Electron dan Vue.js
npm install
```

#### Backend Dependencies (Opsional untuk development)
```bash
# Navigate ke backend directory
cd backend

# Buat virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Kembali ke root directory
cd ..
```

## 🖥️ Running Modes

### Mode 1: Development Mode (Recommended)

Menjalankan aplikasi dalam development mode dengan hot-reload:

```bash
npm run dev
```

Ini akan:
- ✅ Start Vite development server di `http://localhost:5173`
- ✅ Launch Electron app dengan embedded Django backend
- ✅ Enable hot-reload untuk Vue.js changes
- ✅ Copy database ke user directory jika belum ada

### Mode 2: Preview Mode

Untuk test production build tanpa packaging:

```bash
# Build frontend first
npm run build

# Preview built app
npm run preview
```

### Mode 3: Production Build

Untuk membuat installer aplikasi:

```bash
# Build untuk platform saat ini
npm run electron:build

# Atau build untuk platform specific:
# Windows
npm run electron:build -- --win

# macOS
npm run electron:build -- --mac

# Linux
npm run electron:build -- --linux
```

Output installer akan berada di folder `dist/`:
- Windows: `dist/VARANDA POS Setup x.x.x.exe`
- macOS: `dist/VARANDA POS-x.x.x.dmg`
- Linux: `dist/varanda-pos_x.x.x_amd64.deb`

## 📁 Directory Structure

```
VARANDA-POS/
├── backend/              # Django backend
│   ├── pos/             # Main Django app
│   ├── posbackend/      # Django settings
│   ├── manage.py        # Django management
│   └── db.sqlite3       # Development database
├── src/                 # Vue.js frontend source
│   ├── components/      # Vue components
│   ├── pages/          # Vue pages/routes
│   ├── router/         # Vue router config
│   └── main.js         # Vue entry point
├── electron/            # Electron main process
│   ├── main.cjs        # Electron main file
│   └── preload.js      # Preload script
├── dist/               # Build output
├── package.json        # NPM dependencies
└── vite.config.js     # Vite configuration
```

## 🛠️ Troubleshooting

### Problem 1: "command not found: npm"
**Solution**: Install Node.js dari https://nodejs.org/

### Problem 2: "command not found: python"
**Solution**: 
- macOS/Linux: Coba `python3` instead of `python`
- Windows: Install Python dari https://python.org/

### Problem 3: Electron window blank/white screen
**Solution**:
1. Pastikan tidak ada error di console (View → Toggle Developer Tools)
2. Check apakah Django backend running (lihat terminal output)
3. Try refresh window (Ctrl/Cmd + R)

### Problem 4: Port already in use
**Solution**:
```bash
# Check what's using port 8000
# Windows:
netstat -ano | findstr :8000
# macOS/Linux:
lsof -i :8000

# Kill the process atau gunakan port lain
```

### Problem 5: Database errors
**Solution**:
1. Delete existing database di user directory:
   - Windows: `%APPDATA%\VARANDA_POS\db.sqlite3`
   - macOS: `~/Library/Application Support/VARANDA_POS/db.sqlite3`
   - Linux: `~/.config/VARANDA_POS/db.sqlite3`
2. Restart aplikasi (database akan di-create ulang)

## 🔧 Development Tips

### 1. Hot Reload
- Frontend changes akan auto-reload
- Backend changes perlu restart aplikasi

### 2. Debug Mode
```bash
# Enable Electron debug logging
DEBUG=electron:* npm run dev

# Enable Django debug (sudah ON by default)
# Check backend/posbackend/settings.py
```

### 3. Developer Tools
- Electron: View → Toggle Developer Tools (atau F12)
- Vue DevTools: Install browser extension untuk debugging Vue

### 4. Database Access
Untuk access database directly:
```bash
cd backend
python manage.py dbshell
```

### 5. Create Superuser
```bash
cd backend
python manage.py createsuperuser
```
Atau gunakan API endpoint `/create-superuser/` di aplikasi.

## 📱 Running on Different Platforms

### Windows
```bash
# Pastikan menggunakan Command Prompt atau PowerShell
npm run dev
```

### macOS
```bash
# Mungkin perlu permissions untuk Electron
npm run dev

# Jika ada error permission:
sudo npm run dev
```

### Linux
```bash
# Install dependencies yang mungkin diperlukan
sudo apt-get install libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6

npm run dev
```

## 🌐 API Access

Saat running dalam development mode:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

## 📝 Environment Configuration

Untuk custom configuration, buat file `.env` di root:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Electron Configuration  
ELECTRON_IS_DEV=1
```

## 🐛 Debug Commands

```bash
# Check Node version
node --version

# Check NPM version  
npm --version

# Check Python version
python --version
# atau
python3 --version

# Clear NPM cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## 📦 Production Deployment

Untuk production deployment, lihat:
- [BACKEND_REFACTORING_TODO.md](./BACKEND_REFACTORING_TODO.md)
- [DESKTOP_APP_REFACTORING_TODO.md](./DESKTOP_APP_REFACTORING_TODO.md)
- [DEPLOYMENT_STRATEGY_TODO.md](./DEPLOYMENT_STRATEGY_TODO.md)

## 💡 Tips & Best Practices

1. **Always run `npm install`** setelah pull changes dari Git
2. **Check console logs** untuk debugging issues
3. **Use development mode** untuk development, bukan production build
4. **Backup database** sebelum major updates
5. **Test di semua platforms** sebelum release

---

Untuk bantuan lebih lanjut, buka issue di repository atau hubungi tim development.