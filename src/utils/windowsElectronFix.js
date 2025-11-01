/**
 * Windows Electron Input Fixes
 * Multiple approaches for fixing input issues
 */

// Approach 1: Reload page
export function reloadAfterSave(delay = 500) {
  if (window.electronAPI && navigator.platform.includes('Win')) {
    setTimeout(() => {
      console.log('🔄 Windows Electron: Reloading page after save')
      window.location.reload()
    }, delay)
  }
}

// Approach 2: IPC-based input fix
export async function fixInputsViaIPC() {
  if (window.electronAPI && navigator.platform.includes('Win')) {
    try {
      const result = await window.electronAPI.fixInputs()
      console.log('🔄 Windows Electron: IPC input fix result:', result)
      return result
    } catch (error) {
      console.error('❌ IPC input fix failed:', error)
      return false
    }
  }
  return false
}

// Approach 3: Direct DOM fix
export function fixInputsDirectly() {
  if (navigator.platform.includes('Win')) {
    const inputs = document.querySelectorAll('input, textarea, select, button')
    inputs.forEach(input => {
      input.disabled = false
      input.readOnly = false
    })
    console.log('🔄 Windows Electron: Direct DOM fix applied to', inputs.length, 'inputs')
    return inputs.length
  }
  return 0
}

// Combined approach
export async function fixInputsAfterSave(useIPC = true) {
  if (window.electronAPI && navigator.platform.includes('Win')) {
    console.log('🔄 Windows Electron: Applying input fix after save...')
    
    // Try IPC first
    if (useIPC) {
      const ipcResult = await fixInputsViaIPC()
      if (ipcResult) {
        console.log('✅ IPC fix successful')
        return
      }
    }
    
    // Fallback to direct DOM fix
    setTimeout(() => {
      const count = fixInputsDirectly()
      if (count > 0) {
        console.log('✅ Direct DOM fix successful')
      } else {
        console.log('⚠️ No inputs found, trying page reload...')
        reloadAfterSave(1000)
      }
    }, 200)
  }
}

export default fixInputsAfterSave