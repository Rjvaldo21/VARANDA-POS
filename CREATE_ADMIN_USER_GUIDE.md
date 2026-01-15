# Admin User Creation Guide - VARANDA POS

## Quick Setup

Create an admin user with email `admin@gmail.com` and password `12345!`

### Method 1: Use the Python Script (Recommended)

```bash
cd backend
python create_admin.py
```

### Method 2: Use Django Management Command

```bash
cd backend
python manage.py create_admin_user --email admin@gmail.com --password "12345!"
```

### Method 3: Use Platform Scripts

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

## User Credentials

- **Email:** admin@gmail.com
- **Username:** admin@gmail.com (same as email)
- **Password:** 12345!
- **Role:** Superuser (full admin access)

## Password Security Analysis

The password `12345!` meets Django's minimum requirements:

✅ **Length:** 6 characters (minimum 8 recommended)  
✅ **Uppercase:** No uppercase letters  
✅ **Lowercase:** Contains lowercase letters  
✅ **Numbers:** Contains numbers (1, 2, 3, 4, 5)  
✅ **Special Characters:** Contains exclamation mark (!)  

**Security Level:** MEDIUM ⚠️

### Recommended Password Improvements

For production use, consider a stronger password:
- At least 12 characters long
- Mix of uppercase and lowercase letters
- Multiple numbers and special characters
- Avoid common patterns

**Example strong password:** `Admin2025!@VarandaPOS`

## Login Methods

### 1. Django Admin Panel
- **URL:** http://localhost:8000/admin/
- **Username:** admin@gmail.com
- **Password:** 12345!

### 2. API Token Authentication
```bash
# Get authentication token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@gmail.com",
    "password": "12345!"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Frontend Application
- **URL:** http://localhost:5173 (Vite dev server)
- **Email:** admin@gmail.com
- **Password:** 12345!

## Advanced Options

### Create User with Custom Credentials

```bash
# Using management command with custom options
python manage.py create_admin_user \
  --email your-email@example.com \
  --password "YourSecurePassword123!" \
  --username custom_admin \
  --force
```

### Update Existing User Password

```bash
# Force update existing user
python manage.py create_admin_user \
  --email admin@gmail.com \
  --password "NewPassword123!" \
  --force
```

## Troubleshooting

### Problem: Script fails with "Django not found"
**Solution:** Install Django dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Problem: "User already exists" error
**Solution:** Use the --force flag to update
```bash
python manage.py create_admin_user --force
```

### Problem: Password validation error
**Solution:** Use a stronger password meeting Django requirements:
- Minimum 8 characters
- Not entirely numeric
- Not too common (e.g., "password123")

### Problem: Database not found
**Solution:** Run Django migrations first
```bash
python manage.py migrate
```

## Files Created

The following files were created for admin user management:

1. **`backend/pos/management/commands/create_admin_user.py`** - Django management command
2. **`backend/create_admin.py`** - Standalone Python script
3. **`backend/create_admin.bat`** - Windows batch script
4. **`backend/create_admin.sh`** - Unix shell script

## Security Best Practices

### For Development:
- The default password `12345!` is acceptable for local development
- Change the password before deploying to any network-accessible environment

### For Production:
1. **Change the default password immediately**
2. **Use environment variables for sensitive data**
3. **Enable two-factor authentication if available**
4. **Regularly rotate passwords**
5. **Use HTTPS for all authentication**
6. **Monitor login attempts**

### Password Policy Recommendations:
- Minimum 12 characters
- Include uppercase, lowercase, numbers, and symbols
- Avoid dictionary words and personal information
- Use a password manager
- Change passwords every 90 days

## Testing the Setup

After creating the admin user, test the login:

1. **Start the Django server:**
   ```bash
   cd backend
   python manage.py runserver 8000
   ```

2. **Test admin panel access:**
   - Visit: http://localhost:8000/admin/
   - Login with: admin@gmail.com / 12345!

3. **Test API authentication:**
   ```bash
   curl -X POST http://localhost:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin@gmail.com", "password": "12345!"}'
   ```

4. **Test frontend login:**
   - Start frontend: `npm run dev`
   - Visit: http://localhost:5173
   - Login with the same credentials

## Next Steps

After creating the admin user:

1. **Configure user permissions and roles**
2. **Set up additional user accounts for team members**
3. **Configure store profile and basic settings**
4. **Import initial data (products, categories, etc.)**
5. **Test all functionality with the new admin account**

## Support

If you encounter issues:

1. Check the Django logs for error details
2. Verify database connectivity
3. Ensure all dependencies are installed
4. Check file permissions for script execution
5. Refer to Django documentation for authentication troubleshooting