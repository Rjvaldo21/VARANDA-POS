import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🚀 Starting VARANDA POS Development Environment...\n');

// Start Django server
console.log('📡 Starting Django backend server...');
const djangoProcess = spawn('python3', ['manage.py', 'migrate'], {
  cwd: join(__dirname, 'backend'),
  stdio: 'pipe',
  env: { ...process.env }
});

djangoProcess.stdout.on('data', (data) => {
  console.log(`[Django Migrate] ${data.toString().trim()}`);
});

djangoProcess.stderr.on('data', (data) => {
  console.error(`[Django Migrate Error] ${data.toString().trim()}`);
});

djangoProcess.on('close', (code) => {
  console.log(`✅ Django migration completed with code ${code}`);
  
  // Start Django server after migration
  const serverProcess = spawn('python3', ['manage.py', 'runserver', '127.0.0.1:8000'], {
    cwd: join(__dirname, 'backend'),
    stdio: 'pipe',
    env: { ...process.env }
  });

  serverProcess.stdout.on('data', (data) => {
    const output = data.toString().trim();
    if (output.includes('Starting development server')) {
      console.log('✅ Django backend server is running at http://localhost:8000/api/');
    }
    console.log(`[Django] ${output}`);
  });

  serverProcess.stderr.on('data', (data) => {
    console.error(`[Django Error] ${data.toString().trim()}`);
  });
});

// Wait a bit for Django to start before launching frontend
setTimeout(() => {
  console.log('\n🎨 Starting Vite + Electron frontend...');
  
  const frontendProcess = spawn('npm', ['run', 'dev'], {
    shell: true,
    stdio: 'inherit'
  });

  frontendProcess.on('error', (error) => {
    console.error('Failed to start frontend:', error);
  });
}, 3000);

// Handle process termination
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down development environment...');
  process.exit(0);
});