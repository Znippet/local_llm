param(
    [ValidateSet("v1.0", "v2.0")]
    [string]$Version = "v1.0",
    [string]$OVMSModelDir = "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov",
    [switch]$RestartOVMS = $false
)

<#
.SYNOPSIS
Deploy Jinja-Template zu OVMS Modell-Verzeichnis

.DESCRIPTION
Kopiert selektierte Jinja-Template-Version zu OVMS, mit Backup der aktuellen Template.

.PARAMETER Version
Template-Version zu deployen: v1.0 (File Ops) oder v2.0 (Extended Tools)

.PARAMETER OVMSModelDir
OVMS Model-Verzeichnis für Qwen3-Coder

.PARAMETER RestartOVMS
Optional: OVMS-Prozess nach Deploy stoppen

.EXAMPLE
.\deploy_jinja_template.ps1 -Version v1.0
Deploy v1.0, kein Restart

.EXAMPLE
.\deploy_jinja_template.ps1 -Version v2.0 -RestartOVMS $true
Deploy v2.0 und Restart OVMS
#>

$ErrorActionPreference = "Stop"

$TemplateSource = "C:\LLM\jinja_templates\chat_template_cline_optimized_$($Version).jinja"
$TemplateTarget = "$OVMSModelDir\chat_template.jinja"

# Validierungen
if (-not (Test-Path $TemplateSource)) {
    Write-Host "❌ Jinja-Template not found: $TemplateSource" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $OVMSModelDir)) {
    Write-Host "❌ OVMS Model-Dir not found: $OVMSModelDir" -ForegroundColor Red
    exit 1
}

Write-Host "=" * 70
Write-Host "Jinja-Template Deployment"
Write-Host "=" * 70
Write-Host ""
Write-Host "Version: $Version"
Write-Host "Source: $TemplateSource"
Write-Host "Target: $TemplateTarget"
Write-Host ""

# Backup existing template
if (Test-Path $TemplateTarget) {
    $BackupFile = "$OVMSModelDir\chat_template.jinja.backup_$(Get-Date -Format yyyyMMdd_HHmmss)"
    Copy-Item $TemplateTarget $BackupFile -Force
    Write-Host "✓ Backup created: $(Split-Path $BackupFile -Leaf)" -ForegroundColor Green
}

# Deploy
try {
    Copy-Item $TemplateSource $TemplateTarget -Force
    Write-Host "✓ Deployed Jinja $Version to OVMS" -ForegroundColor Green
}
catch {
    Write-Host "❌ Deployment failed: $($_)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Optional OVMS restart
if ($RestartOVMS) {
    Write-Host "Attempting to restart OVMS..."
    $ovms = Get-Process ovms -ErrorAction SilentlyContinue
    if ($ovms) {
        Stop-Process -InputObject $ovms -Force -ErrorAction SilentlyContinue
        Write-Host "✓ OVMS stopped" -ForegroundColor Green
        Start-Sleep -Seconds 2
    }
    Write-Host "⚠️  Please restart OVMS manually:" -ForegroundColor Yellow
    Write-Host "   cd C:\LLM && .\start_ovms_qwen.bat"
} else {
    Write-Host "⚠️  OVMS restart required for template changes to take effect" -ForegroundColor Yellow
    Write-Host "   Manual: Kill OVMS and run: .\start_ovms_qwen.bat" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 70
Write-Host "Deployment Complete" -ForegroundColor Green
Write-Host "=" * 70
