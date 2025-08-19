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

function startDjangoServer() {
  const isProd = app.isPackaged
  const basePath = isProd
    ? path.join(process.resourcesPath, 'backend')
    : path.join(__dirname, '../backend')

  const pythonPath = isProd
  ? path.join(process.resourcesPath, 'backend', 'python', 'python.exe')
  : path.join(basePath, 'python', 'python.exe')
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
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#ffffff',
      symbolColor: '#000000',
      height: 30
    },
    webPreferences: {
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  win.removeMenu()
  win.setMenuBarVisibility(false)

  if (app.isPackaged) {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  } else {
    win.loadURL('http://localhost:5173')
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
