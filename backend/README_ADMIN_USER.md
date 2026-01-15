# Admin User Creation - Quick Start

## 🚀 Quick Setup

Create an admin user with the following credentials:
- **Email:** admin@gmail.com
- **Password:** 12345!

## 📋 Prerequisites

1. Python 3.8+ installed
2. Django backend dependencies installed

## 🛠️ Methods to Create Admin User

### Method 1: Automated Scripts (Recommended)

**Windows:**
```cmd
cd backend
create_admin.bat
```

**Mac/Linux:**
```bash
cd backend
./create_admin.sh
```

### Method 2: Django Management Command

```bash
cd backend
python manage.py create_admin_user --email admin@gmail.com --password "12345!" --force
```

### Method 3: Manual Python Script

```bash
cd backend
python create_admin.py
```

## 🔧 If Dependencies are Missing

Install required packages:
```bash
cd backend
pip install -r requirements.txt
```

Or install core dependencies:
```bash
pip install Django djangorestframework djangorestframework-simplejwt django-cors-headers
```

## 🗄️ Database Setup

If you get database errors, run migrations first:
```bash
cd backend
python manage.py migrate
```

## 🌐 Access Points After Creation

1. **Django Admin Panel:**
   - URL: http://localhost:8000/admin/
   - Login: admin@gmail.com / 12345!

2. **API Token Endpoint:**
   - URL: POST http://localhost:8000/api/token/
   - Body: {"username": "admin@gmail.com", "password": "12345!"}

3. **Frontend Application:**
   - URL: http://localhost:5173 (after running `npm run dev`)
   - Login: admin@gmail.com / 12345!

## 🔒 Security Notes

- Password `12345!` is for development only
- Change password before production deployment
- Consider using environment variables for credentials in production

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Python not found | Install Python 3.8+ |
| Django not found | Run `pip install -r requirements.txt` |
| User already exists | Use `--force` flag |
| Database error | Run `python manage.py migrate` |
| Permission denied | Check file permissions: `chmod +x create_admin.sh` |

## 📞 Need Help?

1. Check the full guide: `CREATE_ADMIN_USER_GUIDE.md`
2. Verify Django server is running: `python manage.py runserver 8000`
3. Check console logs for specific error messages

---

**Quick Commands Summary:**
```bash
cd backend
pip install -r requirements.txt  # Install dependencies
python manage.py migrate         # Setup database
./create_admin.sh                # Create admin user (Mac/Linux)
# OR
create_admin.bat                 # Create admin user (Windows)
python manage.py runserver 8000  # Start server
```