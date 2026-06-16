# Phase 6: Jinja-Template Refinement & Extended Tool Validation
**Status**: PENDING  
**Predecessor**: Phase 5 (Jinja-Template Validation with File Ops) ✅ COMPLETE  
**Successor**: Phase 7 (Justification & Documentation)

**Context**: LLM-Projekt zur Qwen3-Coder Jinja-Template Optimierung für Cline. Phase 5 validierte Template mit 3 File-Operation Tools. Phase 6 erweitert Testing auf echte Cline-Tools (command exec, file search, web search, directory tree).

---

## Ziel
Jinja-Template-Suite aufräumen, erweitern, wasserfest machen:
1. Tests um echte Cline-Tools erweitern (execute_command, search_files, web_search, list_directory_tree)
2. Jinja-Template-Versionierung organisieren (Vergleichbarkeit von Template-Varianten)
3. Test-Infrastruktur für Template-Validierung aufbauen (wiederverwendbar für OpenCode, andere Projekte)
4. Dokumentation aktualisieren (Jinja-Focus, nicht generisch)

---

## Phase 6 Checklist

### 6.1 Jinja-Template Verzeichnis-Struktur aufräumen

**Ziel**: Jinja-Template-Varianten zentral organisieren, Test-Infrastruktur klar separieren

```
C:\LLM\
├── Phase*-*.md                              (Keep — Phase-Dokumentation)
├── QWEN3-CODER-CLINE-PLAN.md               (Keep — Master Plan)
├── README.md                                 (Update — siehe 6.4)
│
├── jinja_templates/                         (NEW — Qwen3-Coder Jinja-Template Archiv)
│   ├── chat_template_original.jinja                    (HF Original, Baseline)
│   ├── chat_template_cline_optimized_v1.jinja         (Phase 3 — File Ops validiert)
│   ├── chat_template_cline_optimized_v2.jinja         (Phase 6 — Extended Tools, if needed)
│   ├── JINJA-VERSIONS.md                   (Template-Versionshistorie & Änderungen)
│   └── README-JINJA.md                     (Wie Jinja-Templates testen, deployen, ändern)
│
├── jinja_tests/                             (NEW — Test-Suite für Jinja-Template-Validierung)
│   ├── run_jinja_phase5.py                 (Phase 5: File Ops — read, list, write)
│   ├── run_jinja_phase6.py                 (Phase 6: Cline Tools — exec, search, web, tree)
│   ├── test_jinja_cline_flow.py            (Realistic multi-turn Cline scenario)
│   ├── README-JINJA-TESTS.md               (Test-Philosophie, wie man Tests schreibt)
│   └── tools_schema.json                   (Tool-Definitionen — zentral, nicht hardcoded)
│
├── jinja_deployment/                       (NEW — Deployment & Setup Scripts)
│   ├── deploy_jinja_template.ps1           (Template zu OVMS Model-Dir kopieren)
│   ├── validate_ovms_setup.ps1             (OVMS Health-Check vor Tests)
│   └── README-DEPLOYMENT.md
│
├── test_results/                            (Existing, reorganize)
│   ├── phase5_file_ops/                    (NEW — Phase 5 Results separieren)
│   │   ├── test_output_tc*.json
│   │   └── Phase5-Test-Results-FINAL.md
│   ├── phase6_extended_tools/              (NEW — Phase 6 Results separieren)
│   │   ├── test_output_tc*.json
│   │   └── Phase6-Test-Results.json
│   └── cline_flow/                         (NEW — Flow-Tests separieren)
│       └── test_cline_flow_result.json
│
└── models/OpenVINO/...                     (Existing — no change)
```

