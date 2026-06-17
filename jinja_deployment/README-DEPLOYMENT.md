# Jinja-Template Deployment Guide

Anleitung zum Deployen von Qwen3-Coder Jinja-Template-Versionen zu OVMS.

---

## Quick Start

### 1. Validate OVMS Setup

```powershell
.\jinja_deployment\validate_ovms_setup.ps1
```

Prüft:
- OVMS-Prozess läuft
- Jinja-Template existiert
- API-Endpoint erreichbar
- Model geladen

### 2. Deploy Template

Deploy v1.0 (File Operations):
```powershell
.\jinja_deployment\deploy_jinja_template.ps1 -Version v1.0 -RestartOVMS $false
```

Deploy v2.0 (Extended Tools):
```powershell
.\jinja_deployment\deploy_jinja_template.ps1 -Version v2.0 -RestartOVMS $true
```

### 3. Run Tests

Nach Deploy OVMS restart (wenn nicht auto):
```bash
python jinja_tests/run_jinja_phase5.py
python jinja_tests/run_jinja_phase6.py
```

---

## Templates

### v1.0 — File Operations (CURRENT PRODUCTION)

File: `jinja_templates/chat_template_cline_optimized_v1.jinja`

**Tools**:
- read_file
- list_files
- write_file

**Status**: ✅ Validated (Phase 5, 5/5 PASS)

**Use Case**: Cline file-based workflows

### v2.0 — Extended Cline Tools (IN TESTING)

File: `jinja_templates/chat_template_cline_optimized_v2.0.jinja`

**Tools**:
- execute_command
- search_files
- web_search
- list_directory_tree

**Status**: ⏳ Testing (Phase 6, pending)

**Use Case**: Rich Cline capabilities

---

## Deployment Process

### Step 1: Pre-Deployment Validation

```powershell
.\jinja_deployment\validate_ovms_setup.ps1
```

Ensure:
- ✓ OVMS running
- ✓ Template file exists
- ✓ API endpoint responding
- ✓ Model loaded

**If failed**: Start OVMS first
```powershell
cd C:\LLM
.\start_ovms_qwen.bat
# Wait 15-30 seconds for startup
```

### Step 2: Deploy

```powershell
.\jinja_deployment\deploy_jinja_template.ps1 -Version <v1.0|v2.0> [-RestartOVMS $true]
```

**What it does**:
1. Validates source template exists
2. Creates backup of current template (timestamp)
3. Copies new template to OVMS model dir
4. Optionally restarts OVMS

### Step 3: Verify Deployment

```powershell
# Check file was copied
Get-Item "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja" | Select-Object LastWriteTime

# Check recent backups
Get-Item "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja.backup_*" | Sort-Object LastWriteTime -Descending | Select-Object Name -First 3
```

### Step 4: Test

After OVMS restart, run tests:

```bash
# File Operations baseline (should always PASS)
python jinja_tests/run_jinja_phase5.py

# Extended tools (v2.0 validation)
python jinja_tests/run_jinja_phase6.py
```

---

## Troubleshooting

### OVMS not running

```powershell
# Start OVMS
cd C:\LLM
.\start_ovms_qwen.bat

# Wait for startup messages:
# [INFO] Listening on http://localhost:9000
# Then Ctrl+C to background or let it run
```

### API Endpoint Error

Symptom: "API endpoint not responding"

```powershell
# Check OVMS process
Get-Process ovms

# If not running, start it:
.\start_ovms_qwen.bat

# If port 9000 is in use by something else:
Get-NetTCPConnection -LocalPort 9000 | Select-Object OwningProcess
```

### Template Deployment Failed

Symptom: "Deployment failed: Access denied" or similar

**Cause**: OVMS may have file locked

```powershell
# Stop OVMS
Stop-Process -Name ovms -Force

# Wait 2 seconds
Start-Sleep -Seconds 2

# Re-deploy
.\jinja_deployment\deploy_jinja_template.ps1 -Version v1.0
```

