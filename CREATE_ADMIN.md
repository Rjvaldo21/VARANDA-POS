# Create Admin User untuk VARANDA-POS

## Quick Create Admin User

### Option 1: Via API (Recommended - Paling Mudah)

1. Pastikan aplikasi sedang running (`npm run dev`)
2. Buka browser atau gunakan curl/Postman
3. Kirim POST request ke:

```
URL: http://localhost:8000/create-superuser/
Method: POST
Headers: Content-Type: application/json
Body:
{
  "username": "admin",
  "password": "admin123"
}
```

Dengan curl:
```bash
curl -X POST http://localhost:8000/create-superuser/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Option 2: Via Django Command

```bash
# Navigate ke backend directory
cd backend

# Create superuser
python manage.py createsuperuser

# Akan muncul prompt:
# Username: admin
# Email address: (kosongkan, tekan Enter)
# Password: admin123
# Password (again): admin123
```

### Option 3: Via Django Shell

```bash
cd backend
python manage.py shell
```

Kemudian paste code ini:
```python
from django.contrib.auth.models import User
user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print(f"Superuser created: {user.username}")
exit()
```

## Default Credentials Setelah Create

```
Username: admin
Password: admin123
Role: Super Admin (otomatis)
```

## Login ke Aplikasi

1. Buka aplikasi VARANDA-POS
2. Klik menu login atau akses `/login`
3. Masukkan username dan password di atas

## Troubleshooting

### Error: "User already exists"
User admin sudah ada. Gunakan Django shell untuk reset password:

```bash
cd backend
python manage.py shell
```

```python
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.set_password('admin123')
user.save()
print("Password updated successfully")
exit()
```

### Forgot Password?
Gunakan Django command:
```bash
cd backend
python manage.py changepassword admin
```

## Security Note

⚠️ **PENTING**: Password `admin123` hanya untuk development/testing. 
Untuk production, gunakan password yang kuat dan kompleks!

## Create Additional Users

Setelah login sebagai admin, Anda bisa:
1. Klik menu "Administrasaun" → "Uzuariu"
2. Klik tombol "Add User"
3. Isi form dan pilih role sesuai kebutuhan