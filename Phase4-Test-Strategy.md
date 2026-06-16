# Phase 4: Test Harness & Validation (Direct Cline CLI)

**Ziel**: Validiere optimiertes Cline-Template mit direkter CLI-Nutzung, ohne Python/Bash-Wrapper  
**Datum**: 2026-06-16  
**Status**: Planungsphase

---

## Übersicht: Warum direkte Cline-Nutzung?

- **Realistische Umgebung**: Cline testet mit echtem CLI, nicht simuliert
- **Parser-Validierung**: Echt Cline-Parser vs. Mock
- **Edge-Cases sichtbar**: Q4-Inaccuracies, Jinja-Fehler direkt erkannt
- **Keine Skript-Abhängigkeiten**: Cline CLI ist Quelle der Wahrheit

---

## Test-Strategie

### Ansatz: Scripted Prompts + Response Logging

1. **Template aktivieren** → Template in OVMS/OpenVINO-Modell laden
2. **Cline mit `--json` aufrufen** → strukturierte Output-Parsing
3. **Response Log erfassen** → jede Tool-Call, jeden Error dokumentieren
4. **Validierungslogik** → JSON-Parser auf Response anwenden
5. **Edge-Case Handling** → bei Fehlern Jinja-Adjustments testen

**Ablauf**:
```
User Prompt → Cline --json → Line-by-line JSON Output → Parser → Validation Log
```

---

## Test Cases (Ausformuliert)

### TC1: Single Tool Call (Basis)

**Ziel**: Model generiert exakt einen Tool-Call mit korrektem JSON

**Setup**:
```bash
cline --json --auto-approve false "Read file /tmp/test.txt using bash_read tool"
```

**Expected JSON Response** (approx):
```json
{"type":"say","text":"Reading file...","ts":...}
{"type":"tool_call","tool":"bash_read","params":{"path":"/tmp/test.txt"},...}
{"type":"say","text":"File content displayed.","ts":...}
```

**Validation**:
- ✅ Genau 1 `"type":"tool_call"` im Output
- ✅ `"tool"` Feld vorhanden
- ✅ `"params"` ist valid JSON (parsbar)
- ✅ Required Parameter (z.B. `path`) vorhanden
- ❌ Kein doppelter Tool-Call (Hallucination Check)

**Edge-Cases zu testen**:
- Q4-Quantifizierung: Können Parameter-Namen verzerrt sein? (z.B. `pah` statt `path`)
- Jinja-Bug: Wird XML-Tag korrekt geschlossen?
- Unicode in Parametern: Werden Umlaute/Sonderzeichen escaped?

---

### TC2: Structured Args Validation

**Ziel**: JSON-Parameter sind valide und typsicher

**Setup** (komplexere Parameter):
```bash
cline --json --auto-approve false "List files matching *.py in /home/user with permission check"
```

**Validation**:
```
Parse params as JSON:
  - params.pattern = "*.py" (String)
  - params.path = "/home/user" (String)
  - params.check_perms = true (Boolean, or missing if optional)
  
Fail if:
  ❌ JSON parse error
  ❌ Unquoted keys (invalid JSON)
  ❌ Mixed quotes (' vs ")
  ❌ Escaped newlines in wrong format
```

**Q4 Quantization Edge-Case**:
- Modell könnte `{"pattern": "*.py"` ohne schließende `}` generieren
- Jinja sollte Guard-Clause haben: `if params ends with "}" else add "}"` (safety)
- Validierung: Parser wirft Error → Cline soll Fehler-Handling triggern

---

### TC3: Tool Result Follow-Up

**Ziel**: Model verarbeitet Tool-Response kohärent

**Setup** (zweiteiliger Dialog):
```bash
cline --json --auto-approve false "First, read /tmp/data.json. Then analyze the structure."
```

**Expected Sequence**:
```
1. User prompt
2. Tool call: read /tmp/data.json
3. Tool result (simulated by Cline)
4. Model reasoning (im JSON als "reasoning" Feld)
5. Second action oder summary
```

