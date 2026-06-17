# Jinja-Template Test Suite Documentation

## Übersicht

Test suite zur Validierung von Qwen3-Coder Jinja-Templates für Cline.

- **Phase 5**: Jinja-Template mit File-Operation Tools validiert (TC1-TC5) ✅
- **Phase 6**: Jinja-Template mit Cline-Tools erweitert (TC6-TC9) ⏳
- **Flow Test**: Realistic Cline multi-turn scenario (User→Tool→Result→Continuation)

---

## Test-Execution

### Phase 5: Jinja File Operations (Baseline)

```bash
python jinja_tests/run_jinja_phase5.py
```

**Erwartet**: 5/5 PASS  
**Tools getestet**: read_file, list_files, write_file  
**Output**: `test_results/phase5_file_ops/Phase5-Test-Results.json`  
**Status**: ✅ COMPLETE (v1.0 validated)

**Test Cases**:
- TC1: Single tool call (read_file mit path)
- TC2: Structured args (list_files mit pattern)
- TC3: Tool result follow-up (read → describe)
- TC4: No-tool answer (2+2 ohne Tools)
- TC5: Multi-step sequencing (write_file → read_file)

### Phase 6: Jinja Extended Cline Tools

```bash
python jinja_tests/run_jinja_phase6.py
```

**Erwartet**: 4/4 PASS (TC6-TC9)  
**Tools getestet**: execute_command, search_files, web_search, list_directory_tree  
**Output**: `test_results/phase6_extended_tools/Phase6-Test-Results.json`  
**Status**: ⏳ Testing (v2.0 in validation)

**Test Cases**:
- TC6: execute_command (shell command execution)
- TC7: search_files (pattern matching in directories)
- TC8: web_search (information retrieval)
- TC9: list_directory_tree (directory traversal with depth)

### Realistic Cline Flow Test

```bash
python jinja_tests/test_jinja_cline_flow.py
```

**Erwartet**: PASS  
**Szenario**: Multi-turn User→Tool→Result→Continuation  
**Output**: `test_results/cline_flow/test_cline_flow_result.json`  
**Status**: ✅ Available

---

## Test-Philosophie (Jinja-fokussiert)

### Strict Tool Validation

**JSON Parameter Parsing**: 
- Alle Argumente müssen valid JSON sein
- Kein Halluzinieren von Tool-Argumenten
- Required params müssen vorhanden sein

**Tool Name Allowlist**: 
- Nur definierte Tools erlaubt
- Keine halluzinierten/erfundenen Tools
- Fehler bei unerwarteten Tool-Namen

**Required Parameters**: 
- read_file: `path` required
- list_files: `path` required
- write_file: `path`, `content` required
- execute_command: `command` required
- search_files: `pattern`, `path` required
- web_search: `query` required
- list_directory_tree: `path` required

**Multi-step Sequencing**: 
- Tool-Calls müssen in korrekter Reihenfolge erfolgen
- Tool Results korrekt integriert
- Model Continuation nach Tool-Responses

### Jinja-Template Robustheit

**Q4 Quantization Safe**: 
- INT4 Models zeigen keine Parameter-Name Corruption
- Keine Degradation bei GGUF/INT4 Quantization

**Special Character Handling**: 
- Paths mit `/`, `\`
- Strings mit `"`, `'`, backticks
- Unicode in Tool-Arguments
- Escape-Sequenzen korrekt

**ChatML Format Compliance**: 
- Qwen3 `<|im_start|>` / `<|im_end|>` korrekt
- Tool wrapper format valid
- Parameter rendering eindeutig

### Tool-Schema Centralization

**Single Source of Truth**:
- Alle Tools definiert in `jinja_tests/tools_schema.json`
- Tests laden Schemas via JSON, nicht hardcoded
- Einfache Erweiterung neuer Tools

