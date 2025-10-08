import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🚀 Starting VARANDA POS Development...\n');

// Start Vite
console.log('🎨 Starting Vite dev server...');
const viteProcess = spawn('npx', ['vite'], {
  stdio: 'inherit',
  shell: true
});

// Wait for Vite to start, then launch Electron
setTimeout(() => {
  console.log('\n💻 Starting Electron...');
  
  const electronProcess = spawn('npx', ['electron', '.'], {
    stdio: 'inherit',
    shell: true
  });

  electronProcess.on('close', () => {
    console.log('Electron closed');
    viteProcess.kill();
    process.exit(0);
  });
}, 5000);

// Handle termination
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down...');
  process.exit(0);
});