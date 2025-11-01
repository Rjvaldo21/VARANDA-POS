const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  printReceipt: (data) => ipcRenderer.send('print-receipt', data),
  onPrintStatus: (callback) => ipcRenderer.on('print-status', (_event, status) => callback(status)),
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
  fixInputs: () => ipcRenderer.invoke('fix-inputs'),
})