**Aktionen**:
- [ ] Erstelle `jinja_templates/` Verzeichnis
- [ ] Kopiere/Rename `.jinja` Dateien: `*_v1`, `*_v2` (Versionierung!)
- [ ] Erstelle `jinja_tests/` Verzeichnis
- [ ] Verschiebe `run_phase5_tests.py` → `jinja_tests/run_jinja_phase5.py`
- [ ] Verschiebe `test_cline_flow.py` → `jinja_tests/test_jinja_cline_flow.py`
- [ ] Erstelle `jinja_tests/tools_schema.json` (Tool-Defs zentral)
- [ ] Erstelle `jinja_deployment/` & verschiebe PS-Scripts
- [ ] Reorganize `test_results/` in Subfolders (phase5, phase6, cline_flow)
- [ ] Erstelle `jinja_templates/JINJA-VERSIONS.md` (Template-Changelog)
- [ ] Alte `.py` und `.ps1` aus C:\LLM\ root löschen (nach Verschieben)
- [ ] `git add -A` & commit mit Nachricht "Phase 6: Organize Jinja-Template Workspace"

---

### 6.2 Jinja-Template mit Cline-Tools erweitern & validieren

**Kontext**: Phase 5 validierte Jinja-Template mit 3 File-Operation Tools. Phase 6 erweitert Jinja-Template auf echte Cline-Befähigungen.

**Neue Tools im Jinja-Template testen**:
1. `execute_command` — Bash/Powershell Befehle (z.B. kompilieren, testen, laufen)
2. `search_files` — Grep/File-Suche (z.B. Strings in Codebase finden)
3. `web_search` — Web-Suche (z.B. Dokumentation nachschlagen)
4. `list_directory_tree` — Rekursives Directory-Listing (z.B. Projekt-Struktur verstehen)

**Test-Cases (TC6-TC9) — Jinja-Template-Validierung**:

| TC | Tool | Test | Success Criteria |
|----|------|------|------------------|
| TC6 | execute_command | `Run "echo hello"` | Returns output, no injection |
| TC7 | search_files | `Search "pattern" in /tmp/test_data` | Finds matches, JSON args valid |
| TC8 | web_search | `Search "Qwen3 Coder"` | API call structured (mock if offline) |
| TC9 | list_directory_tree | `List /tmp/test_data recursively` | Correct tree structure, depth respected |

**Schreibe `jinja_tests/run_jinja_phase6.py`**:
- Lade Tool-Schemas aus `jinja_tests/tools_schema.json` (zentral)
- Schreibe TC6-TC9 Test-Cases (Jinja-Template-Validierung mit neuen Tools)
- Nutze gleiche strikte Validierung wie Phase 5
- Führe Tool-Execution Simulation durch (wie `test_cline_flow.py`)
- Ergebnis: `test_results/phase6_extended_tools/Phase6-Test-Results.json`

**Tool Definitionen** — Zentral in `jinja_tests/tools_schema.json`:
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "execute_command",
        "description": "Execute shell command (bash/powershell)",
        "parameters": {
          "type": "object",
          "properties": {
            "command": {"type": "string", "description": "Command to execute"},
            "timeout": {"type": "integer", "description": "Timeout in seconds (optional, default 30)"}
          },
          "required": ["command"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "search_files",
        "description": "Search files by pattern (grep/ripgrep)",
        "parameters": {
          "type": "object",
          "properties": {
            "pattern": {"type": "string", "description": "Search pattern"},
            "path": {"type": "string", "description": "Directory path"},
            "recursive": {"type": "boolean", "description": "Recursive search (optional, default true)"}
          },
          "required": ["pattern", "path"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "web_search",
        "description": "Search web (mock if offline)",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "description": "Result limit (optional, default 5)"}
          },
          "required": ["query"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_directory_tree",
        "description": "List directory recursively",
        "parameters": {
          "type": "object",
          "properties": {
            "path": {"type": "string", "description": "Directory path"},
            "max_depth": {"type": "integer", "description": "Maximum depth (optional, default 3)"}
          },
          "required": ["path"]
        }
      }
    }
  ]
}
```

**Aktionen**:
- [ ] Erstelle `jinja_tests/tools_schema.json` mit oben definierten Tools
- [ ] Schreibe `jinja_tests/run_jinja_phase6.py` mit TC6-TC9
- [ ] Test-Cases laden Tools von `tools_schema.json` (nicht hardcoded!)
- [ ] Implementiere Tool-Simulation (fake execute_command, search_files, etc)
- [ ] Führe Tests aus: `python jinja_tests/run_jinja_phase6.py`
- [ ] Ergebnisse in `test_results/phase6_extended_tools/Phase6-Test-Results.json`
- [ ] Alle TC6-TC9 müssen PASS sein (oder Jinja-Template justieren)

---

### 6.3 Jinja-Template Versions-Dokumentation

**Erstelle `jinja_templates/JINJA-VERSIONS.md`** — Änderungshistorie pro Template-Variante:

```markdown
# Qwen3-Coder Jinja-Template Versionen