**Schema Structure**:
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "tool_name",
        "description": "...",
        "parameters": {
          "type": "object",
          "properties": { ... },
          "required": [ ... ]
        }
      }
    }
  ]
}
```

---

## Neue Tests hinzufügen

### Schritt 1: Tool zu tools_schema.json hinzufügen

```json
{
  "type": "function",
  "function": {
    "name": "my_new_tool",
    "description": "Tool description",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {"type": "string", "description": "..."},
        "param2": {"type": "integer", "description": "..."}
      },
      "required": ["param1"]
    }
  }
}
```

### Schritt 2: Test-Case schreiben

```python
def tc<N>_<tool_name>():
    """TC<N>: <Tool Name> — STRICT: <validation requirement>"""
    print(f"\n[TC<N>] <Tool Name>")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Use my_new_tool to do something"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    log_response(<N>, data)
    result = validate_response(
        <N>, data,
        require_tool=True,
        allowed_tools=[...]
    )

    # Additional validation specific to this tool
    if result["tool_calls"]:
        # Add tool-specific checks here
        pass

    return result
```

### Schritt 3: Test in main() Loop hinzufügen

```python
def main():
    # ... health check ...
    results = []
    results.append(tc6_execute_command())
    time.sleep(1)
    results.append(tc7_search_files())
    # ADD NEW TEST HERE:
    time.sleep(1)
    results.append(tc<N>_<tool_name>())
    # ...
```

### Schritt 4: Run & Validate

```bash
python jinja_tests/run_jinja_phase6.py
# Expected: TC<N> PASS
```

---

## Tool-Schemas (tools_schema.json)

Zentrales Archiv aller unterstützten Tools:

```bash
# Alle Tool-Namen auflisten:
cat jinja_tests/tools_schema.json | python -m json.tool | grep '"name"'
# Output:
#   "name": "read_file",
#   "name": "list_files",
#   "name": "write_file",
#   "name": "execute_command",
#   "name": "search_files",
#   "name": "web_search",
#   "name": "list_directory_tree"
```

---

## Debugging & Troubleshooting

### OVMS nicht erreichbar

```powershell
# Check ob OVMS läuft:
Get-Process ovms

# Check Endpoint:
curl http://localhost:9000/v3/models/qwen3-coder-30b-a3b-instruct-int4-ov
```

### Template-Fehler in Response

- Prüfe `test_output_tc<N>.json` für raw API response
- Suche nach "error" field im JSON
- Prüfe Jinja-Syntax in deployed template

### Tool-Call Parser Error

- Verifikation: args_str muss valid JSON sein
- Häufig: Unescaped quotes oder special chars
- Lösung: Template Guard-Clauses prüfen

### Q4 Quantization Issues

- INT4 Models können Parameter-Namen verderben
- Symptom: "unkown parameter" Fehler
- Lösung: Template v1.0 bewährt für diese Fälle

---

## Test Results Interpretation

### PASS Status

Alle Validierungsschritte erfolgreich:
- API-Response received (kein HTTP error)
- Response format valid (choices[], message[])
- Tool calls strukturell korrekt (function.name, function.arguments)
- Arguments valid JSON
- Required params vorhanden
- Tool names in allowlist

### FAIL Status mit Errors

Beispiele:

- `no_tool_call`: Tool-Call erwartet, aber nicht generiert
- `invalid_tool`: Tool-Name nicht in allowlist
- `invalid_json_args`: Arguments können nicht als JSON parsed werden
- `missing_param`: Required parameter fehlt
- `wrong_tool_count`: Falsche Anzahl von Tool-Calls
- `wrong_tool_name`: Falscher Tool-Name
- `api_error`: OVMS API error
- `no_choices`: Response hat keine choices

---

## Phase Progression

**Phase 5**: ✅ COMPLETE
- File Operations baseline etabliert
- v1.0 Template validated
- 5/5 Test-Cases PASS

**Phase 6**: ⏳ IN PROGRESS
- Extended Tools validieren (TC6-TC9)
- v2.0 Template refinement if needed
- Target: 4/4 Test-Cases PASS

**Phase 7**: ⏹️ PENDING
- Documentation & Justification
- Final README writeup
- Archive & Release

---

## Ressourcen

- Template-Definitionen: `jinja_templates/JINJA-VERSIONS.md`
- Deploy-Anleitung: `jinja_deployment/README-DEPLOYMENT.md`
- Master-Plan: `QWEN3-CODER-CLINE-PLAN.md`
- Test-Results: `test_results/`
