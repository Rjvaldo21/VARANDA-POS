#!/usr/bin/env python
"""
Script to create migration for enhanced role management system
Run this with: python manage.py shell < create_role_migration.py
"""

import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posbackend.settings')
django.setup()

from django.core.management import call_command

# Create migration for Profile model changes
try:
    print("Creating migration for enhanced role management...")
    call_command('makemigrations', 'pos', '--name', 'enhanced_role_management')
    print("✅ Migration created successfully!")
    
    print("\nTo apply the migration, run:")
    print("python manage.py migrate")
    
except Exception as e:
    print(f"❌ Error creating migration: {e}")