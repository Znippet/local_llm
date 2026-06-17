# Qwen3-Coder Jinja-Template Optimization for Cline

**Goal**: Optimized `chat_template.jinja` for Qwen3-Coder-30B-A3B, integrated with Cline via OpenVINO Model Server (OVMS).

**Status**: Phase 5 ✅ COMPLETE | Phase 6 ⏳ IN PROGRESS

---

## Project Overview

This project systematically optimizes Jinja chat templates for Qwen3-Coder-30B-A3B-Instruct, focusing on **Cline** compatibility. Research spans 7 template sources, structural analysis, synthesis, and rigorous testing.

**Phases**:
- ✅ **Phase 1**: Template Collection (7 sources, analysis)
- ✅ **Phase 2**: Structural Comparison (side-by-side diff)
- ✅ **Phase 3**: Cline-Optimized Template (v1.0)
- ✅ **Phase 4**: Test Strategy (5 test cases)
- ✅ **Phase 5**: Test Execution (5/5 PASS, v1.0 validated)
- ⏳ **Phase 6**: Extended Tools & Cleanup (4 new tools, TC6-TC9)
- ⏹️ **Phase 7**: Documentation & Justification

---

## Quick Start

### 1. Validate OVMS Setup

```powershell
.\jinja_deployment\validate_ovms_setup.ps1
```

### 2. Deploy Latest Template

```powershell
# Deploy v1.0 (File Operations — CURRENT PRODUCTION)
.\jinja_deployment\deploy_jinja_template.ps1 -Version v1.0

# Or deploy v2.0 (Extended Tools — AFTER Phase 6 validation)
.\jinja_deployment\deploy_jinja_template.ps1 -Version v2.0 -RestartOVMS $true
```

### 3. Run Tests

```bash
# Phase 5: File Operations (always PASS, baseline)
python jinja_tests/run_jinja_phase5.py
# Expected: 5/5 PASS

# Phase 6: Extended Cline Tools (v2.0 validation)
python jinja_tests/run_jinja_phase6.py
# Expected: 4/4 PASS (pending v2.0 refinement)
```

---

## Jinja-Template Versions

### v1.0 — File Operations (PRODUCTION)

**File**: `jinja_templates/chat_template_cline_optimized_v1.jinja`

**Tools Supported**:
- `read_file` — Read file contents
- `list_files` — Directory listing
- `write_file` — Write/create files

**Status**: ✅ **Validated** (Phase 5: 5/5 PASS)

**Use Case**: Cline file-based workflows (read/modify/write code)

**Test Cases**:
- TC1: Single tool call
- TC2: Structured arguments
- TC3: Tool result follow-up
- TC4: No-tool answer path
- TC5: Multi-step sequencing

### v2.0 — Extended Cline Tools (TESTING)

**File**: `jinja_templates/chat_template_cline_optimized_v2.jinja`

**New Tools** (planned):
- `execute_command` — Shell command execution
- `search_files` — Pattern matching in directories
- `web_search` — Information retrieval
- `list_directory_tree` — Directory tree traversal

**Status**: ⏳ **Testing** (Phase 6: TC6-TC9 pending)

**Use Case**: Rich Cline capabilities (exec, search, web)

**Test Cases**:
- TC6: execute_command
- TC7: search_files
- TC8: web_search
- TC9: list_directory_tree

---

## Testing & Validation

### Test Suite Structure

```
jinja_tests/
├── run_jinja_phase5.py          # Phase 5: TC1-TC5 (File Ops)
├── run_jinja_phase6.py          # Phase 6: TC6-TC9 (Extended Tools)
├── test_jinja_cline_flow.py     # Realistic multi-turn scenario
├── tools_schema.json            # Central tool definitions
└── README-JINJA-TESTS.md        # Test documentation
```

### Test Results

```
test_results/
├── phase5_file_ops/
│   ├── test_output_tc1.json
│   ├── test_output_tc2.json
│   ├── test_output_tc3.json
│   ├── test_output_tc4.json
│   ├── test_output_tc5.json
│   └── Phase5-Test-Results.json    (5/5 PASS ✅)
├── phase6_extended_tools/
│   ├── test_output_tc6.json
│   ├── test_output_tc7.json
│   ├── test_output_tc8.json
│   ├── test_output_tc9.json
│   └── Phase6-Test-Results.json    (⏳ pending)
└── cline_flow/
    └── test_cline_flow_result.json
```