## v1.0: `chat_template_cline_optimized_v1.jinja` (2026-06-16)
**Source**: Unsloth Official + Issue #475 Guard Clause  
**Purpose**: Cline File Operations (read, list, write)  
**Format**: Qwen3 ChatML → OpenAI API (OVMS normalized)  
**Validated Tools**: read_file, list_files, write_file  
**Test Evidence**: Phase 5 (TC1-TC5) — 5/5 PASS  
**Status**: ✅ Production-Ready

Changes from Unsloth Official:
- Added IMPORTANT section with explicit guard: "Do NOT omit <tool_call> tag"
- Tool schema rendering clarified
- Parameter handling optimized for JSON safety

## v2.0: `chat_template_cline_optimized_v2.jinja` (2026-06-17)
**Purpose**: Extended Cline Tools (command exec, search, web, tree)  
**Format**: Same Qwen3 ChatML → OpenAI API  
**Targeted Tools**: execute_command, search_files, web_search, list_directory_tree  
**Test Status**: Phase 6 Testing (TC6-TC9) — PENDING  
**Status**: ⏳ In Refinement

Changes from v1:
- (TBD: If v2 needed after Phase 6 testing — document refinements here)
- Tool-specific instruction clarifications (if needed)

## Template Comparison Matrix

| Feature | v1.0 | v2.0 |
|---------|------|------|
| read_file | ✅ | ✅ |
| list_files | ✅ | ✅ |
| write_file | ✅ | ✅ |
| execute_command | ❌ | ⏳ |
| search_files | ❌ | ⏳ |
| web_search | ❌ | ⏳ |
| list_directory_tree | ❌ | ⏳ |
| OVMS Compatibility | ✅ | ✅ |
| JSON Parameter Safety | ✅ | ✅ |
| Q4 Quantization Robust | ✅ | ✅ |
```

**Aktionen**:
- [ ] Erstelle `jinja_templates/JINJA-VERSIONS.md`
- [ ] Dokumentiere v1.0 (Phase 5 validated) + Änderungen vs Original
- [ ] Placeholder für v2.0 (Phase 6, TBD nach Testing)

---

### 6.4 README — Jinja-Template Testing dokumentieren

**Update `C:\LLM\README.md`** mit Jinja-spezifischen Abschnitten:

```markdown
## Jinja-Template für Qwen3-Coder → Cline Optimierung

Dieses Projekt optimiert Jinja-Chat-Templates für Qwen3-Coder-30B, spezialisiert auf Cline (AI Code Editor).

### Jinja-Template Versionen

| Version | Phase | Tools | Status |
|---------|-------|-------|--------|
| v1.0 | Phase 5 | read_file, list_files, write_file | ✅ Validated |
| v2.0 | Phase 6 | + execute_command, search_files, web_search, list_directory_tree | ⏳ Testing |

Siehe `jinja_templates/JINJA-VERSIONS.md` für Details.

### Jinja-Template Testing & Validation

**Phase 5 - File Operations** (Baseline):
```bash
python jinja_tests/run_jinja_phase5.py
# Expected: TC1-TC5 PASS
# Validates: read_file, list_files, write_file with strict parameter checking
```

**Phase 6 - Extended Cline Tools** (New):
```bash
python jinja_tests/run_jinja_phase6.py
# Expected: TC6-TC9 PASS
# Validates: execute_command, search_files, web_search, list_directory_tree
```

