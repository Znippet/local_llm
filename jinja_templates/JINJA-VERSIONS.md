# Qwen3-Coder Jinja-Template Versionen

## v1.0: `chat_template_cline_optimized_v1.jinja` (2026-06-16)

**Quelle**: Unsloth Official + Issue #475 Guard Clause  
**Purpose**: Cline File Operations (read_file, list_files, write_file)  
**Format**: Qwen3 ChatML → OpenAI API (OVMS normalized)  
**Validated Tools**: read_file, list_files, write_file  
**Test Evidence**: Phase 5 (TC1-TC5) — 5/5 PASS  
**Status**: ✅ Production-Ready  

### Änderungen vs. Unsloth Official:
- IMPORTANT section mit expliziter Guard: "Do NOT omit <tool_call> tag"
- Tool-Schema-Rendering klarifiziert
- Parameter-Handling für JSON-Sicherheit optimiert
- Minimalistisch: kein Vision/Thinking, fokussiert auf Cline File-Ops

### Bewährte Test-Cases:
- TC1: Single tool call (read_file)
- TC2: Structured args (list_files mit pattern)
- TC3: Tool result follow-up (read → describe)
- TC4: No-tool answer (2+2 ohne Tools)
- TC5: Multi-step sequencing (write → read)

---

## v2.0: `chat_template_cline_optimized_v2.jinja` (2026-06-17)

**Purpose**: Extended Cline Tools (execute_command, search_files, web_search, list_directory_tree)  
**Format**: Qwen3 ChatML → OpenAI API (OVMS compatible)  
**Target Tools**: execute_command, search_files, web_search, list_directory_tree  
**Test Status**: Phase 6 Testing (TC6-TC9) — PENDING  
**Status**: ⏳ In Refinement  

### Planned Changes from v1:
- Enhanced tool description clarity for command execution
- Improved parameter validation for path-based operations
- (Documentation TBD after Phase 6 testing results)

### Planned Test Cases:
- TC6: execute_command (bash/powershell)
- TC7: search_files (pattern matching in directories)
- TC8: web_search (information retrieval)
- TC9: list_directory_tree (directory traversal with depth limits)

---

## Template Comparison Matrix

| Feature | v1.0 | v2.0 |
|---------|------|------|
| read_file | ✅ Validated | ✅ Validated |
| list_files | ✅ Validated | ✅ Validated |
| write_file | ✅ Validated | ✅ Validated |
| execute_command | ❌ Not in v1 | ⏳ Testing |
| search_files | ❌ Not in v1 | ⏳ Testing |
| web_search | ❌ Not in v1 | ⏳ Testing |
| list_directory_tree | ❌ Not in v1 | ⏳ Testing |
| OVMS Compatibility | ✅ Confirmed | ✅ Expected |
| JSON Parameter Safety | ✅ Confirmed | ✅ Expected |
| Q4 Quantization Robust | ✅ Confirmed | ✅ Expected |
| Multi-step Sequencing | ✅ Confirmed | ✅ Expected |

---

## Deployment & Activation

Deploy v1.0 to OVMS:
```powershell
.\jinja_deployment\deploy_jinja_template.ps1 -Version v1.0 -RestartOVMS $true
```

Deploy v2.0 after Phase 6 validation:
```powershell
.\jinja_deployment\deploy_jinja_template.ps1 -Version v2.0 -RestartOVMS $true
```

---

## Test Results Archive

**Phase 5 Results**: `test_results/phase5_file_ops/Phase5-Test-Results.json`
- Status: ✅ 5/5 PASS
- Date: 2026-06-17
- Template: v1.0

**Phase 6 Results**: `test_results/phase6_extended_tools/Phase6-Test-Results.json`
- Status: ⏳ Pending
- Date: 2026-06-17
- Template: v2.0 (in testing)

---

## Decision Log

| Version | Decision | Rationale |
|---------|----------|-----------|
| v1.0 | Base on Unsloth Official | Universally tested, maintained |
| v1.0 | Add Issue #475 Guard Clause | Reliability boost, non-invasive |
| v1.0 | Pure XML (not JSON-in-XML) | Simpler parser, faster execution |
| v1.0 | Minimize bloat | No vision/reasoning/thinking logic needed |
| v2.0 | Extend to command/search tools | Real Cline workflows require these |
| v2.0 | Keep v1 format/philosophy | Proven working, no breaking changes |

---

## Architecture Notes

**v1.0 & v2.0 Compatibility**:
- Both use Qwen3 ChatML native format
- OVMS converts to OpenAI API wrapper automatically
- Tool schema handling identical across versions
- Multi-turn conversation state managed by client (Cline)
- No template-side session tracking

**Why Minimal v1 Works**:
1. Cline handles tool orchestration (client-side)
2. OVMS bridges Qwen3→OpenAI format automatically
3. Guard clauses prevent parser confusion
4. Structured JSON args eliminate ambiguity

---

## Next Steps

- **Phase 6**: Validate TC6-TC9 with v2.0
- **If v2.0 PASS**: Use v2.0 as production default
- **If v2.0 FAIL**: Document refinements, iterate
- **Phase 7**: Documentation & justification writeup
