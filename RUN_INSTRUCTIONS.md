# VARANDA POS - Instruksi Menjalankan Aplikasi

## Cara Menjalankan Aplikasi

### Opsi 1: Menggunakan Script Otomatis (Rekomendasi)

1. Buka terminal di folder project VARANDA-POS
2. Jalankan perintah:
   ```bash
   ./run-dev.sh
   ```
   Script ini akan otomatis:
   - Membersihkan port yang digunakan
   - Menjalankan database migrations
   - Memulai Django backend server di port 8000
   - Memulai Vite + Electron frontend

### Opsi 2: Menjalankan Manual

Jika script tidak bekerja, jalankan manual dengan 2 terminal:

**Terminal 1 - Backend Django:**
```bash
cd backend
python3 manage.py migrate
python3 manage.py runserver 127.0.0.1:8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### Opsi 3: Menggunakan npm script
```bash
npm run dev:full
```

## Troubleshooting

### 1. Port sudah digunakan
Jika ada error port 8000 atau 5173 sudah digunakan:
```bash
# Kill process di port 8000
lsof -ti:8000 | xargs kill -9

# Kill process di port 5173  
lsof -ti:5173 | xargs kill -9
```

### 2. Database tidak terkoneksi
- Pastikan Django server berjalan di port 8000
- Cek file `src/axios.js` menggunakan URL: `http://localhost:8000/api`

### 3. Fungsi simpan tidak bekerja
- Buka browser console (F12) untuk melihat error
- Pastikan token authentication tersimpan di localStorage
- Cek network tab untuk melihat API response

### 4. Dependencies tidak terinstall

**Backend:**
```bash
cd backend
pip3 install -r requirements.txt
```

**Frontend:**
```bash
npm install
```

## Akses Aplikasi

- **Frontend POS**: http://localhost:5173
- **API Backend**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/

## Membuat User Admin

```bash
cd backend
python3 manage.py createsuperuser
```

## Build untuk Production

```bash
npm run electron:build
```

Aplikasi akan di-build ke folder `dist/`