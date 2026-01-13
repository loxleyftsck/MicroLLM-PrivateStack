# Start MicroLLM-PrivateStack with Gunicorn (Production Mode)
# Windows PowerShell version

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Starting MicroLLM-PrivateStack" -ForegroundColor Green
Write-Host "Production Mode: Gunicorn + Gevent" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Cyan

# Create logs directory if not exists
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Stop existing processes
Write-Host "`nStopping existing servers..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*api_gateway*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start Gunicorn
Write-Host "`nStarting Gunicorn server..." -ForegroundColor Green
Set-Location backend

gunicorn `
    --config ../gunicorn_config.py `
    --chdir . `
    api_gateway:app

Write-Host "`nServer stopped." -ForegroundColor Red
