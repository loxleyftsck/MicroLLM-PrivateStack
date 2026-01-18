# MicroLLM PrivateStack - Electron Desktop App

## Overview
This is the desktop application wrapper for MicroLLM PrivateStack. It bundles the Python backend with a native Electron frontend for a seamless desktop experience.

## Features
- 🖥️ Native desktop application
- 🚀 Auto-starts Python backend
- 📌 System tray integration
- 🔄 Background operation
- 🎨 Beautiful splash screen during loading
- 📦 Portable or installer options

## Requirements
- Node.js 18+ and npm
- Python 3.10+ with pip
- All Python dependencies installed (see main requirements.txt)

## Development

### Install dependencies
```bash
cd electron-app
npm install
```

### Run in development mode
```bash
npm start
```

## Building

### Build for Windows
```bash
npm run build:win
```
Outputs:
- `dist/MicroLLM PrivateStack Setup.exe` (Installer)
- `dist/MicroLLM PrivateStack.exe` (Portable)

### Build for macOS
```bash
npm run build:mac
```
Output: `dist/MicroLLM PrivateStack.dmg`

### Build for Linux
```bash
npm run build:linux
```
Outputs:
- `dist/MicroLLM PrivateStack.AppImage`
- `dist/microllm-privatestack.deb`

## Project Structure
```
electron-app/
├── main.js          # Electron main process
├── preload.js       # Secure IPC bridge
├── splash.html      # Loading screen
├── icon.png         # App icon
├── package.json     # NPM config
├── build/           # Build resources
│   └── icon.png     # Icon for builds
└── dist/            # Built applications
```

## How It Works

1. **Startup**: Electron launches and shows splash screen
2. **Backend**: Spawns Python process running Waitress server
3. **Health Check**: Polls `/api/health` until server is ready
4. **Main Window**: Loads the web UI from localhost:8000
5. **System Tray**: Runs in background when closed
6. **Shutdown**: Terminates Python process on quit

## Configuration

Environment variables can be set in `main.js`:
- `CONFIG.PORT` - Server port (default: 8000)
- `CONFIG.PYTHON_STARTUP_TIMEOUT` - Max wait time for server (default: 120s)

## Troubleshooting

### "Failed to start server" error
- Ensure Python is in PATH
- Install dependencies: `pip install -r requirements.txt`
- Check if port 8000 is available

### Slow startup
- First launch loads the AI model (~1GB)
- Subsequent launches are faster due to caching

### App doesn't close
- Use system tray icon to quit properly
