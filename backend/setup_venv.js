#!/usr/bin/env node

/**
 * Cross-platform Virtual Environment Setup Script
 * Sets up Python virtual environment for Windows, Mac, and Linux
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const platform = os.platform();
const isWindows = platform === 'win32';
const isMac = platform === 'darwin';
const isLinux = platform === 'linux';

console.log('🚀 VARANDA-POS Virtual Environment Setup');
console.log('=' .repeat(50));
console.log(`📱 Platform: ${platform}`);
console.log(`💻 Architecture: ${os.arch()}`);
console.log(`🏠 Home: ${os.homedir()}`);

function runCommand(command, args, options = {}) {
    return new Promise((resolve, reject) => {
        console.log(`🔄 Running: ${command} ${args.join(' ')}`);
        
        const process = spawn(command, args, {
            stdio: 'inherit',
            shell: isWindows,
            ...options
        });

        process.on('close', (code) => {
            if (code === 0) {
                console.log(`✅ Command completed: ${command}`);
                resolve(code);
            } else {
                console.error(`❌ Command failed with code ${code}: ${command}`);
                reject(new Error(`Command failed: ${command}`));
            }
        });

        process.on('error', (err) => {
            console.error(`❌ Command error: ${err.message}`);
            reject(err);
        });
    });
}

async function checkPythonInstallation() {
    console.log('\n🔍 Checking Python installation...');
    
    const pythonCommands = isWindows 
        ? ['python', 'python3', 'py'] 
        : ['python3', 'python'];

    for (const cmd of pythonCommands) {
        try {
            const version = execSync(`${cmd} --version`, { encoding: 'utf8', stdio: 'pipe' });
            console.log(`✅ Found: ${cmd} - ${version.trim()}`);
            return cmd;
        } catch (error) {
            console.log(`❌ Not found: ${cmd}`);
        }
    }

    throw new Error('❌ Python not found. Please install Python 3.8+ and add it to PATH.');
}

async function setupVirtualEnvironment(pythonCmd) {
    console.log('\n📦 Setting up virtual environment...');

    const venvName = isWindows ? 'venv' : (isMac ? 'venv_mac' : 'venv');
    const venvPath = path.join(__dirname, venvName);

    // Remove existing venv if it exists
    if (fs.existsSync(venvPath)) {
        console.log(`🗑️ Removing existing virtual environment: ${venvName}`);
        fs.rmSync(venvPath, { recursive: true, force: true });
    }

    // Create virtual environment
    console.log(`🔨 Creating virtual environment: ${venvName}`);
    await runCommand(pythonCmd, ['-m', 'venv', venvName]);

    return venvPath;
}

async function activateAndInstall(venvPath) {
    console.log('\n📥 Installing dependencies...');

    const activateScript = isWindows 
        ? path.join(venvPath, 'Scripts', 'activate.bat')
        : path.join(venvPath, 'bin', 'activate');
    
    const pythonExe = isWindows 
        ? path.join(venvPath, 'Scripts', 'python.exe')
        : path.join(venvPath, 'bin', 'python');

    const pipExe = isWindows 
        ? path.join(venvPath, 'Scripts', 'pip.exe')
        : path.join(venvPath, 'bin', 'pip');

    console.log(`🔄 Python executable: ${pythonExe}`);
    console.log(`🔄 Pip executable: ${pipExe}`);

    // Upgrade pip first
    console.log('⬆️ Upgrading pip...');
    await runCommand(pythonExe, ['-m', 'pip', 'install', '--upgrade', 'pip']);

    // Install requirements
    const requirementsPath = path.join(__dirname, 'requirements.txt');
    if (fs.existsSync(requirementsPath)) {
        console.log('📦 Installing from requirements.txt...');
        await runCommand(pipExe, ['install', '-r', 'requirements.txt']);
    } else {
        console.log('📦 Installing core dependencies...');
        const packages = [
            'Django>=5.2.0,<5.3.0',
            'djangorestframework>=3.14.0',
            'django-cors-headers>=4.0.0',
            'djangorestframework-simplejwt>=5.2.0',
            'python-dotenv>=1.0.0',
            'Pillow>=10.0.0',
            'reportlab>=3.6.0',
            'python-barcode>=0.14.0',
            'qrcode>=7.4.0'
        ];
        
        for (const pkg of packages) {
            await runCommand(pipExe, ['install', pkg]);
        }
    }

    return { pythonExe, pipExe };
}

async function runMigrations(pythonExe) {
    console.log('\n🗄️ Running database migrations...');
    
    const managePy = path.join(__dirname, 'manage.py');
    if (fs.existsSync(managePy)) {
        await runCommand(pythonExe, [managePy, 'migrate']);
        console.log('✅ Database migrations completed');
    } else {
        console.log('⚠️ manage.py not found, skipping migrations');
    }
}

async function createStartupScripts(venvPath, pythonExe) {
    console.log('\n📝 Creating startup scripts...');

    const venvName = path.basename(venvPath);
    
    if (isWindows) {
        // Windows batch file
        const batchContent = `@echo off
echo 🚀 Starting VARANDA-POS Backend (Windows)
cd /d "%~dp0"
call ${venvName}\\Scripts\\activate.bat
echo ✅ Virtual environment activated: ${venvName}
python manage.py runserver 127.0.0.1:8000
pause
`;
        fs.writeFileSync(path.join(__dirname, 'start_backend.bat'), batchContent);
        console.log('✅ Created: start_backend.bat');
    } else {
        // Unix shell script
        const shellContent = `#!/bin/bash
echo "🚀 Starting VARANDA-POS Backend (${platform})"
cd "$(dirname "$0")"
source ${venvName}/bin/activate
echo "✅ Virtual environment activated: ${venvName}"
python manage.py runserver 127.0.0.1:8000
`;
        const scriptPath = path.join(__dirname, 'start_backend.sh');
        fs.writeFileSync(scriptPath, shellContent);
        fs.chmodSync(scriptPath, '755');
        console.log('✅ Created: start_backend.sh');
    }

    // Create cross-platform info file
    const infoContent = `# VARANDA-POS Virtual Environment Info
Platform: ${platform}
Architecture: ${os.arch()}
Virtual Environment: ${venvName}
Python Path: ${pythonExe}
Created: ${new Date().toISOString()}

## Usage:
### Windows:
- Run: start_backend.bat
- Or: ${venvName}\\Scripts\\activate.bat && python manage.py runserver

### Mac/Linux:
- Run: ./start_backend.sh  
- Or: source ${venvName}/bin/activate && python manage.py runserver

## Electron Auto-Detection:
The Electron app will automatically detect and use this virtual environment.
`;
    fs.writeFileSync(path.join(__dirname, 'VENV_INFO.md'), infoContent);
    console.log('✅ Created: VENV_INFO.md');
}

async function main() {
    try {
        console.log('\n' + '='.repeat(50));
        
        // Step 1: Check Python
        const pythonCmd = await checkPythonInstallation();
        
        // Step 2: Create virtual environment
        const venvPath = await setupVirtualEnvironment(pythonCmd);
        
        // Step 3: Install dependencies
        const { pythonExe } = await activateAndInstall(venvPath);
        
        // Step 4: Run migrations
        await runMigrations(pythonExe);
        
        // Step 5: Create startup scripts
        await createStartupScripts(venvPath, pythonExe);
        
        console.log('\n🎉 Setup completed successfully!');
        console.log('=' .repeat(50));
        console.log('✅ Virtual environment ready');
        console.log('✅ Dependencies installed');
        console.log('✅ Database migrated');
        console.log('✅ Startup scripts created');
        console.log('\n🚀 You can now run the application with:');
        console.log('   npm run dev');
        console.log('\n📝 Or start backend manually with:');
        if (isWindows) {
            console.log('   backend\\start_backend.bat');
        } else {
            console.log('   backend/start_backend.sh');
        }
        
    } catch (error) {
        console.error('\n❌ Setup failed:', error.message);
        console.error('\n💡 Troubleshooting:');
        console.error('1. Make sure Python 3.8+ is installed');
        console.error('2. Check if Python is in your PATH');
        console.error('3. Try running as administrator/sudo if needed');
        console.error('4. Check internet connection for package downloads');
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { main, checkPythonInstallation, setupVirtualEnvironment };