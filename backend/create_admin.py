#!/usr/bin/env python
"""
Quick script to create admin user for VARANDA POS
Run this script from the backend directory
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posbackend.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


def create_admin_user():
    print("🚀 Creating admin user for VARANDA POS")
    print("=" * 50)
    
    # User credentials
    email = 'admin@gmail.com'
    username = email  # Use email as username
    password = 'admin12345!'  # Updated to meet Django requirements
    
    try:
        # Validate password
        validate_password(password)
        print("✅ Password validation passed")
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            print(f"⚠️  User '{username}' already exists!")
            
            # Ask if user wants to update
            update = input("Do you want to update the existing user? (y/n): ").lower().strip()
            if update in ['y', 'yes']:
                user = User.objects.get(username=username)
                user.email = email
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()
                print("✅ Updated existing admin user!")
            else:
                print("❌ Operation cancelled")
                return
        else:
            # Create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print("✅ Admin user created successfully!")
        
        # Display user details
        print("\n👤 Admin User Details:")
        print(f"   📧 Email: {email}")
        print(f"   👤 Username: {username}")
        print(f"   🔑 Password: {password}")
        print(f"   🔐 Is Superuser: Yes")
        print(f"   👔 Is Staff: Yes")
        
        print("\n🎉 You can now login to:")
        print("   🌐 Admin Panel: http://localhost:8000/admin/")
        print("   🔗 API Token: POST http://localhost:8000/api/token/")
        
        # Password security check
        print("\n🔒 Password Security Analysis:")
        security_checks = [
            (len(password) >= 8, "Length (8+ characters)", "✅" if len(password) >= 8 else "❌"),
            (any(c.isupper() for c in password), "Uppercase letters", "✅" if any(c.isupper() for c in password) else "⚠️"),
            (any(c.islower() for c in password), "Lowercase letters", "✅" if any(c.islower() for c in password) else "⚠️"),
            (any(c.isdigit() for c in password), "Numbers", "✅" if any(c.isdigit() for c in password) else "⚠️"),
            (any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password), "Special characters", "✅" if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password) else "⚠️"),
        ]
        
        score = sum(1 for check, _, _ in security_checks if check)
        
        for check, name, icon in security_checks:
            print(f"   {icon} {name}")
        
        if score >= 4:
            print("   🛡️  Password strength: STRONG")
        elif score >= 3:
            print("   🔶 Password strength: MEDIUM")
        else:
            print("   ⚠️  Password strength: WEAK")
        
        print("\n✨ Admin user setup complete!")
        
    except ValidationError as e:
        print(f"❌ Password validation failed: {', '.join(e.messages)}")
        print("\n💡 Password requirements:")
        print("   - At least 8 characters long")
        print("   - Cannot be too common")
        print("   - Cannot be entirely numeric")
        print("   - Should contain mix of letters, numbers, and symbols")
        
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")


if __name__ == "__main__":
    create_admin_user()