### Run Tests

#### Phase 5: File Operations (Baseline)

```bash
python jinja_tests/run_jinja_phase5.py
```

Expected output:
```
[PASS] TC1: PASS (0 errors)
[PASS] TC2: PASS (0 errors)
[PASS] TC3: PASS (0 errors)
[PASS] TC4: PASS (0 errors)
[PASS] TC5: PASS (0 errors)

Total: 5/5 PASS
```

#### Phase 6: Extended Cline Tools

```bash
python jinja_tests/run_jinja_phase6.py
```

Expected output (pending Phase 6 completion):
```
[PASS] TC6: PASS (0 errors)
[PASS] TC7: PASS (0 errors)
[PASS] TC8: PASS (0 errors)
[PASS] TC9: PASS (0 errors)

Total: 4/4 PASS
```

---

## Template Deployment

### Deploy Template to OVMS

See detailed guide: `jinja_deployment/README-DEPLOYMENT.md`

**Quick Deploy**:

```powershell
# Validate setup first
.\jinja_deployment\validate_ovms_setup.ps1

# Deploy v1.0
.\jinja_deployment\deploy_jinja_template.ps1 -Version v1.0

# After OVMS restart, run tests
python jinja_tests/run_jinja_phase5.py
```

**Deploy with Restart**:

```powershell
.\jinja_deployment\deploy_jinja_template.ps1 -Version v2.0 -RestartOVMS $true
```

### Manual Rollback

```powershell
# List backups
Get-Item "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja.backup_*" | Sort-Object LastWriteTime -Descending

# Restore specific backup
Copy-Item "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja.backup_YYYYMMDD_HHMMSS" `
          "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja" -Force
```

---

## Directory Structure

```
C:\LLM/
├── jinja_templates/                    (Template archive)
│   ├── chat_template_original.jinja          (HuggingFace Original, baseline)
│   ├── chat_template_cline_optimized_v1.jinja    (Phase 3, validated)
│   ├── chat_template_cline_optimized_v2.jinja    (Phase 6, testing)
│   ├── JINJA-VERSIONS.md                (Version history & changelog)
│   └── README-JINJA.md                  (Template usage guide)
│
├── jinja_tests/                        (Test suite)
│   ├── run_jinja_phase5.py              (TC1-TC5: File Ops)
│   ├── run_jinja_phase6.py              (TC6-TC9: Extended Tools)
│   ├── test_jinja_cline_flow.py         (Realistic scenario)
│   ├── tools_schema.json                (Central tool definitions)
│   └── README-JINJA-TESTS.md            (Test documentation)
│
├── jinja_deployment/                   (Deployment scripts)
│   ├── deploy_jinja_template.ps1        (Template deployment)
│   ├── validate_ovms_setup.ps1          (Health check)
│   └── README-DEPLOYMENT.md             (Deployment guide)
│
├── test_results/                       (Test execution results)
│   ├── phase5_file_ops/                 (Phase 5 outputs)
│   │   ├── test_output_tc*.json
│   │   └── Phase5-Test-Results.json
│   ├── phase6_extended_tools/           (Phase 6 outputs)
│   │   └── Phase6-Test-Results.json
│   └── cline_flow/                      (Flow test results)
│
├── models/OpenVINO/                    (Model binaries)
│   └── Qwen3-Coder-30B-A3B-Instruct-int4-ov/
│       ├── chat_template.jinja          (Currently deployed)
│       ├── chat_template.jinja.backup_* (Versioned backups)
│       ├── model.xml
│       └── model.bin
│
├── Phase1-Template-Collection.md       (Research: 7 sources)
├── Phase2-Structural-Comparison.md     (Research: side-by-side diff)
├── Phase3-Cline-Optimized-Template.md  (Template design)
├── Phase4-Test-Strategy.md             (Test plan)
├── Phase5-Test-Results.md              (Phase 5 summary)
├── Phase6-Refinement-Plan.md           (Phase 6 plan)
├── QWEN3-CODER-CLINE-PLAN.md          (Master plan)
└── README.md                            (This file)
```

---

## Tool Definitions

All tools centrally defined in: `jinja_tests/tools_schema.json`

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "read_file",
        "description": "Read file content",
        "parameters": { ... }
      }
    },
    { ... other tools ... }
  ]
}
```

