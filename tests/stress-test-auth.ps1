# MicroLLM Stress Test - Authenticated Version
Write-Host "`n=== MICROLLM STRESS TEST (AUTH) ===`n" -ForegroundColor Cyan

$API = "http://localhost:8000"

# Get auth token
if (!(Test-Path "test_token.txt")) {
    Write-Host "ERROR: test_token.txt not found. Run create_test_user.py first!" -ForegroundColor Red
    exit 1
}

$TOKEN = (Get-Content "test_token.txt").Trim()
$HEADERS = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type"  = "application/json"
}

Write-Host "Using auth token: $($TOKEN.Substring(0,20))..." -ForegroundColor Gray
Write-Host ""

# Test 1: Rapid Sequential
Write-Host "TEST 1: Rapid Fire (5 queries)" -ForegroundColor Yellow
$times = @()
1..5 | ForEach-Object {
    Write-Host "  Query $_..." -NoNewline
    $start = Get-Date
    try {
        $r = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Headers $HEADERS -Body '{"message":"Test","max_tokens":30}'
        $t = (Get-Date) - $start
        $times += $t.TotalSeconds
        Write-Host " $($t.TotalSeconds)s" -ForegroundColor Green
    }
    catch {
        Write-Host " FAILED: $_" -ForegroundColor Red
    }
}
$avg = ($times | Measure-Object -Average).Average
Write-Host "Average: $([math]::Round($avg,2))s`n" -ForegroundColor Cyan

# Test 2: Long Query
Write-Host "TEST 2: Long Complex Query" -ForegroundColor Yellow
$long = "Analyze business expansion to Southeast Asia with 50M budget. Consider risks, opportunities, competition, and regulations. Provide 5 key recommendations."
$start = Get-Date
try {
    $r = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Headers $HEADERS -Body (@{message = $long; max_tokens = 256 } | ConvertTo-Json)
    $t = (Get-Date) - $start
    Write-Host "  Time: $($t.TotalSeconds)s" -ForegroundColor Green
    Write-Host "  Response: $($r.response.Length) chars`n" -ForegroundColor Cyan
}
catch {
    Write-Host "  FAILED: $_`n" -ForegroundColor Red
}

# Test 3: Token Variations
Write-Host "TEST 3: Token Limits" -ForegroundColor Yellow
@(50, 100, 200, 256) | ForEach-Object {
    Write-Host "  max_tokens=$_..." -NoNewline
    $start = Get-Date
    try {
        $r = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Headers $HEADERS -Body "{`"message`":`"Explain AI`",`"max_tokens`":$_}"
        $t = (Get-Date) - $start
        Write-Host " $($t.TotalSeconds)s" -ForegroundColor Green
    }
    catch {
        Write-Host " FAILED" -ForegroundColor Red
    }
}
Write-Host ""

# Test 4: Languages 
Write-Host "TEST 4: Multilingual" -ForegroundColor Yellow
@(
    "What is AI?",
    "Apa itu kecerdasan buatan?",
    "Explain cloud computing"
) | ForEach-Object {
    Write-Host "  $_..." -NoNewline
    $start = Get-Date
    try {
        $body = @{message = $_; max_tokens = 80 } | ConvertTo-Json
        $r = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Headers $HEADERS -Body $body
        $t = (Get-Date) - $start
        Write-Host " $($t.TotalSeconds)s" -ForegroundColor Green
    }
    catch {
        Write-Host " FAILED" -ForegroundColor Red
    }
}
Write-Host ""

# Test 5: Health Spam
Write-Host "TEST 5: Health Check Spam (20x)" -ForegroundColor Yellow
$htimes = @()
1..20 | ForEach-Object {
    $start = Get-Date
    Invoke-RestMethod -Uri "$API/health" | Out-Null
    $htimes += ((Get-Date) - $start).TotalMilliseconds
}
$havg = ($htimes | Measure-Object -Average).Average
Write-Host "  Average: $([math]::Round($havg,2))ms`n" -ForegroundColor Green

# Summary
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Chat avg: $([math]::Round($avg,2))s" -ForegroundColor Green
Write-Host "Health avg: $([math]::Round($havg,2))ms" -ForegroundColor Green
Write-Host "Status: All tests completed`n" -ForegroundColor Green