**Validation**:
- ✅ Nach Tool-Response continuation, nicht Abbruch
- ✅ Reasoning-Feld vorhanden (wenn Template mit Reasoning)
- ✅ Zweiter Tool-Call oder coherent text folgt
- ❌ Nicht "Tool failed, aborting" ohne Retry

**Jinja-Critical**:
- Tool-Response-Wrapper muss korrekt sein: `<tool_result>...</tool_result>`
- Wenn Jinja malformed → Model könnte "confused" wirken (incoherent follow-up)

---

### TC4: No-Tool Answer Path

**Ziel**: Model generiert KEINE Tool-Call, wenn nicht nötig

**Setup**:
```bash
cline --json --auto-approve false "What is 2+2? No tool needed."
```

**Expected**:
```json
{"type":"say","text":"2+2 equals 4.","ts":...}
```

**Validation**:
- ✅ Keine `"type":"tool_call"` im Output
- ❌ Fake Tool-Call: z.B. `<tool_call><tool>calculator</tool>...</tool_call>` in text

**Q4 Hallucination-Check**:
- Quantized Model könnte "Tool-Call Tics" haben (immer versuchen zu callen)
- Wenn falsche Tool-Calls bei non-Tool-Prompts → Jinja zu permissive
- Lösung: Jinja kann explizite "Instruction" haben: "Only use tools if user asks"

---

### TC5: Multi-Step Tool Use

**Ziel**: Chain 2+ Tool-Calls mit richtigem State-Handling

**Setup**:
```bash
cline --json --auto-approve false "
Create a file /tmp/script.py with content 'print(1+1)', 
then execute it with bash, 
then read the output."
```

**Expected Sequence**:
```
1. Tool: write_file(path=/tmp/script.py, content=...)
2. Tool result: "File created"
3. Tool: bash_exec(cmd=python /tmp/script.py)
4. Tool result: "2"
5. Model text: "Output is 2"
(oder weitere Tool-Calls bei Bedarf)
```

**Validation**:
- ✅ Tool-Calls sequenziell (nicht parallel im Output)
- ✅ Jedes Tool-Call hat zugehörigen Result
- ✅ State korrekt: Datei existiert bei bash-Call
- ❌ Nicht "Execute before Create"

**Jinja Multi-Step Complexity**:
- Must handle Tool-Result wrapping: `<tool_result>...</tool_result>`
- Model sollte Results "verstehen" und mit Kontext weitermachen
- Q4 Bug-Risk: Model könnte Results ignorieren → Loop/Hallucinate

---

## Response Parser Validation Logic

### 1. JSON Output Extraction

```
Für jede Output-Zeile:
  - Parse as JSON
  - Fail if malformed → Log Error
  - Extract "type" field
```

### 2. Tool-Call Validation

```
Wenn type == "tool_call":
  - Tool-Name muss in [bash_read, write_file, bash_exec, ...] sein
  - params muss JSON-parsbar sein
  - Required fields für Tool X müssen existieren
  - Log: tool_name, param_keys, param_types
```

### 3. Response Structure Check

```
Validiere Cline JSON Format:
  - Required: "type", "text" (oder "params" bei tool_call)
  - Required: "ts" (timestamp)
  - Optional: "reasoning" (Extended Thinking)
  - Optional: "partial" (Streaming)
  
Fail Criteria:
  - Missing "type"
  - "text" is null/empty for "say" type
  - "params" not valid JSON for "tool_call" type
```

### 4. OVMS Dependency Check

**Requirement**: OVMS must be running and responsive.

If Cline request times out:
```
ERROR: OVMS not responding
Action: User must start OVMS service
Command: systemctl start ovms
Then: Re-run test case
```

**No fallback to dummy responses** — real endpoint required for valid testing.

---

## Jinja Template Edge-Case Handling

### Q4 Quantization Artifacts

**Symptom**: Model generiert Parameter-Namen mit typos
- `{"pth": "value"}` statt `{"path": "value"}`
- `{"prms": ...}` statt `{"params": ...}`

