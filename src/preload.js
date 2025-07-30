const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  selectFile: () => ipcRenderer.invoke('select-file'),
  
  // OpenAI API
  generateSummary: (data) => ipcRenderer.invoke('generate-summary', data),
  
  // Settings
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  getSettings: () => ipcRenderer.invoke('get-settings'),
  
  // Platform info
  platform: process.platform
});

// DOM helpers
contextBridge.exposeInMainWorld('domAPI', {
  // Safe DOM manipulation helpers
  ready: (callback) => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', callback);
    } else {
      callback();
    }
  }
});