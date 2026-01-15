# VARANDA POS - Fix Running Instructions

## Cara Menjalankan Aplikasi (UPDATED)

### Metode 1: Manual (3 Terminal) - PALING STABIL

**Terminal 1 - Backend Django:**
```bash
cd backend
python3 manage.py migrate
python3 manage.py runserver 127.0.0.1:8000
```

**Terminal 2 - Frontend Vite:**
```bash
npm run vite
```

**Terminal 3 - Electron (tunggu vite ready dulu):**
```bash
npm run electron
```

### Metode 2: Semi-Otomatis (2 Terminal)

**Terminal 1 - Backend Django:**
```bash
cd backend
python3 manage.py runserver 127.0.0.1:8000
```

**Terminal 2 - Frontend + Electron:**
```bash
npm run dev
```

### Metode 3: Full Otomatis
```bash
./run-dev.sh
```

## Jika Ada Error

### Error: Electron not found
```bash
# Install ulang electron
npm install electron@25.9.0 --save-dev

# Atau install semua dependencies
npm install
```

### Error: Port already in use
```bash
# Kill semua process
lsof -ti:5173 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### Error: Module not found
```bash
# Install ulang semua dependencies
rm -rf node_modules package-lock.json
npm install
```

## Test Fungsi Simpan

1. Buka browser console (F12)
2. Coba simpan data
3. Lihat Network tab untuk melihat request ke API
4. Pastikan request ke: http://localhost:8000/api/
5. Jika error 401, login ulang

## Login Credentials Default

Jika belum ada user:
```bash
cd backend
python3 manage.py createsuperuser
```

## Memastikan Database Berjalan

Cek apakah Django server sudah jalan:
```bash
curl http://localhost:8000/api/
```

Harus return response JSON, bukan error.