**Realistic Cline Flow Test**:
```bash
python jinja_tests/test_jinja_cline_flow.py
# Multi-turn User→Tool→Result→Continuation scenario
```

### Template Deployment zu OVMS

```powershell
# Deploy v1.0 (File Ops)
.\jinja_deployment\deploy_jinja_template.ps1 -Version v1.0

# Deploy v2.0 (Extended Tools) — nach Phase 6 validation
.\jinja_deployment\deploy_jinja_template.ps1 -Version v2.0

# Restart OVMS for template changes to take effect
```

### Tool-Definitionen (Zentral)

Alle Tests nutzen Tool-Schemas von `jinja_tests/tools_schema.json`:
- Keine hardcoded Tool-Definitionen in Test-Scripts
- Single source of truth für Tool-API
- Einfache Erweiterung neuer Tools

Siehe `jinja_tests/README-JINJA-TESTS.md` für Details.

### Test-Philosophie

- **Strict Validation**: JSON parameter parsing, tool name allowlist, required params
- **No Hallucinations**: Forbid fake tools, validate schema adherence
- **Q4 Quantization Safe**: INT4 models tested, no parameter name corruption
- **Multi-turn Flows**: Tool Results properly integrated, Model Continuation working

```

**Aktionen**:
- [ ] Erweitere `README.md` mit oben definierten Abschnitten
- [ ] Linke auf `jinja_templates/JINJA-VERSIONS.md`
- [ ] Linke auf `jinja_tests/README-JINJA-TESTS.md`
- [ ] Linke auf `jinja_deployment/README-DEPLOYMENT.md`
- [ ] Deploy-Befehle dokumentieren

---

### 6.5 Jinja-Template Test-Dokumentation

**Erstelle `jinja_tests/README-JINJA-TESTS.md`** — Wie man Jinja-Templates mit verschiedenen Tool-Sets testet:

```markdown
# Jinja-Template Test Suite Documentation

## Überblick
- **Phase 5**: Jinja-Template mit File-Operation Tools validiert (TC1-TC5)
- **Phase 6**: Jinja-Template mit Cline-Tools erweitert (TC6-TC9)
- **Flow Test**: Realistic Cline multi-turn scenario (User→Tool→Result→Continuation)

## Test-Execution

### Phase 5: Jinja File Operations (Baseline)
```bash
python run_jinja_phase5.py
# Expected: 5/5 PASS
# Tools: read_file, list_files, write_file
# Output: test_results/phase5_file_ops/Phase5-Test-Results-FINAL.md
```

### Phase 6: Jinja Extended Cline Tools
```bash
python run_jinja_phase6.py
# Expected: 4/4 PASS (TC6-TC9)
# Tools: execute_command, search_files, web_search, list_directory_tree
# Output: test_results/phase6_extended_tools/Phase6-Test-Results.json
```

### Realistic Cline Flow Test
```bash
python test_jinja_cline_flow.py
# Expected: PASS
# Validates: User Prompt → Jinja Model Call → Tool Execution → Model Continuation
# Output: test_results/cline_flow/test_cline_flow_result.json
```

## Test-Philosophie (Jinja-fokussiert)

**Strict Tool Validation**:
- JSON Parameter Parsing: Alle Arguments müssen valid JSON sein
- Tool Name Allowlist: Keine halluzinierten Tools (nur definierte)
- Required Parameters: Jedes Tool braucht seine Required Params
- Multi-step Sequencing: TC6 (exec) + TC7 (search) im richtigen Kontext

**Jinja-Template Robustheit**:
- Q4 Quantization Safe: INT4 Models zeigen keine Parameter-Name Corruption
- Special Char Handling: Paths mit `/`, Strings mit `"`, etc. escaped korrekt
- ChatML Format Compliance: Qwen3 `<|im_start|>` / `<|im_end|>` korrekt

