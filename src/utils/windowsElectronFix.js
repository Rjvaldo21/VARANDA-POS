/**
 * Simple Windows Electron Fix
 * Just reload the page after save operations
 */

export function reloadAfterSave(delay = 500) {
  if (window.electronAPI && navigator.platform.includes('Win')) {
    setTimeout(() => {
      console.log('🔄 Windows Electron: Reloading page after save')
      window.location.reload()
    }, delay)
  }
}

export default reloadAfterSave