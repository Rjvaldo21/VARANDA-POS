#!/usr/bin/env python3
"""
Install Django dependencies for VARANDA-POS backend
Run this script to install all required dependencies
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Installing VARANDA-POS Backend Dependencies")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"📋 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    
    # Install dependencies
    dependencies = [
        "Django>=5.2.0,<5.3.0",
        "djangorestframework>=3.14.0",
        "django-cors-headers>=4.0.0", 
        "djangorestframework-simplejwt>=5.2.0",
        "python-dotenv>=1.0.0",
        "dj-database-url>=2.1.0",
        "Pillow>=10.0.0",
        "reportlab>=3.6.0",
        "python-barcode>=0.14.0",
        "qrcode>=7.4.0"
    ]
    
    # Try different pip commands
    pip_commands = ["pip3", "pip", f"{sys.executable} -m pip"]
    
    success = False
    for pip_cmd in pip_commands:
        print(f"\n🔄 Trying with: {pip_cmd}")
        
        # Test if pip command works
        test_result = run_command(f"{pip_cmd} --version", f"Testing {pip_cmd}")
        if not test_result:
            continue
            
        # Install each dependency
        all_installed = True
        for dep in dependencies:
            install_cmd = f"{pip_cmd} install '{dep}'"
            if not run_command(install_cmd, f"Installing {dep}"):
                all_installed = False
                break
        
        if all_installed:
            success = True
            break
    
    if success:
        print("\n✅ All dependencies installed successfully!")
        print("\n🚀 Now you can run:")
        print("   python3 manage.py runserver")
        return True
    else:
        print("\n❌ Failed to install dependencies with all pip commands")
        print("\n💡 Try manually:")
        print("   pip3 install django djangorestframework djangorestframework-simplejwt")
        print("   pip3 install django-cors-headers python-dotenv dj-database-url")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)