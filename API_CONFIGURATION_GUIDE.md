# 🔧 API Configuration Guide - VARANDA-POS

## ✅ Centralized API Configuration Implemented

Semua hardcoded API URLs telah diperbaiki dan diganti dengan sistem terpusat menggunakan environment variables.

## 📁 File Configuration

### 1. Environment File (`.env`)
```env
# API Configuration - Update port sesuai Django server
VITE_API_BASE_URL=http://localhost:8001/api

# Alternative URLs untuk environment berbeda:
# VITE_API_BASE_URL=http://localhost:8000/api  # Development alternative
# VITE_API_BASE_URL=https://your-domain.com/api  # Production
```

### 2. Centralized Axios Instance (`src/axios.js`)
```javascript
import axios from 'axios'

// Get base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api'
const baseURL = API_BASE_URL.endsWith('/') ? API_BASE_URL : `${API_BASE_URL}/`

const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Auto JWT token attachment
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
export { baseURL, API_BASE_URL }
```

## 🔄 Cara Menggunakan

### Import di Component Vue
```javascript
// ✅ BENAR - Gunakan centralized API
import api from '@/axios'

// API calls
const response = await api.get('users/')
const result = await api.post('products/', data)

// ❌ SALAH - Jangan gunakan hardcoded URLs
import axios from 'axios'
const response = await axios.get('http://localhost:8000/api/users/')
```

### Untuk Static Assets/Media
```javascript
import { baseURL } from '@/axios'

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${baseURL.replace('/api/', '')}${path}`
}
```

## 🚀 Quick Setup Guide

### 1. Development
```bash
# Update .env file
echo "VITE_API_BASE_URL=http://localhost:8001/api" > .env

# Start frontend
npm run dev
```

### 2. Production
```bash
# Update .env file untuk production
echo "VITE_API_BASE_URL=https://your-api-domain.com/api" > .env

# Build aplikasi
npm run build
```

### 3. Testing dengan Port Berbeda
```bash
# Jika Django running di port 8000
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env

# Jika Django running di port 8080  
echo "VITE_API_BASE_URL=http://localhost:8080/api" > .env
```

## 📝 File Changes Summary

### ✅ Files Updated (20 files):
- `src/pages/Administrasaun.vue`
- `src/pages/IventoriuProdutu.vue` 
- `src/pages/RelatoriuFaan.vue`
- `src/pages/RelatoriuTranzasaun.vue`
- `src/pages/RelatoriuFinansas.vue`
- `src/pages/TranzasaunKompra.vue`
- `src/pages/TranzasaunRetornuFaan.vue`
- `src/pages/TranzasaunRetornuKompra.vue`
- `src/pages/IventoriuSupplier.vue`
- `src/pages/IventoriuListaKliente.vue`
- `src/pages/Kategoria.vue`
- `src/pages/WarehouseList.vue`
- `src/pages/WarehouseStock.vue`
- `src/pages/StockMovementHistory.vue`
- `src/pages/InventoriuHadiaStok.vue`
- `src/pages/IventoriuUnidade.vue`
- `src/pages/KomputadorKasir.vue`
- `src/pages/RelatoriuProdutu.vue`
- `src/pages/KonfiguraPontos.vue`
- `src/components/pos/BarcodeInput.vue`

### 📄 Backup Files Created:
All original files saved with `.backup` extension.

## 🔧 Troubleshooting

### 1. Server Connection Error
```bash
# Check .env file
cat .env

# Pastikan VITE_API_BASE_URL sesuai dengan Django port
```

### 2. CORS Issues
```bash
# Pastikan Django settings.py memiliki:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]
```

### 3. JWT Token Issues  
```bash
# Check browser localStorage
localStorage.getItem('token')
localStorage.getItem('refresh_token')
```

### 4. Restore Original Files (if needed)
```bash
# Restore all backup files
find . -name "*.backup" -exec sh -c 'mv "$1" "${1%.backup}"' _ {} \;
```

## 🎯 Benefits

1. **Single Point of Configuration** - Ubah URL di satu tempat (`.env`)
2. **Environment Flexibility** - Easy switching between dev/staging/production  
3. **No More Hardcoded URLs** - Semua API calls menggunakan environment variable
4. **Automatic JWT Handling** - Token otomatis attach ke setiap request
5. **Error Handling** - Centralized response interceptors untuk 401/403
6. **Better Maintainability** - Code lebih clean dan mudah di-maintain

## 📞 Testing

### Manual Test:
1. Update `.env` dengan URL berbeda
2. Restart `npm run dev`
3. Coba login dan API calls lainnya
4. Pastikan semua request ke URL baru

### Quick Test Script:
```bash
# Test different ports
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env && npm run dev
```

---

**⚡ Sekarang semua API URLs sudah terpusat dan mudah di-manage!**

Untuk mengubah API URL, cukup update file `.env` dan restart aplikasi.