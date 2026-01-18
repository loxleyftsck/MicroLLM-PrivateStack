# Compile the LaTeX paper
# This script compiles paper.tex to PDF using pdflatex and bibtex

Write-Host "=== Compiling MicroLLM-PrivateStack Paper ===" -ForegroundColor Green

# Check if pdflatex is installed
try {
    $version = pdflatex --version
    Write-Host "pdflatex found: OK" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: pdflatex not found!" -ForegroundColor Red
    Write-Host "Please install MiKTeX from: https://miktex.org/download" -ForegroundColor Yellow
    exit 1
}

# Check if bibtex is installed
try {
    $version = bibtex --version
    Write-Host "bibtex found: OK" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: bibtex not found!" -ForegroundColor Red
    Write-Host "Please install MiKTeX from: https://miktex.org/download" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nCompiling LaTeX document..." -ForegroundColor Cyan

# First pass: generate .aux file
Write-Host "`n[1/4] First pdflatex pass..." -ForegroundColor Yellow
pdflatex -interaction=nonstopmode paper.tex
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: First pdflatex pass failed!" -ForegroundColor Red
    exit 1
}

# Process bibliography
Write-Host "`n[2/4] Processing bibliography with bibtex..." -ForegroundColor Yellow
bibtex paper
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: bibtex encountered issues, continuing..." -ForegroundColor Yellow
}

# Second pass: resolve citations
Write-Host "`n[3/4] Second pdflatex pass..." -ForegroundColor Yellow
pdflatex -interaction=nonstopmode paper.tex
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Second pdflatex pass failed!" -ForegroundColor Red
    exit 1
}

# Third pass: resolve cross-references
Write-Host "`n[4/4] Third pdflatex pass..." -ForegroundColor Yellow
pdflatex -interaction=nonstopmode paper.tex
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Third pdflatex pass failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Compilation Complete! ===" -ForegroundColor Green
Write-Host "Output file: paper.pdf" -ForegroundColor Cyan

# Clean up auxiliary files (optional)
$cleanup = Read-Host "`nClean up auxiliary files (.aux, .log, .bbl, etc.)? [y/N]"
if ($cleanup -eq "y" -or $cleanup -eq "Y") {
    Write-Host "Cleaning up..." -ForegroundColor Yellow
    Remove-Item -ErrorAction SilentlyContinue *.aux, *.log, *.bbl, *.blg, *.out, *.toc, *.lof, *.lot
    Write-Host "Cleanup complete!" -ForegroundColor Green
}

Write-Host "`nYou can now open paper.pdf to view your compiled document." -ForegroundColor Green
