/**
 * MicroLLM-PrivateStack Electron Main Process
 * Manages Python backend and Electron window
 */

const { app, BrowserWindow, Tray, Menu, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

// Configuration
const CONFIG = {
    PORT: 8000,
    PYTHON_STARTUP_TIMEOUT: 120000, // 2 minutes for model loading
    CHECK_INTERVAL: 1000,
};

let mainWindow = null;
let splashWindow = null;
let tray = null;
let pythonProcess = null;
let isQuitting = false;

// Get resource paths
function getResourcePath(relativePath) {
    if (app.isPackaged) {
        return path.join(process.resourcesPath, relativePath);
    }
    return path.join(__dirname, '..', relativePath);
}

// Create splash screen
function createSplashWindow() {
    splashWindow = new BrowserWindow({
        width: 500,
        height: 350,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        resizable: false,
        center: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        }
    });

    splashWindow.loadFile(path.join(__dirname, 'splash.html'));
    splashWindow.setSkipTaskbar(true);
}

// Create main window
function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        title: 'MicroLLM PrivateStack',
        icon: path.join(__dirname, 'icon.png'),
        show: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    mainWindow.loadURL(`http://localhost:${CONFIG.PORT}`);

    mainWindow.once('ready-to-show', () => {
        if (splashWindow) {
            splashWindow.close();
            splashWindow = null;
        }
        mainWindow.show();
        mainWindow.focus();
    });

    mainWindow.on('close', (event) => {
        if (!isQuitting) {
            event.preventDefault();
            mainWindow.hide();
            return false;
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

// Create system tray
function createTray() {
    tray = new Tray(path.join(__dirname, 'icon.png'));
    
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Open MicroLLM',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                    mainWindow.focus();
                }
            }
        },
        {
            label: 'Admin Dashboard',
            click: () => {
                shell.openExternal(`http://localhost:${CONFIG.PORT}/admin.html`);
            }
        },
        { type: 'separator' },
        {
            label: 'Restart Server',
            click: () => {
                restartPythonServer();
            }
        },
        { type: 'separator' },
        {
            label: 'Quit',
            click: () => {
                isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setToolTip('MicroLLM PrivateStack');
    tray.setContextMenu(contextMenu);

    tray.on('double-click', () => {
        if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
        }
    });
}

// Start Python backend
function startPythonServer() {
    return new Promise((resolve, reject) => {
        // First check if server is already running
        http.get(`http://localhost:${CONFIG.PORT}/health`, (res) => {
            if (res.statusCode === 200) {
                console.log('Server is already running!');
                resolve();
                return;
            }
        }).on('error', () => {
            // Server not running, start it
            launchPythonProcess(resolve, reject);
        });
    });
}

function launchPythonProcess(resolve, reject) {
    const backendPath = getResourcePath('backend');
    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';

    console.log('Starting Python server...');
    console.log('Backend path:', backendPath);

    pythonProcess = spawn(pythonPath, [
        '-m', 'waitress',
        '--host=0.0.0.0',
        `--port=${CONFIG.PORT}`,
        'api_gateway:app'
    ], {
        cwd: backendPath,
        env: {
            ...process.env,
            PYTHONUNBUFFERED: '1',
            PYTHONIOENCODING: 'utf-8',
            MODEL_PATH: getResourcePath('models/deepseek-r1-1.5b-q4.gguf')
        }
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[Python] ${data.toString().trim()}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.log(`[Python] ${data.toString().trim()}`);
    });

    pythonProcess.on('error', (err) => {
        console.error('Failed to start Python:', err);
        reject(err);
    });

    pythonProcess.on('exit', (code) => {
        console.log(`Python exited with code ${code}`);
        if (!isQuitting && code !== 0) {
            dialog.showErrorBox('Server Error', 
                'The backend server has stopped unexpectedly. Please restart the application.');
        }
    });

    // Wait for server to be ready
    waitForServer(resolve, reject);
}

// Wait for server to respond
function waitForServer(resolve, reject) {
    const startTime = Date.now();

    const check = () => {
        if (Date.now() - startTime > CONFIG.PYTHON_STARTUP_TIMEOUT) {
            reject(new Error('Server startup timeout'));
            return;
        }

        http.get(`http://localhost:${CONFIG.PORT}/health`, (res) => {
            if (res.statusCode === 200) {
                console.log('Server is ready!');
                resolve();
            } else {
                setTimeout(check, CONFIG.CHECK_INTERVAL);
            }
        }).on('error', () => {
            setTimeout(check, CONFIG.CHECK_INTERVAL);
        });
    };

    setTimeout(check, 2000); // Initial delay for server startup
}

// Restart Python server
async function restartPythonServer() {
    if (pythonProcess) {
        pythonProcess.kill();
    }

    try {
        await startPythonServer();
        if (mainWindow) {
            mainWindow.reload();
        }
    } catch (error) {
        dialog.showErrorBox('Restart Failed', error.message);
    }
}

// Stop Python server
function stopPythonServer() {
    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
    }
}

// App lifecycle
app.whenReady().then(async () => {
    createSplashWindow();
    createTray();

    try {
        await startPythonServer();
        createMainWindow();
    } catch (error) {
        if (splashWindow) splashWindow.close();
        dialog.showErrorBox('Startup Error', 
            `Failed to start the server:\n${error.message}\n\nMake sure Python and required packages are installed.`);
        app.quit();
    }
});

app.on('window-all-closed', () => {
    // Keep running in system tray
});

app.on('activate', () => {
    if (mainWindow === null) {
        createMainWindow();
    } else {
        mainWindow.show();
    }
});

app.on('before-quit', () => {
    isQuitting = true;
    stopPythonServer();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('Uncaught exception:', error);
    dialog.showErrorBox('Error', error.message);
});
