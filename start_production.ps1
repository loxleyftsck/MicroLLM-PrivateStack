# Production deployment script for MicroLLM-PrivateStack

param(
    [switch]$Development,
    [int]$Workers = 2,
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host "MicroLLM-PrivateStack Production Server"
Write-Host "============================================================"

if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Force -Path "logs" | Out-Null
}

$env:REDIS_ENABLED = "false"
try {
    $conn = Test-NetConnection -ComputerName localhost -Port 6379 -WarningAction SilentlyContinue
    if ($conn.TcpTestSucceeded) {
        Write-Host "Redis is running on port 6379"
        $env:REDIS_ENABLED = "true"
    }
    else {
        Write-Host "Redis not detected on localhost:6379"
    }
}
catch {
    Write-Host "Redis detection failed"
}

$env:API_HOST = "0.0.0.0"
$env:API_PORT = $Port
$env:GUNICORN_WORKERS = $Workers
$env:LOG_LEVEL = "info"

if ($Development) {
    Write-Host "Running in DEVELOPMENT mode"
    $env:DEBUG = "true"
    Set-Location backend
    python api_gateway.py
}
else {
    Write-Host "Running in PRODUCTION mode"
    Write-Host "   Workers: $Workers"
    Write-Host "   Port: $Port"
    
    $platform = [System.Environment]::OSVersion.Platform
    Set-Location backend
    
    if ($platform -eq "Unix") {
        gunicorn -c ../gunicorn.conf.py api_gateway:app
    }
    else {
        Write-Host "Windows detected - using Waitress"
        
        # Ensure waitress is installed
        pip install waitress --quiet
        
        Write-Host ("   URL: http://localhost:" + $Port)
        
        python -m waitress --port=$Port --threads=$Workers api_gateway:app
    }
}
