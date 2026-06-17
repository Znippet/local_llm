<#
.SYNOPSIS
Pre-Test Health Check für OVMS Jinja-Template Setup

.DESCRIPTION
Validiert:
- OVMS-Prozess läuft
- Jinja-Template existiert
- API-Endpoint erreichbar
- Qwen3-Coder Model geladen

.EXAMPLE
.\validate_ovms_setup.ps1
#>

$ErrorActionPreference = "Continue"

Write-Host "=" * 70
Write-Host "OVMS Setup Validation"
Write-Host "=" * 70
Write-Host ""

$AllPass = $true

# 1. Check OVMS Process
Write-Host "[1] OVMS Process Check..."
$ovms = Get-Process ovms -ErrorAction SilentlyContinue
if ($ovms) {
    Write-Host "    ✓ OVMS running (PID: $($ovms.Id))" -ForegroundColor Green
} else {
    Write-Host "    ❌ OVMS not running!" -ForegroundColor Red
    $AllPass = $false
}

# 2. Check Template File
Write-Host "[2] Jinja-Template Check..."
$template = "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja"
if (Test-Path $template) {
    $size = (Get-Item $template).Length / 1KB
    Write-Host "    ✓ Template found ($($size)KB): $(Split-Path $template -Leaf)" -ForegroundColor Green
} else {
    Write-Host "    ❌ Template missing: $template" -ForegroundColor Red
    $AllPass = $false
}

# 3. Check API Endpoint
Write-Host "[3] API Endpoint Check..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9000/v3/models/qwen3-coder-30b-a3b-instruct-int4-ov" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "    ✓ API responsive (HTTP 200)" -ForegroundColor Green
    } else {
        Write-Host "    ⚠️  API responded but status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "    ❌ API endpoint not responding: $($_)" -ForegroundColor Red
    $AllPass = $false
}

# 4. Try Model Query
Write-Host "[4] Model Availability Check..."
try {
    $result = Invoke-RestMethod -Uri "http://localhost:9000/v3/models/qwen3-coder-30b-a3b-instruct-int4-ov" -Method Get -TimeoutSec 5
    if ($result) {
        Write-Host "    ✓ Model responding: Qwen3-Coder-30B-A3B (INT4)" -ForegroundColor Green
    }
} catch {
    Write-Host "    ⚠️  Could not query model details" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 70

if ($AllPass) {
    Write-Host "✓ All checks passed - Ready for testing!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Run tests with:"
    Write-Host "  python C:\LLM\jinja_tests\run_jinja_phase5.py  # File Ops (TC1-TC5)"
    Write-Host "  python C:\LLM\jinja_tests\run_jinja_phase6.py  # Extended Tools (TC6-TC9)"
    Write-Host ""
    exit 0
} else {
    Write-Host "⚠️  Some checks failed - Review issues above" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Fix OVMS:"
    Write-Host "  cd C:\LLM && .\start_ovms_qwen.bat"
    Write-Host ""
    exit 1
}