Add new tools to this file — tests will automatically load them.

---

## OVMS Setup

### Start OVMS Server

```powershell
cd C:\LLM
.\start_ovms_qwen.bat
```

Ensure startup message shows:
```
[INFO] Listening on http://localhost:9000
```

### Model Configuration

**Command**:
```
ovms --log_level WARNING --model_repository_path c:\LLM\models \
  --source_model OpenVINO/Qwen3-Coder-30B-A3B-Instruct-int4-ov \
  --task text_generation \
  --target_device AUTO \
  --tool_parser qwen3coder \
  --enable_tool_guided_generation false \
  --rest_port 9000 \
  --cache_dir .ovcache \
  --model_name qwen3-coder-30b-a3b-instruct-int4-ov
```

**Key Settings**:
- `--tool_parser qwen3coder` — Qwen3-specific tool parsing
- `--enable_tool_guided_generation false` — Template-based tool calls (not server-guided)
- `--rest_port 9000` — API port for tests & Cline

---

## Integration with Cline

### Configure Cline to Use Local OVMS

In Cline settings / config:

```json
{
  "model": "qwen3-coder-30b-a3b-instruct-int4-ov",
  "apiBase": "http://localhost:9000/v3",
  "temperature": 0.6,
  "maxTokens": 8192
}
```

### Expected Tool Calls

Cline will use:
- `read_file` / `write_file` — Code editing
- `search_files` — Code search (Phase 6)
- `execute_command` — Run tests/compile (Phase 6)
- `list_directory_tree` — Project navigation (Phase 6)

---

## Test Philosophy

### Strict Validation

- ✓ Valid JSON arguments (no hallucinations)
- ✓ Tool names in allowlist
- ✓ Required parameters present
- ✓ Multi-step sequencing correct
- ✓ Q4 quantization robust (no corruption)

### No Hallucinations

- ✗ Fake tools
- ✗ Missing parameters
- ✗ Invalid JSON args
- ✗ Out-of-order tool calls
- ✗ Text-as-tool-call confusion

---

## Troubleshooting

### OVMS Not Responding

```powershell
# Check process
Get-Process ovms

# Check port
Get-NetTCPConnection -LocalPort 9000

# Restart
Stop-Process -Name ovms -Force
Start-Sleep -Seconds 2
.\start_ovms_qwen.bat
```

### Template Deployment Failed

```powershell
# OVMS may have file locked
Stop-Process -Name ovms -Force
Start-Sleep -Seconds 2
.\jinja_deployment\deploy_jinja_template.ps1 -Version v1.0
```

### Tests FAIL

1. Check `test_results/phase*/test_output_tc*.json` for raw response
2. Verify OVMS restarted after deployment
3. Check template file timestamp (should be recent)
4. Run health check: `.\jinja_deployment\validate_ovms_setup.ps1`

---

## Resources

- **Master Plan**: `QWEN3-CODER-CLINE-PLAN.md`
- **Template Versions**: `jinja_templates/JINJA-VERSIONS.md`
- **Test Suite**: `jinja_tests/README-JINJA-TESTS.md`
- **Deployment**: `jinja_deployment/README-DEPLOYMENT.md`
- **Phase Outputs**: `Phase*-*.md`

---

## Next Steps

1. **Phase 6**: Validate TC6-TC9 (extended tools)
   ```bash
   python jinja_tests/run_jinja_phase6.py
   ```

2. **If PASS**: Use v2.0 as production default

3. **If FAIL**: Document refinements, iterate template

4. **Phase 7**: Final documentation & justification writeup

---

## Repository Metadata

**Repository**: C:\LLM  
**Git Branch**: master  
**Status**: Active Development  
**Last Updated**: 2026-06-17  
**Project Lead**: Stefan Dohren  
**Contact**: stefan.dohren@live.de