**Tool-Schema Centralization**:
- Alle Tools definiert in `tools_schema.json` (zentral)
- Tests laden Schemas via JSON, nicht hardcoded
- Neue Tools einfach in `tools_schema.json` hinzufügen, Tests laufen weiter

## Neue Tests hinzufügen

1. Tool zu `jinja_tests/tools_schema.json` hinzufügen
2. Test-Case schreiben:
   ```python
   def tc<N>_<tool_name>():
       payload = {
           "model": MODEL,
           "messages": [...],
           "tools": load_tools_schema(),  # Zentral geladen!
           ...
       }
       data = post_json(..., payload)
       result = validate_response(..., require_tool=True, allowed_tools=[...])
       return result
   ```
3. In `main()` Loop hinzufügen
4. Simulieren Tool-Execution (fake implementation)
5. Run `python run_jinja_phase6.py` und validieren

## Tool-Schemas (tools_schema.json)

Zentrales Archiv aller unterstützten Tools — einfach lesen & deployen:
```bash
cat jinja_tests/tools_schema.json | jq .tools[].function.name
# Output: read_file, list_files, write_file, execute_command, search_files, web_search, list_directory_tree
```
```

**Aktionen**:
- [ ] Erstelle `jinja_tests/README-JINJA-TESTS.md` mit oben definiertem Inhalt
- [ ] Dokumentiere Philosophy (Jinja-fokussiert, nicht generisch)
- [ ] Erkläre Tool-Schema Centralization

---

### 6.6 Jinja-Template Deployment-Scripts

**Erstelle `jinja_deployment/deploy_jinja_template.ps1`** — Deploy Jinja-Varianten zu OVMS:

```powershell
param(
    [ValidateSet("v1.0", "v2.0")]
    [string]$Version = "v1.0",
    [string]$OVMSModelDir = "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov",
    [switch]$RestartOVMS = $false
)

$TemplateFile = "C:\LLM\jinja_templates\chat_template_cline_optimized_$($Version).jinja"

if (-not (Test-Path $TemplateFile)) {
    Write-Error "Jinja-Template not found: $TemplateFile"
    exit 1
}

# Backup existing template
$BackupFile = "$OVMSModelDir\chat_template.jinja.backup_$(Get-Date -Format yyyyMMdd_HHmmss)"
if (Test-Path "$OVMSModelDir\chat_template.jinja") {
    Copy-Item "$OVMSModelDir\chat_template.jinja" $BackupFile
    Write-Host "Backup saved: $BackupFile"
}

# Deploy
Copy-Item $TemplateFile "$OVMSModelDir\chat_template.jinja" -Force
Write-Host "✓ Deployed Jinja v$Version to OVMS Model Dir"
Write-Host "  Source: $TemplateFile"
Write-Host "  Dest: $OVMSModelDir\chat_template.jinja"

if ($RestartOVMS) {
    Write-Host "`nRestarting OVMS..."
    Get-Process ovms -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "OVMS stopped. Please restart manually with: .\start_ovms_qwen.bat"
} else {
    Write-Host "`n⚠️  OVMS restart required for template changes to take effect"
    Write-Host "   Manual: Kill OVMS process and restart .\start_ovms_qwen.bat"
}
```

**Erstelle `jinja_deployment/validate_ovms_setup.ps1`** — Pre-Test Health Check:

```powershell
# Check OVMS running
$ovms = Get-Process ovms -ErrorAction SilentlyContinue
if (-not $ovms) {
    Write-Error "OVMS not running!"
    exit 1
}

# Check template file exists
$template = "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja"
if (-not (Test-Path $template)) {
    Write-Error "Jinja-Template missing: $template"
    exit 1
}

# Check API endpoint
$test = Invoke-WebRequest -Uri "http://localhost:9000/v3/models/qwen3-coder-30b-a3b-instruct-int4-ov" -TimeoutSec 5
if ($test.StatusCode -ne 200) {
    Write-Error "OVMS API not responding"
    exit 1
}

