<#
.SYNOPSIS
Stop OVMS Server via PID-Tracking

.DESCRIPTION
Liest PID aus Datei, beendet OVMS Prozess sauber.
Wartet auf Shutdown, validiert Beendigung.

.EXAMPLE
.\stop_ovms_server.ps1
#>

$ErrorActionPreference = "Continue"

$PidFile = "C:\LLM\.ovms_pid"

Write-Host "=" * 70
Write-Host "OVMS Server Shutdown"
Write-Host "=" * 70
Write-Host ""

# Read PID from file
if (-not (Test-Path $PidFile)) {
    Write-Host "❌ PID file not found: $PidFile" -ForegroundColor Red
    Write-Host "   OVMS may not have been started with start_ovms_server.ps1" -ForegroundColor Yellow

    # Try to find OVMS process by name
    $ovms = Get-Process ovms -ErrorAction SilentlyContinue
    if ($ovms) {
        Write-Host ""
        Write-Host "Found OVMS process (PID: $($ovms.Id))"
        Write-Host "Attempting to stop..."
        $PID = $ovms.Id
    } else {
        Write-Host ""
        Write-Host "No OVMS process running"
        exit 0
    }
} else {
    $PID = (Get-Content $PidFile -Encoding UTF8).Trim()
    if (-not $PID) {
        Write-Host "❌ PID file is empty: $PidFile" -ForegroundColor Red
        exit 1
    }
    Write-Host "PID from file: $PID"
}

# Check if process exists
$process = Get-Process -Id $PID -ErrorAction SilentlyContinue
if (-not $process) {
    Write-Host "⚠️  Process not found (PID: $PID)" -ForegroundColor Yellow
    Write-Host "   Already stopped? Cleaning up PID file..."
    if (Test-Path $PidFile) {
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
    exit 0
}

Write-Host "Stopping OVMS (PID: $PID)..."
Write-Host ""

# Stop process gracefully first
$process.CloseMainWindow() | Out-Null
Start-Sleep -Seconds 2

# Check if still running
$process = Get-Process -Id $PID -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "Process still running, forcing termination..."
    Stop-Process -Id $PID -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Validate stopped
$process = Get-Process -Id $PID -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "❌ Process still running (PID: $PID)" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✓ OVMS stopped successfully" -ForegroundColor Green
}

# Cleanup PID file
if (Test-Path $PidFile) {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "✓ PID file cleaned up" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 70
Write-Host "OVMS Shutdown Complete" -ForegroundColor Green
Write-Host "=" * 70

# Verify port 9000 is free
Start-Sleep -Seconds 1
try {
    $connection = Get-NetTCPConnection -LocalPort 9000 -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "⚠️  Port 9000 still in use" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Port 9000 is free" -ForegroundColor Green
    }
} catch {
    Write-Host "✓ Port 9000 is free" -ForegroundColor Green
}