### Tests FAIL after Deployment

Symptom: TC1-TC5 or TC6-TC9 FAIL

**Check**:
1. Template was actually deployed
   ```powershell
   Get-Item "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja" | Select-Object LastWriteTime
   ```

2. OVMS was restarted after deployment
   ```powershell
   Get-Process ovms | Select-Object StartTime
   # Should be recent
   ```

3. Restart OVMS manually
   ```powershell
   Stop-Process -Name ovms -Force
   Start-Sleep -Seconds 2
   # Run .\start_ovms_qwen.bat
   ```

4. Re-run test
   ```bash
   python jinja_tests/run_jinja_phase5.py
   ```

---

## Rollback to Previous Version

All deployments create timestamped backups:

```powershell
# List recent backups
Get-Item "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja.backup_*" | Sort-Object LastWriteTime -Descending

# Restore specific backup
$BackupFile = "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja.backup_20260617_120000"
Copy-Item $BackupFile "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja" -Force

# Restart OVMS to pick up change
Stop-Process -Name ovms -Force
Start-Sleep -Seconds 2
# Run .\start_ovms_qwen.bat
```

---

## Template Comparison

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| **Format** | Qwen3 ChatML | Qwen3 ChatML |
| **File Ops** | ✅ | ✅ |
| **Command Exec** | ❌ | ⏳ |
| **Search** | ❌ | ⏳ |
| **Web Search** | ❌ | ⏳ |
| **Dir Tree** | ❌ | ⏳ |
| **Status** | ✅ Production | ⏳ Testing |
| **Phase** | Phase 5 ✅ | Phase 6 ⏳ |
| **Test Results** | 5/5 PASS | Pending |

---

## OVMS Model Directory Structure

```
C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\
├── chat_template.jinja                          (Current template)
├── chat_template.jinja.backup_20260617_120000   (Backup from 2026-06-17 12:00)
├── chat_template.jinja.backup_20260617_110000   (Backup from 2026-06-17 11:00)
├── model.xml
├── model.bin
└── ... (other model files)
```

---

## Testing After Deployment

### Full Test Suite

```powershell
# Validate setup first
.\jinja_deployment\validate_ovms_setup.ps1

# Run Phase 5 (File Operations baseline)
python jinja_tests/run_jinja_phase5.py
# Expected: 5/5 PASS

# Run Phase 6 (Extended Tools)
python jinja_tests/run_jinja_phase6.py
# Expected: 4/4 PASS (or inform if v2.0 refinement needed)

# Check results
cat test_results/phase5_file_ops/Phase5-Test-Results.json
cat test_results/phase6_extended_tools/Phase6-Test-Results.json
```

### Quick Test

```bash
# Just quick health check without full test suite
curl -s http://localhost:9000/v3/models/qwen3-coder-30b-a3b-instruct-int4-ov | python -m json.tool
```

---

## Environment Setup

### Prerequisites

- PowerShell 5.0+ (comes with Windows 10+)
- OVMS running with Qwen3-Coder model
- Python 3.7+ (for tests)

### First Time Setup

```powershell
# Ensure OVMS working
cd C:\LLM
.\start_ovms_qwen.bat
# Wait 15-30 seconds for startup

# In another terminal:
.\jinja_deployment\validate_ovms_setup.ps1

# Should see: ✓ All checks passed
```

---

## Next Steps

- **Phase 6 Testing**: Run `run_jinja_phase6.py` after v2.0 deployment
- **If PASS**: Use v2.0 as production default
- **If FAIL**: Document refinements, iterate
- **Phase 7**: Final documentation writeup

---

## Contact / Support

For issues or questions:
- Check test results: `test_results/phase*/` JSON files
- Review template: `jinja_templates/JINJA-VERSIONS.md`
- Check main plan: `QWEN3-CODER-CLINE-PLAN.md`