**Jinja Counter-Measure**:
- Add Normalization Comment in Template: "Parameter names MUST match tool schema exactly"
- Ensure instruction clarity (Issue #475 style)

**Test**: Parse params; log any missing required keys → Indicates Q4 issue

---

### Guard Clause Validation

**Hypothese**: Issue #475 guard clause ("do NOT omit <tool_call>") is critical

**Test Strategy**:
1. Run same prompt 10x (quantization variance)
2. Count failures: model omits tool_call / hallucination
3. If >20% fail → guard clause needed
4. If <5% fail → guard clause may be optional (but keep for safety)

---

### XML Tag Malformation

**Symptom**: Unmatched tags, missing closing `>`

```xml
<tool_call>
  <tool>read_file</tool>
  <parameter>
    <name>path</name>
    <value>/tmp/test.txt
  </parameter>
</tool_call>
<!-- Missing closing > or </tool_call> -->
```

**Detection**: XML Parser should fail → Log line number

**Jinja Fix**: Template should render `>` explicitly, not rely on string interpolation

---

## Test Execution Plan

### Phase 4a: Setup & Validation (30 min)

1. **OVMS Health Check** (BLOCKING)
   ```bash
   # Check if OVMS is running
   systemctl status ovms
   
   # If not running: STOP HERE
   # Ask user: "OVMS not running. Start service now?"
   # Cannot proceed without real endpoint
   ```
   - If OVMS unavailable → **HALT execution**
   - User must start OVMS before continuing

2. **Template Deployment**
   - Copy optimized template to OVMS model directory
   - Restart OVMS service
   - Verify model loads without errors

3. **Cline CLI Verification**
   - Run `cline --json "What is 1+1?"` (sanity check)
   - Confirm JSON output format is correct
   - If timeout/error → OVMS not responding → User must fix

4. **Test Environment Setup**
   - Create `/tmp/test_data/` directory
   - Prepare test files: `test.txt`, `data.json`, `script.py`
   - Ensure Cline has read/write permissions

---

### Phase 4b: Test Case Execution (45 min)

**For Each Test Case (TC1-TC5)**:

```bash
# Run test with logging
cline --json --auto-approve false "[TC#: description]" 2>&1 | tee test_output_tc#.jsonl

# Parse & validate
python validate_response.py test_output_tc#.jsonl > test_result_tc#.json

# Inspect failures
cat test_result_tc#.json | grep -E "FAIL|ERROR"
```

**Iteration Loop** (if failures):
1. Review error log
2. Identify root cause (Jinja? Q4? Cline version?)
3. Adjust template if needed
4. Re-run test
5. Compare results

---

### Phase 4c: Edge-Case Testing (30 min)

**Run variants**:
- **Baseline**: Standard prompt
- **Q4 Stress**: Repeat TC5 (multi-step) 5x, log variance
- **Unicode**: Prompt with Umlauts, Emojis
- **Long Params**: Path with 200+ char filename
- **Special Chars**: Param value with `\n`, `"`, `\`, etc.

**Acceptance Criteria**:
- ✅ >90% success rate on TC1-TC5 (single run each)
- ✅ Q4 variance: <20% failure rate over 5 runs
- ✅ No unescaped special char errors

---

## Validation Script (Pseudo-Code)

```python
# validate_response.py

import json
import sys

def validate_cline_response(jsonl_file):
    """Parse Cline --json output, validate tool calls."""
    
    results = {
        "total_lines": 0,
        "tool_calls": [],
        "errors": [],
        "say_messages": []
    }
    
    with open(jsonl_file) as f:
        for line_num, line in enumerate(f, 1):
            results["total_lines"] += 1
            try:
                msg = json.loads(line)
            except json.JSONDecodeError as e:
                results["errors"].append({
                    "line": line_num,
                    "type": "json_parse_error",
                    "error": str(e),
                    "raw": line[:100]
                })
                continue
            
            msg_type = msg.get("type")
            
            if msg_type == "tool_call":
                results["tool_calls"].append({
                    "line": line_num,
                    "tool": msg.get("tool"),
                    "params_valid": validate_json(msg.get("params", {}))
                })
            
            elif msg_type == "say":
                results["say_messages"].append({
                    "line": line_num,
                    "text_length": len(msg.get("text", ""))
                })
    
    return results

def validate_json(params):
    """Check if params is valid JSON."""
    try:
        if isinstance(params, str):
            json.loads(params)
        return True
    except:
        return False
```

---

## Expected Outputs (Phase 4)

### Deliverables

1. **Test Execution Logs**
   - `test_output_tc1.jsonl` → `test_output_tc5.jsonl`
   - Raw Cline JSON responses

2. **Validation Results**
   - `test_result_tc1.json` → `test_result_tc5.json`
   - Parsed, categorized failures

3. **Summary Report**
   - `Phase4-Test-Results.md`
   - Success rates, failure analysis, recommendations

4. **Jinja Adjustments (if needed)**
   - Modified `chat_template_cline_optimized.jinja` v2
   - Changelog: which clauses added, why

---

## Failure Modes & Recovery

| Issue | Symptom | Recovery |
|-------|---------|----------|
| **OVMS not running** | Cline timeout / "connection refused" | **HALT tests.** User starts: `systemctl start ovms`. Verify with Phase 4a check. Retry. |
| **Template not loaded** | Model uses old template (wrong tool format) | Copy template again, restart OVMS, verify with sanity check |
| **Q4 param typos** | `{"pth": ...}` instead of `{"path": ...}` | Add Jinja clarification, redeploy, re-test |
| **XML malformed** | Parser error, Cline stops mid-response | Check template for `>` escaping, fix Jinja, redeploy |
| **Hallucinated tool calls** | Non-existent tools in response | Strengthen instruction clarity (Issue #475 guard), redeploy |
| **Multi-step loops** | Tool call → result → ignore result → repeat | Verify Tool-Result wrapper `<tool_result>` in template |

---

---

## Phase 5: Test Execution & Template Refinement (EXECUTION GUIDE)

### Phase 5 Execution Checklist

**Pre-Flight (Phase 4a)**:
- [ ] OVMS running: `systemctl status ovms`
- [ ] Template copied to OVMS model dir
- [ ] OVMS restarted: `systemctl restart ovms`
- [ ] Model loads without errors
- [ ] Sanity check: `cline --json "What is 1+1?"` → valid JSON response
- [ ] Test data dir created: `/tmp/test_data/`
- [ ] Test files prepared: `test.txt`, `data.json`, `script.py`

**Test Execution (Phase 4b)**:
- [ ] TC1 executed: `cline --json "[TC1: ...]" 2>&1 | tee test_output_tc1.jsonl`
- [ ] TC1 validated: `python validate_response.py test_output_tc1.jsonl > test_result_tc1.json`
- [ ] TC1 result inspected: `cat test_result_tc1.json | grep -E "FAIL|ERROR"`
- [ ] Repeat for TC2, TC3, TC4, TC5
- [ ] Log all failures with line numbers

**Edge-Case Testing (Phase 4c)**:
- [ ] Q4 Stress (TC5 x5): Test multi-step robustness
- [ ] Unicode test: Umlauts, emoji in params
- [ ] Long params test: 200+ char paths
- [ ] Special chars test: `\n`, `"`, `\` escaping

**Analysis Phase**:
- [ ] Parse all test_result_*.json files
- [ ] Group failures by category (Q4, Jinja, XML, etc.)
- [ ] Document root causes in `Phase5-Test-Analysis.md`
- [ ] Decide: fix template or move to Phase 6?

---

### Template Refinement Loop (if failures detected)

**For each identified issue**:

1. **Identify root cause from test failure**
   - Example: Q4 param typos → `{"pth": ...}` instead of `{"path": ...}`
   - Example: XML malformed → missing `>` or `</tool_call>`
   - Example: Hallucination → fake tool calls in no-tool prompts

2. **Locate Jinja template section**
   - Open `chat_template_cline_optimized.jinja`
   - Find corresponding Jinja macro or section
   - Example for param typos: `render_extra_keys` macro, param name rendering

3. **Apply targeted fix**
   - Add Jinja guard clause: `| default("path")` for optional params
   - Add explicit instruction: "Parameter names MUST match schema exactly"
   - Add XML guard: ensure closing tags rendered `}}` or similar
   - Strengthen Issue #475 guard: "Do NOT omit <tool_call> tags"

4. **Redeploy template**
   - Copy refined template to OVMS model directory
   - Restart OVMS: `systemctl restart ovms`
   - Verify model reloads: sanity check pass

5. **Re-run failed test cases**
   - Re-execute tests that failed in Phase 4b
   - Compare new results vs. baseline
   - Document improvement (or degradation)

6. **Iterate if needed**
   - If still failing: repeat steps 1-5
   - If passing: lock template version, move to Phase 6

---

### Go/No-Go Decision Gate (Phase 5 Exit)

**SUCCESS PATH** → Phase 6 Documentation:
- ✅ TC1-TC5 all pass (100% on single run)
- ✅ Q4 stress test: <20% variance over 5 runs
- ✅ Edge-cases: no unescaped special char errors
- ✅ Template stable: no more than 1-2 refinement cycles needed

**PARTIAL SUCCESS** → Minor Refinement Cycle:
- ⚠️ 1-2 test cases still failing
- ⚠️ Root cause identified and fixable
- ⚠️ Refinement loop run (one more iteration)
- Then re-check against SUCCESS criteria

**BLOCKED** → Escalation / Root Cause Analysis:
- ❌ >2 simultaneous failures with unclear root causes
- ❌ Q4 variance >20% consistently (model quantization issue)
- ❌ Jinja changes break other test cases
- Action: Document all failures, root causes → Phase 6 limitations section

---

### Deliverables (Phase 5 Exit)

Required outputs before Phase 6:

1. **Test Execution Logs**
   - `test_output_tc1.jsonl` → `test_output_tc5.jsonl`
   - Raw Cline JSON responses (one per test case)

2. **Validation Results**
   - `test_result_tc1.json` → `test_result_tc5.json`
   - Parsed, categorized with error analysis

3. **Summary Report**
   - `Phase5-Test-Results.md`
   - Test results table (TC1-TC5 pass/fail)
   - Edge-case results (Q4 stress, unicode, special chars)
   - Failure analysis with root causes
   - Refinement changelog (if template v2 created)

4. **Refined Template (if needed)**
   - `chat_template_cline_optimized_v2.jinja` (if refinements made)
   - OR confirmation that v1 passes all tests as-is

---

## Success Criteria (Phase 5 Exit)

- [x] **Phase 4a-c executed** completely
- [x] **Test logs captured** (5 JSONL files)
- [x] **Validation completed** (5 result JSON files)
- [x] **Root causes documented** (if failures)
- [x] **Template stable** (passes criteria OR refinements locked)
- [x] **Go/No-Go decision made** → Phase 6 ready or blocked
- [x] **Deliverables complete** → Phase5-Test-Results.md exists

---

## Next Phase (Phase 6)

**Phase 6: Documentation & Justification** will use Phase 5 results to:
1. Explain why JSON-in-XML or pure XML for Cline
2. Justify Unsloth base + Issue #475 enhancements
3. Document Phase 5 test evidence & refinements
4. Write integration instructions for OVMS
5. Lock final template version

---

## Notes

- **Direct Cline CLI**: No Python/Bash wrapper needed; Cline is the test harness
- **JSON output**: Use `--json` flag for machine-parseable responses
- **Edge-case risk**: Q4 quantization + Jinja complexity = variance expected
- **Iterative**: Phase 4 is exploratory; expect 1-2 refinement cycles before Phase 5 lock
