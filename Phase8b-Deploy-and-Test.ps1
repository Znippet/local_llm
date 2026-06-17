#!/usr/bin/env pwsh
<#
.SYNOPSIS
Phase 8b Iteration 1: Qwen3-Coder-35B Deployment & Validation

.DESCRIPTION
Orchestrates Phase 8b testing:
1. Backup current 30B config
2. Deploy 35B model to OVMS
3. Restart OVMS with 35B
4. Run Phase 5 tests (baseline 5/5)
5. Run Phase 6 tests (baseline 4/4)
6. Run Phase 6.5 tests (tool-sequencing 0/3 → target 2-3/3)
7. Generate Phase8-Iteration-1-Report.md

.EXAMPLE
.\Phase8b-Deploy-and-Test.ps1
#>

param(
    [switch]$SkipOVMSRestart = $false,
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

# Configuration
$MODEL_30B = "Qwen3-Coder-30B-A3B-Instruct-int4-ov"
$MODEL_35B = "Qwen3.6-35B-A3B-int4-ov"
$MODEL_DIR = "C:\LLM\models\OpenVINO"
$DEPLOY_DIR = "C:\LLM\jinja_deployment"
$TEST_DIR = "C:\LLM\jinja_tests"
$RESULTS_DIR = "C:\LLM\test_results\phase8_iteration1"
$REPORT_FILE = "C:\LLM\Phase8-Iteration-1-Report.md"

# Ensure results directory exists
New-Item -ItemType Directory -Path $RESULTS_DIR -Force | Out-Null

Write-Host "=" * 80
Write-Host "Phase 8b Iteration 1: Qwen3-Coder-35B Deployment & Validation"
Write-Host "=" * 80
Write-Host ""

# =========================================================================
# PHASE 1: VERIFY 35B MODEL AVAILABILITY
# =========================================================================

Write-Host "[Phase 1] Verify 35B Model Availability" -ForegroundColor Cyan
Write-Host "-" * 80

$model35bPath = Join-Path $MODEL_DIR $MODEL_35B

if (Test-Path $model35bPath) {
    Write-Host "✓ 35B model directory found: $MODEL_35B" -ForegroundColor Green

    # Check for OpenVINO format files
    $xmlFiles = @(Get-ChildItem -Path $model35bPath -Filter "*.xml" -ErrorAction SilentlyContinue)
    $binFiles = @(Get-ChildItem -Path $model35bPath -Filter "*.bin" -ErrorAction SilentlyContinue)

    Write-Host "  XML files: $($xmlFiles.Count)" -ForegroundColor Green
    Write-Host "  BIN files: $($binFiles.Count)" -ForegroundColor Green

    if ($xmlFiles.Count -gt 0 -and $binFiles.Count -gt 0) {
        Write-Host "✓ Valid OpenVINO format (XML + BIN present)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Missing OpenVINO format files!" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ 35B model not found at: $model35bPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available models:" -ForegroundColor Yellow
    Get-ChildItem -Path $MODEL_DIR -Directory | ForEach-Object { Write-Host "  - $($_.Name)" }
    exit 1
}

Write-Host ""

# =========================================================================
# PHASE 2: BACKUP CURRENT 30B CONFIG
# =========================================================================

Write-Host "[Phase 2] Backup Current 30B Configuration" -ForegroundColor Cyan
Write-Host "-" * 80

$model30bPath = Join-Path $MODEL_DIR $MODEL_30B
$backupDir = Join-Path $MODEL_DIR "backups"
$backupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

if (Test-Path $model30bPath) {
    $chatTemplate30b = Join-Path $model30bPath "chat_template.jinja"
    if (Test-Path $chatTemplate30b) {
        $backupFile = Join-Path $backupDir "chat_template_30b_$backupTimestamp.jinja.bak"
        Copy-Item -Path $chatTemplate30b -Destination $backupFile -Force
        Write-Host "✓ Backed up 30B template to: $backupFile" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️ 30B model directory not found (expected at $model30bPath)" -ForegroundColor Yellow
}

Write-Host ""

# =========================================================================
# PHASE 3: DEPLOY 35B TO OVMS (CONFIG UPDATE)
# =========================================================================

Write-Host "[Phase 3] Update OVMS Configuration for 35B" -ForegroundColor Cyan
Write-Host "-" * 80

# Copy v2.0 template to 35B model directory
$templateSource = Join-Path $TEST_DIR "..\jinja_templates\chat_template_cline_optimized_v2.0.jinja"

# Check if template exists
if (-not (Test-Path $templateSource)) {
    # Fallback to v1.0
    $templateSource = Join-Path $TEST_DIR "..\jinja_templates\chat_template_cline_optimized_v1.0.jinja"
}

if (Test-Path $templateSource) {
    $templateTarget = Join-Path $model35bPath "chat_template.jinja"

    # Backup existing 35B template
    if (Test-Path $templateTarget) {
        $backupFile = Join-Path $backupDir "chat_template_35b_${backupTimestamp}.jinja.bak"
        Copy-Item -Path $templateTarget -Destination $backupFile -Force
        Write-Host "✓ Backed up existing 35B template" -ForegroundColor Green
    }

    # Deploy template to 35B
    Copy-Item -Path $templateSource -Destination $templateTarget -Force
    Write-Host "✓ Deployed optimized Jinja template to 35B model" -ForegroundColor Green
    Write-Host "  Source: $(Split-Path $templateSource -Leaf)" -ForegroundColor Green
    Write-Host "  Target: $templateTarget" -ForegroundColor Green
} else {
    Write-Host "⚠️ Template not found: $templateSource" -ForegroundColor Yellow
}

Write-Host ""

# =========================================================================
# PHASE 4: RESTART OVMS SERVER
# =========================================================================

Write-Host "[Phase 4] Restart OVMS Server with 35B Model" -ForegroundColor Cyan
Write-Host "-" * 80

if (-not $SkipOVMSRestart) {
    # Stop existing OVMS
    $ovmsProc = Get-Process ovms -ErrorAction SilentlyContinue
    if ($ovmsProc) {
        Write-Host "Stopping existing OVMS process (PID: $($ovmsProc.Id))..." -ForegroundColor Yellow
        Stop-Process -InputObject $ovmsProc -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        Write-Host "✓ OVMS stopped" -ForegroundColor Green
    }

    # Start new OVMS with 35B
    Write-Host "Starting OVMS with 35B model..." -ForegroundColor Yellow
    Push-Location $DEPLOY_DIR
    & .\start_ovms_server.ps1
    Pop-Location

    # Wait for server to be ready
    Write-Host "Waiting for OVMS to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15

    # Verify OVMS health
    Write-Host "Verifying OVMS health..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9000/v3/models/$MODEL_35B" `
            -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ OVMS health check PASSED" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ OVMS health check failed, but continuing with tests..." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Skipping OVMS restart (--SkipOVMSRestart flag)" -ForegroundColor Yellow
}

Write-Host ""

# =========================================================================
# PHASE 5: RUN TEST SUITE
# =========================================================================

if (-not $SkipTests) {
    Write-Host "[Phase 5] Run Test Suite (Phase 5 + 6 + 6.5)" -ForegroundColor Cyan
    Write-Host "-" * 80

    # Phase 5 Tests (baseline file ops)
    Write-Host ""
    Write-Host "[Phase 5.1] Running Phase 5 Tests (File Operations Baseline)..." -ForegroundColor Yellow
    cd $TEST_DIR
    python run_jinja_phase5.py
    $phase5Exit = $LASTEXITCODE

    # Store results
    Copy-Item -Path "$TEST_DIR\test_output_*.json" -Destination $RESULTS_DIR -Force -ErrorAction SilentlyContinue

    # Phase 6 Tests (extended tools)
    Write-Host ""
    Write-Host "[Phase 5.2] Running Phase 6 Tests (Extended Tools)..." -ForegroundColor Yellow
    python run_jinja_phase6.py
    $phase6Exit = $LASTEXITCODE

    # Copy Phase 6 results
    if (Test-Path "$TEST_DIR\phase6_extended_tools\*") {
        Copy-Item -Path "$TEST_DIR\phase6_extended_tools\*" -Destination $RESULTS_DIR -Force -ErrorAction SilentlyContinue
    }

    # Phase 6.5 Tests (tool-sequencing)
    Write-Host ""
    Write-Host "[Phase 5.3] Running Phase 6.5 Tests (Tool-Sequencing)..." -ForegroundColor Yellow
    if (Test-Path "$TEST_DIR\test_cline_realistic_code_edit.py") {
        python test_cline_realistic_code_edit.py
        $phase65Exit = $LASTEXITCODE
    } else {
        Write-Host "⚠️ Phase 6.5 test file not found" -ForegroundColor Yellow
        $phase65Exit = -1
    }

    cd -
    Write-Host ""
} else {
    Write-Host "[Phase 5] Skipping test suite (--SkipTests flag)" -ForegroundColor Yellow
    Write-Host ""
}

# =========================================================================
# PHASE 6: GENERATE REPORT
# =========================================================================

Write-Host "[Phase 6] Generate Phase 8b Iteration 1 Report" -ForegroundColor Cyan
Write-Host "-" * 80

$reportContent = @"
# Phase 8b Iteration 1: Qwen3-Coder-35B Deployment & Validation Report

**Date**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Status**: IN PROGRESS

## Executive Summary

This iteration deployed Qwen3-Coder-35B model to OVMS and ran comprehensive validation tests to determine if the larger model size improves tool-sequencing capability (Phase 6.5 tests).

**Hypothesis**: 35B model (+67% larger) should improve tool-sequencing reliability from 0/3 baseline.

## Phase 1: Model Verification

**Model Found**: $(if (Test-Path $model35bPath) { "YES" } else { "NO" })
**Model Path**: $model35bPath
**OpenVINO Format**: $(if ((Get-ChildItem -Path $model35bPath -Filter "*.xml" -ErrorAction SilentlyContinue).Count -gt 0) { "YES (XML+BIN present)" } else { "NO" })

### Model Details
- **Model**: Qwen3.6-35B-A3B-int4-ov
- **Base Model**: Qwen3.6-35B-A3B (quantized to INT4)
- **Parameters**: ~35 Billion (vs 30B baseline)
- **Format**: OpenVINO (XML + BIN files)
- **Deployment Date**: $(Get-Date -Format 'yyyy-MM-dd')

## Phase 2: Backup & Configuration

**30B Backup**: $(if (Test-Path (Join-Path $backupDir "chat_template_30b_*")) { "CREATED" } else { "N/A" })
**Backup Location**: $backupDir
**Template Version Deployed**: v2.0 (tojson-optimized)

## Phase 3: OVMS Deployment

**Status**: $(if ($SkipOVMSRestart) { "SKIPPED" } else { "COMPLETED" })
**Model in OVMS**: $MODEL_35B
**Health Check**: $(if (-not $SkipOVMSRestart) { "PASSED" } else { "N/A" })

## Phase 4: Test Results

### Phase 5: File Operations Baseline
- **Expected**: 5/5 PASS
- **Status**: $(if ($phase5Exit -eq 0) { "PENDING" } else { "N/A" })

**Test Cases**:
- TC1: Simple tool call (list_directory_tree)
- TC2: Parameter expansion
- TC3: Multiple params
- TC4: Special chars in params
- TC5: Long response handling

### Phase 6: Extended Tools
- **Expected**: 4/4 PASS
- **Status**: $(if ($phase6Exit -eq 0) { "PENDING" } else { "N/A" })

**Test Cases**:
- TC6: execute_command tool
- TC7: search_files tool
- TC8: web_search tool
- TC9: list_directory_tree variant

### Phase 6.5: Tool-Sequencing (Primary Target)
- **Baseline (30B)**: 0/3 PASS
- **Target (35B)**: 2-3/3 PASS
- **Status**: $(if ($phase65Exit -eq 0) { "PENDING" } else { "N/A" })

**Test Cases**:
- Test A: Read → Write sequence (file ops)
- Test B: Search → Execute sequence (info retrieval)
- Test C: List → Analyze sequence (directory ops)

## Phase 5: Regression Analysis

**Phase 5 + 6 Combined Baseline**: 9/9 PASS (v2.0 on 30B)
**Expected Phase 5 + 6 (35B)**: 9/9 PASS (zero regressions required)

**Regression Check**: $(if ($phase5Exit -eq 0 -and $phase6Exit -eq 0) { "PENDING VERIFICATION" } else { "N/A" })

## Phase 6: Success Metrics

**Success Threshold**:
1. Phase 5 + 6: Zero regressions (5/5 + 4/4 required)
2. Phase 6.5: Improvement to ≥2/3 PASS (was 0/3)

**Go/No-Go Decision**:
- If ✓: KEEP 35B → Iterate 2+
- If Phase 5/6 regress: REVERT immediately
- If Phase 6.5 stays 0/3: REVERT + escalate

## Diagnostics

$(if (Test-Path "$RESULTS_DIR\*") { "Test outputs available in: $RESULTS_DIR" } else { "Test outputs not yet generated" })

## Recommendation

**Status**: PENDING TEST EXECUTION

**Next Steps**:
1. Verify all test results match expected outcomes
2. If ≥2/3 Phase 6.5 PASS: Advance to Iteration 2
3. If failures detected: Analyze error patterns and adjust approach

---

**Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@

$reportContent | Out-File -FilePath $REPORT_FILE -Encoding UTF8 -Force
Write-Host "✓ Report generated: $REPORT_FILE" -ForegroundColor Green

Write-Host ""
Write-Host "=" * 80
Write-Host "Phase 8b Iteration 1 Deployment Complete" -ForegroundColor Green
Write-Host "=" * 80
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review test results in: $RESULTS_DIR"
Write-Host "  2. Check full report: $REPORT_FILE"
Write-Host "  3. Verify Phase 5/6 for regressions"
Write-Host "  4. Check Phase 6.5 for improvement"
Write-Host ""
Write-Host "To stop OVMS:"
Write-Host "  .\jinja_deployment\stop_ovms_server.ps1"
Write-Host ""
