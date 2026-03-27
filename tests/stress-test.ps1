# MicroLLM Stress Test
# UPDATED (2026-03-26): Added JWT auth header to all /api/chat requests.
Write-Host "`n=== MICROLLM STRESS TEST ===`n" -ForegroundColor Cyan

$API  = "http://localhost:8000"
$PASS = 0
$FAIL = 0

# Load JWT token
if (!(Test-Path "test_token.txt")) {
    Write-Host "ERROR: test_token.txt not found. Run: python scripts/create_test_user.py" -ForegroundColor Red
    exit 1
}
$TOKEN = (Get-Content "test_token.txt").Trim()
$H = @{ "Authorization" = "Bearer $TOKEN"; "Content-Type" = "application/json" }

# Test 1: Rapid Sequential
Write-Host "TEST 1: Rapid Fire (5 queries)" -ForegroundColor Yellow
$times = @()
1..5 | ForEach-Object {
    Write-Host "  Query $_..." -NoNewline
    $start = Get-Date
    try {
        $null = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Headers $H -Body '{"message":"Test","max_tokens":30}'
        $t = (Get-Date) - $start
        $times += $t.TotalSeconds
        Write-Host " $($t.TotalSeconds)s" -ForegroundColor Green
        $script:PASS++
    } catch { Write-Host " FAIL: $_" -ForegroundColor Red; $script:FAIL++ }
}
$avg = ($times | Measure-Object -Average).Average
Write-Host "Average: $([math]::Round($avg,2))s`n" -ForegroundColor Cyan

# Test 2: Long Query
Write-Host "TEST 2: Long Complex Query" -ForegroundColor Yellow
$long = "Analyze business expansion to Southeast Asia with 50M budget. Consider risks, opportunities, competition, and regulations. Provide 5 key recommendations."
$t2 = $null
try {
    $start = Get-Date
    $resp2 = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Headers $H -Body (@{message = $long; max_tokens = 256 } | ConvertTo-Json)
    $t2 = (Get-Date) - $start
    Write-Host "  Time: $($t2.TotalSeconds)s" -ForegroundColor Green
    Write-Host "  Response: $($resp2.response.Length) chars`n" -ForegroundColor Cyan
    $PASS++
} catch {
    Write-Host "  FAIL: $_" -ForegroundColor Red
    $FAIL++
}

# Test 3: Token Variations
Write-Host "TEST 3: Token Limits" -ForegroundColor Yellow
@(50, 100, 200, 256) | ForEach-Object {
    Write-Host "  max_tokens=$_..." -NoNewline
    $start = Get-Date
    try {
        $null = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Headers $H -Body "{`"message`":`"Explain AI`",`"max_tokens`":$_}"
        $t = (Get-Date) - $start
        Write-Host " $($t.TotalSeconds)s" -ForegroundColor Green; $script:PASS++
    } catch { Write-Host " FAIL" -ForegroundColor Red; $script:FAIL++ }
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
    $body = @{message = $_; max_tokens = 80 } | ConvertTo-Json
    try {
        $null = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Headers $H -Body $body
        $t = (Get-Date) - $start
        Write-Host " $($t.TotalSeconds)s" -ForegroundColor Green; $script:PASS++
    } catch { Write-Host " FAIL" -ForegroundColor Red; $script:FAIL++ }
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
$total = $PASS + $FAIL
Write-Host "=== SUMMARY ==" -ForegroundColor Cyan
Write-Host "Chat avg    : $([math]::Round($avg,2))s" -ForegroundColor Green
Write-Host "Health avg  : $([math]::Round($havg,2))ms" -ForegroundColor Green
Write-Host "Pass/Fail   : $PASS/$total" -ForegroundColor $(if ($FAIL -eq 0) { 'Green' } else { 'Red' })
if ($FAIL -gt 0) { exit 1 }
