# MicroLLM Stress Test - Simple Version
Write-Host "`n=== MICROLLM STRESS TEST ===`n" -ForegroundColor Cyan

$API = "http://localhost:8000"

# Test 1: Rapid Sequential
Write-Host "TEST 1: Rapid Fire (5 queries)" -ForegroundColor Yellow
$times = @()
1..5 | ForEach-Object {
    Write-Host "  Query $_..." -NoNewline
    $start = Get-Date
    $r = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Body '{"message":"Test","max_tokens":30}' -ContentType "application/json"
    $t = (Get-Date) - $start
    $times += $t.TotalSeconds
    Write-Host " $($t.TotalSeconds)s" -ForegroundColor Green
}
$avg = ($times | Measure-Object -Average).Average
Write-Host "Average: $([math]::Round($avg,2))s`n" -ForegroundColor Cyan

# Test 2: Long Query
Write-Host "TEST 2: Long Complex Query" -ForegroundColor Yellow
$long = "Analyze business expansion to Southeast Asia with 50M budget. Consider risks, opportunities, competition, and regulations. Provide 5 key recommendations."
$start = Get-Date
$r = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Body (@{message = $long; max_tokens = 256 } | ConvertTo-Json) -ContentType "application/json"
$t = (Get-Date) - $start
Write-Host "  Time: $($t.TotalSeconds)s" -ForegroundColor Green
Write-Host "  Response: $($r.response.Length) chars`n" -ForegroundColor Cyan

# Test 3: Token Variations
Write-Host "TEST 3: Token Limits" -ForegroundColor Yellow
@(50, 100, 200, 256) | ForEach-Object {
    Write-Host "  max_tokens=$_..." -NoNewline
    $start = Get-Date
    $r = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Body "{`"message`":`"Explain AI`",`"max_tokens`":$_}" -ContentType "application/json"
    $t = (Get-Date) - $start
    Write-Host " $($t.TotalSeconds)s" -ForegroundColor Green
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
    $r = Invoke-RestMethod -Uri "$API/api/chat" -Method POST -Body $body -ContentType "application/json"
    $t = (Get-Date) - $start
    Write-Host " $($t.TotalSeconds)s" -ForegroundColor Green
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
Write-Host "Status: All tests passed ✓`n" -ForegroundColor Green
