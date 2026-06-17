<#
.SYNOPSIS
Run all Jinja tests mit automatischem Server-Start/Stop

.DESCRIPTION
1. Startet OVMS Server
2. Validiert Setup
3. Führt Phase 5 Tests aus (TC1-TC5)
4. Führt Phase 6 Tests aus (TC6-TC9)
5. Stoppt OVMS Server

.PARAMETER SkipPhase6
Skip Phase 6 Tests (nur Phase 5)

.EXAMPLE
.\run_all_tests.ps1
# Startet Server, Phase 5 & 6, stoppt Server

.\run_all_tests.ps1 -SkipPhase6
# Nur Phase 5
#>

param(
    [switch]$SkipPhase6 = $false
)

$ErrorActionPreference = "Stop"

$JinjaDir = "C:\LLM\jinja_deployment"
$TestsDir = "C:\LLM\jinja_tests"

Write-Host ""
Write-Host "╔" + ("=" * 68) + "╗"
Write-Host "║ Jinja-Template Test Suite (Complete Run)                          ║"
Write-Host "╚" + ("=" * 68) + "╝"
Write-Host ""

# Phase 1: Start Server
Write-Host "[1] Starting OVMS Server..."
Write-Host ""
& "$JinjaDir\start_ovms_server.ps1"

Write-Host ""
Write-Host "Waiting before tests (5 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Phase 2: Validate Setup
Write-Host ""
Write-Host "[2] Validating OVMS Setup..."
Write-Host ""
& "$JinjaDir\validate_ovms_setup.ps1"

# Phase 3: Run Tests
Write-Host ""
Write-Host "[3] Running Phase 5 Tests (TC1-TC5: File Operations)..."
Write-Host ""
python "$TestsDir\run_jinja_phase5.py"
$Phase5Exit = $LASTEXITCODE

Write-Host ""
if ($Phase5Exit -eq 0) {
    Write-Host "✓ Phase 5 Tests PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Phase 5 Tests FAILED" -ForegroundColor Red
}

# Phase 4: Optional Phase 6
if (-not $SkipPhase6) {
    Write-Host ""
    Write-Host "[4] Running Phase 6 Tests (TC6-TC9: Extended Tools)..."
    Write-Host ""
    python "$TestsDir\run_jinja_phase6.py"
    $Phase6Exit = $LASTEXITCODE

    Write-Host ""
    if ($Phase6Exit -eq 0) {
        Write-Host "✓ Phase 6 Tests PASSED" -ForegroundColor Green
    } else {
        Write-Host "❌ Phase 6 Tests FAILED" -ForegroundColor Red
    }
}

# Phase 5: Cleanup - Stop Server
Write-Host ""
Write-Host "[5] Stopping OVMS Server..."
Write-Host ""
& "$JinjaDir\stop_ovms_server.ps1"

# Summary
Write-Host ""
Write-Host "╔" + ("=" * 68) + "╗"
Write-Host "║ Test Suite Complete                                              ║"
Write-Host "╚" + ("=" * 68) + "╝"
Write-Host ""

Write-Host "Results:"
Write-Host "  Phase 5 (TC1-TC5):     $(if ($Phase5Exit -eq 0) { '✓ PASS' } else { '❌ FAIL' })"
if (-not $SkipPhase6) {
    Write-Host "  Phase 6 (TC6-TC9):     $(if ($Phase6Exit -eq 0) { '✓ PASS' } else { '❌ FAIL' })"
}

Write-Host ""
Write-Host "Test Results saved to:"
Write-Host "  Phase 5: C:\LLM\test_results\phase5_file_ops\Phase5-Test-Results.json"
if (-not $SkipPhase6) {
    Write-Host "  Phase 6: C:\LLM\test_results\phase6_extended_tools\Phase6-Test-Results.json"
}

Write-Host ""

# Exit with appropriate code
if ($SkipPhase6) {
    exit $Phase5Exit
} else {
    exit $(if ($Phase5Exit -eq 0 -and $Phase6Exit -eq 0) { 0 } else { 1 })
}
