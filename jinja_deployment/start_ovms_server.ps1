<#
.SYNOPSIS
Start OVMS Server mit PID-Tracking

.DESCRIPTION
Startet OVMS Model Server, schreibt PID zu Datei für späteren Stop.
Prüft ob bereits laufen (Port 9000).

.EXAMPLE
.\start_ovms_server.ps1
#>

$ErrorActionPreference = "Stop"

$PidFile = "C:\LLM\.ovms_pid"
$OvmsExe = "C:\LLM\ovms\ovms.exe"
$ModelDir = "C:\LLM\models"
$CacheDir = "C:\LLM\.ovcache"

Write-Host "=" * 70
Write-Host "OVMS Server Startup"
Write-Host "=" * 70
Write-Host ""

# Check ob bereits läuft (Port 9000)
try {
    $existing = Get-NetTCPConnection -LocalPort 9000 -ErrorAction SilentlyContinue
    if ($existing) {
        $proc = Get-Process -Id $existing.OwningProcess -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "⚠️  OVMS already running (PID: $($proc.Id))" -ForegroundColor Yellow
            Write-Host "   Port 9000 in use"

            # Update PID file anyway
            $proc.Id | Out-File $PidFile -Encoding UTF8 -NoNewline
            Write-Host "   PID file updated: $PidFile"
            exit 0
        }
    }
} catch {
    # Port check failed, continue
}

# Cleanup old PID file
if (Test-Path $PidFile) {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

# Validate OVMS exe
if (-not (Test-Path $OvmsExe)) {
    Write-Host "❌ OVMS executable not found: $OvmsExe" -ForegroundColor Red
    exit 1
}

Write-Host "Starting OVMS..."
Write-Host "  Executable: $OvmsExe"
Write-Host "  Model Dir: $ModelDir"
Write-Host "  Cache Dir: $CacheDir"
Write-Host ""

# Build command line with proper formatting (like .bat file)
# NOTE: Use 30B by default (35B is incompatible multi-modal model)
# To use 35B, set $env:OVMS_MODEL environment variable
$ModelName = if ($env:OVMS_MODEL) {
    $env:OVMS_MODEL
} else {
    "Qwen3-Coder-30B-A3B-Instruct-int4-ov"  # Default to 30B (text-only, compatible)
}

$args = @(
    "--log_level WARNING",
    "--model_repository_path c:\LLM\models",
    "--source_model OpenVINO/$ModelName",
    "--task text_generation",
    "--target_device AUTO",
    "--tool_parser qwen3coder",
    "--enable_tool_guided_generation false",
    "--rest_port 9000",
    "--cache_dir .ovcache",
    "--model_name $ModelName"
)

# Start OVMS with arguments
$process = Start-Process `
    -FilePath $OvmsExe `
    -ArgumentList $args `
    -PassThru `
    -NoNewWindow

# Write PID to file
$process.Id | Out-File $PidFile -Encoding UTF8 -NoNewline

Write-Host "✓ OVMS started (PID: $($process.Id))" -ForegroundColor Green
Write-Host "  PID saved to: $PidFile"
Write-Host ""
Write-Host "Waiting for server startup (15 seconds)..."
Start-Sleep -Seconds 15

# Validate startup
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9000/v3/models/$ModelName" `
        -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ OVMS API responding" -ForegroundColor Green
        Write-Host "  Model: $ModelName" -ForegroundColor Green
        Write-Host ""
        Write-Host "=" * 70
        Write-Host "Ready for testing" -ForegroundColor Green
        Write-Host "=" * 70
        Write-Host ""
        Write-Host "Run tests:"
        Write-Host "  python C:\LLM\jinja_tests\run_jinja_phase5.py"
        Write-Host "  python C:\LLM\jinja_tests\run_jinja_phase6.py"
        Write-Host ""
        Write-Host "To stop server:"
        Write-Host "  .\jinja_deployment\stop_ovms_server.ps1"
    }
} catch {
    Write-Host "⚠️  API not responding yet (may still be loading)" -ForegroundColor Yellow
    Write-Host "   Wait 30 seconds and retry"
}
