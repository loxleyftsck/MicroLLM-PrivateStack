# Build MicroLLM PrivateStack Desktop App
# Run this script to create Windows installer

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "MicroLLM PrivateStack - Desktop App Builder" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Navigate to electron-app
Set-Location $PSScriptRoot\electron-app

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "Building Windows application..." -ForegroundColor Yellow
Write-Host "This may take several minutes..."
Write-Host ""

# Build
npm run build:win

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "BUILD COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output files:"
Write-Host "  Installer: electron-app\dist\MicroLLM PrivateStack Setup.exe"
Write-Host "  Portable:  electron-app\dist\MicroLLM PrivateStack.exe"
Write-Host ""
Write-Host "To run the installer:"
Write-Host "  .\electron-app\dist\MicroLLM PrivateStack Setup.exe"