Write-Host "✓ OVMS running"
Write-Host "✓ Jinja-Template loaded"
Write-Host "✓ API endpoint ready"
```

**Aktionen**:
- [ ] Erstelle `jinja_deployment/deploy_jinja_template.ps1` mit oben definierten Inhalten
- [ ] Erstelle `jinja_deployment/validate_ovms_setup.ps1`
- [ ] Erstelle `jinja_deployment/README-DEPLOYMENT.md` (Dokumentation)

---

### 6.7 Git Cleanup Commit

**Aktionen**:
- [ ] Verschiebe Files in neue Verzeichnisse
- [ ] Lösche doppelte/alte Files aus root
- [ ] `git add -A` & `git commit -m "Phase 6: Cleanup & Reorganize"`

---

## Phase 6 Exit Criteria

- [x] Verzeichnis-Struktur reorganisiert
- [x] Alle Tests erweitert (TC1-TC9)
- [x] TC1-TC5 (Phase 5) still PASS ✅
- [x] TC6-TC9 (Phase 6) all PASS ✅
- [x] Template-Changelog dokumentiert
- [x] README erweitert
- [x] Test-Dokumentation geschrieben
- [x] Deploy-Script erstellt
- [x] Git cleanup commit

**When all above COMPLETE → Phase 7 (Documentation & Justification)**

---

## Files to Create/Move/Delete (Jinja-fokussiert)

### CREATE — Jinja Template Archive
- `jinja_templates/` directory
- `jinja_templates/chat_template_cline_optimized_v1.jinja` (renamed from existing)
- `jinja_templates/chat_template_cline_optimized_v2.jinja` (if Phase 6 refinements needed)
- `jinja_templates/JINJA-VERSIONS.md` (versioning & changelog)
- `jinja_templates/README-JINJA.md` (wie man Templates benutzt)

### CREATE — Jinja Test Suite
- `jinja_tests/` directory
- `jinja_tests/run_jinja_phase5.py` (moved+renamed from `run_phase5_tests.py`)
- `jinja_tests/run_jinja_phase6.py` (NEW — extended tools TC6-TC9)
- `jinja_tests/test_jinja_cline_flow.py` (moved from `test_cline_flow.py`)
- `jinja_tests/tools_schema.json` (NEW — centralized Tool definitions)
- `jinja_tests/README-JINJA-TESTS.md` (Test documentation)

### CREATE — Jinja Deployment
- `jinja_deployment/` directory
- `jinja_deployment/deploy_jinja_template.ps1` (Deploy Jinja v1.0/v2.0 to OVMS)
- `jinja_deployment/validate_ovms_setup.ps1` (Pre-test checks)
- `jinja_deployment/README-DEPLOYMENT.md` (Deployment guide)

### CREATE — Test Results Organization
- `test_results/phase5_file_ops/` directory
- `test_results/phase6_extended_tools/` directory
- `test_results/cline_flow/` directory

### MOVE (with rename)
- `C:\LLM\run_phase5_tests.py` → `jinja_tests/run_jinja_phase5.py`
- `C:\LLM\test_cline_flow.py` → `jinja_tests/test_jinja_cline_flow.py`
- `C:\LLM\debug_ovms.ps1` → `jinja_deployment/debug_ovms.ps1`
- `C:\LLM\chat_template_cline_optimized.jinja` → `jinja_templates/chat_template_cline_optimized_v1.jinja`

### DELETE (after move)
- `C:\LLM\run_phase5_tests.py`
- `C:\LLM\test_cline_flow.py`
- `C:\LLM\debug_ovms.ps1`
- `C:\LLM\chat_template_cline_optimized.jinja` (backup safe in jinja_templates/)
- `C:\LLM\chat_template_original.jinja` → `jinja_templates/chat_template_original.jinja` (MOVE, not delete)

### UPDATE
- `README.md` — add Jinja Template Testing section (6.4)
- `QWEN3-CODER-CLINE-PLAN.md` — update Phase checklist

---

## Next: Execute Phase 6 with `/clear`

```
/clear "Phase 6: Refinement (Cleanup, Test Extension, Reorganize)"
```

Follow checklist step-by-step.
