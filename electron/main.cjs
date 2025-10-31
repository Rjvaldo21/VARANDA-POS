const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let djangoProcess = null

const fs = require('fs')

function prepareDatabase() {
  const isProd = app.isPackaged

  const packedDb = isProd
    ? path.join(process.resourcesPath, 'resources', 'data', 'db.sqlite3')
    : path.join(__dirname, '../resources/data/db.sqlite3')

  const userDataDir = app.getPath('userData')
  const userDbPath = path.join(userDataDir, 'db.sqlite3')

  if (!fs.existsSync(userDataDir)) {
    fs.mkdirSync(userDataDir, { recursive: true })
  }

  if (!fs.existsSync(userDbPath)) {
    try {
      fs.copyFileSync(packedDb, userDbPath)
      console.log('✅ DB copied to:', userDbPath)
    } catch (err) {
      console.error('❌ Failed to copy DB:', err)
    }
  }

  return userDbPath
}

function getPythonPath(basePath, isProd) {
  if (isProd) {
    // Production: Use bundled Python
    return process.platform === 'win32' 
      ? path.join(process.resourcesPath, 'backend', 'python', 'python.exe')
      : path.join(process.resourcesPath, 'backend', 'python', 'python3')
  } else {
    // Development: Auto-detect virtual environment
    const isWindows = process.platform === 'win32'
    const isDarwin = process.platform === 'darwin'
    
    // Try different virtual environment paths in order of preference
    const venvPaths = isWindows 
      ? [
          path.join(basePath, 'venv', 'Scripts', 'python.exe'),
          path.join(basePath, 'env', 'Scripts', 'python.exe'),
          'python.exe',
          'python'
        ]
      : [
          path.join(basePath, 'venv_mac', 'bin', 'python'),
          path.join(basePath, 'venv', 'bin', 'python'),
          path.join(basePath, 'env', 'bin', 'python'),
          'python3',
          'python'
        ]
    
    // Check which Python path exists and is executable
    for (const pythonPath of venvPaths) {
      try {
        if (path.isAbsolute(pythonPath)) {
          if (fs.existsSync(pythonPath)) {
            console.log(`✅ Found Python at: ${pythonPath}`)
            return pythonPath
          }
        } else {
          // For system Python, we'll try it anyway
          console.log(`🔄 Trying system Python: ${pythonPath}`)
          return pythonPath
        }
      } catch (error) {
        console.log(`❌ Python path not found: ${pythonPath}`)
      }
    }
    
    // Fallback to system Python
    console.log('⚠️ No virtual environment found, using system Python')
    return isWindows ? 'python.exe' : 'python3'
  }
}

function startDjangoServer() {
  const isProd = app.isPackaged
  const basePath = isProd
    ? path.join(process.resourcesPath, 'backend')
    : path.join(__dirname, '../backend')

  const pythonPath = getPythonPath(basePath, isProd)
  const managePyPath = path.join(basePath, 'manage.py')
  const userDbPath = prepareDatabase()  

  const envWithDb = {
    ...process.env,
    USER_DATA_PATH: path.dirname(userDbPath),
    PYTHONPATH: basePath
  }

  const migrateProcess = spawn(pythonPath, [managePyPath, 'migrate'], {
    cwd: basePath,
    env: envWithDb
  })

  migrateProcess.stdout.on('data', (data) => {
    console.log(`⚙️ Django Migrate: ${data}`)
  })

  migrateProcess.stderr.on('data', (data) => {
    console.error(`❌ Django Migrate Error: ${data}`)
  })

  migrateProcess.on('close', (code) => {
    console.log(`✅ Django migrate selesai dengan kode ${code}`)

    djangoProcess = spawn(pythonPath, [managePyPath, 'runserver', '127.0.0.1:8000'], {
      cwd: basePath,
      env: envWithDb
    })

    djangoProcess.stdout.on('data', (data) => {
      console.log(`📡 Django: ${data}`)
    })

    djangoProcess.stderr.on('data', (data) => {
      console.error(`❌ Django Error: ${data}`)
    })

    djangoProcess.on('close', (code) => {
      console.log(`🔚 Django process exited with code ${code}`)
    })
  })
}


function stopDjangoServer() {
  if (djangoProcess) {
    djangoProcess.kill()
    console.log('🛑 Django server stopped.')
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1024,
    height: 700,
    minWidth: 800,
    minHeight: 600,
    backgroundColor: '#ffffff',
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  win.removeMenu()
  win.setMenuBarVisibility(false)

  // Show window only after content is loaded to prevent input focus issues
  win.once('ready-to-show', () => {
    win.show()
    win.focus()
  })

  // Add event listeners for Windows-specific input issues
  win.webContents.on('dom-ready', () => {
    console.log('🎯 DOM ready - enabling input focus')
    win.webContents.executeJavaScript(`
      // Force enable all inputs on Windows
      document.addEventListener('DOMContentLoaded', function() {
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
          input.removeAttribute('disabled');
          input.style.pointerEvents = 'auto';
          input.style.userSelect = 'text';
        });
      });
      
      // Ensure inputs work after page loads
      setTimeout(() => {
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
          input.removeAttribute('disabled');
          input.style.pointerEvents = 'auto';
          input.style.userSelect = 'text';
        });
      }, 1000);
    `)
  })

  if (app.isPackaged) {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  } else {
    // Try different ports that Vite might use
    const tryLoadURL = async (ports) => {
      for (const port of ports) {
        try {
          const url = `http://localhost:${port}`
          console.log(`🔗 Trying to load: ${url}`)
          await win.loadURL(url)
          console.log(`✅ Successfully loaded: ${url}`)
          return
        } catch (error) {
          console.log(`❌ Failed to load port ${port}, trying next...`)
        }
      }
      console.error('❌ Could not connect to Vite dev server on any port')
    }
    
    // Try common Vite ports
    tryLoadURL([5173, 5174, 5175, 3000])
  }
}

ipcMain.on('print-receipt', (event, data) => {
  console.log('🖨️ Print data:', data)
  event.sender.send('print-status', 'success')
})

ipcMain.handle('open-file-dialog', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openFile']
  })
  return canceled ? null : filePaths[0]
})

app.whenReady().then(() => {
  startDjangoServer()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  stopDjangoServer()
  if (process.platform !== 'darwin') app.quit()
})
