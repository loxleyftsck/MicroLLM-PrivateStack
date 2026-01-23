/**
 * Preload script for secure IPC communication
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to renderer
contextBridge.exposeInMainWorld('electronAPI', {
    // App info
    getVersion: () => require('./package.json').version,
    
    // System
    platform: process.platform,
    
    // Notifications (if needed in future)
    onNotification: (callback) => ipcRenderer.on('notification', callback),
});
