# Phase 7: Template Refinement & Re-Testing

**Status**: PLANNING  
**Previous**: Phase 6 COMPLETE (9/9 baseline PASS) + Phase 6.5 AUDIT (tool sequencing FAIL)  
**Goal**: Fix template, validate real Cline workflows  
**Expected Duration**: 2-3 hours

---

## Problem Analysis

### Current Issue: Tool Sequencing Fails

**Test Result (Phase 6.5)**:
```
Scenario: "Add multiply function to Python file"
Expected: read_file → write_file → execute_command
Actual:   read_file ✓, write_file ✗ (wrong tool called)
Result:   FAIL
```

### Root Cause: Template Rendering

**v1.0 (Current - BROKEN)**:
- Manual XML string concatenation (117 lines)
- Iterates tool.parameters.properties manually
- String escaping errors possible
- Model gets malformed XML → confusion → wrong tool picks

**Hack (Qwen 3.5 - PROVEN BETTER)**:
- Single line: `{{ tool | tojson }}`
- JSON serialization (atomic, reliable)
- No manual string building
- Model gets clean JSON → understands tools → correct sequencing

### Why Hack Works Better
1. **JSON is atomic** — either valid or parse fails (no partial/malformed)
2. **No escaping errors** — tojson handles all edge cases
3. **Simpler for model** — JSON structure clearer than nested XML tags
4. **Proven in field** — used for Qwen 3.5-35B A3B (larger model)

---

## Phase 7 Goals

### Primary Goal: Fix Tool Sequencing
- [ ] Adapt Hack template for Qwen3-Coder-30B
- [ ] Remove unnecessary Vision/Video macros (Cline doesn't need)
- [ ] Keep tojson-based tool serialization
- [ ] Deploy v2.0 template

### Secondary Goals: Validate Real Workflows
- [ ] Phase 6.5 tests PASS with v2.0
- [ ] Realistic code edit workflow works
- [ ] Error handling consistent
- [ ] Multi-turn tool sequences reliable

### Tertiary Goals: Maintain Stability
- [ ] Phase 5-6 tests still PASS (no regression)
- [ ] Backward compatible messaging format
- [ ] Same ChatML compliance

---

## Key Changes: v1.0 → v2.0

### Change 1: Tool Rendering (Lines 45-52)

**BEFORE (v1.0 - Manual XML)**:
```jinja
{%- if tools is iterable and tools | length > 0 %}
    {{- "\n\n# Tools\n\nYou have access to the following functions:\n\n" }}
    {{- "<tools>" }}
    {%- for tool in tools %}
        {{- "\n<function>\n<name>" ~ tool.name ~ "</name>" }}
        {{- '\n<description>' ~ (tool.description | trim) ~ '</description>' }}
        ...  (30+ more lines of manual XML building)
{%- endif %}
```

**AFTER (v2.0 - JSON serialization)**:
```jinja
{%- if tools and tools is iterable and tools is not mapping %}
    {{- '<|im_start|>system\n' }}
    {{- "# Tools\n\nYou have access to the following functions:\n\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>" }}
{%- endif %}
```

**Benefit**: 5 lines instead of 30+, no manual escaping, guaranteed valid JSON

### Change 2: Remove Vision/Video (Not needed for Cline)

**REMOVE** (Hack macros, lines 1-41):
```jinja
{%- set image_count = namespace(value=0) %}
{%- set video_count = namespace(value=0) %}
{%- macro render_content(content, do_vision_count, is_system_content=false) %}
    ... (40 lines of vision/video handling)
{%- endmacro %}
```

**REASON**: 
- Cline is code editor, not vision agent
- Adds 30+ lines of unnecessary complexity
- Increases parse errors
- Keep template minimal & focused

### Change 3: Keep Cline-Specific Guard Clauses

**KEEP** (v1.0 feature):
```jinja
Do NOT omit the initial <tool_call> tag ⭐ This is critical
```

**REASON**: Empirically reduces hallucinations

---

## Testing Plan

### Phase 7a: Template Modification
1. Read Hack template (lines 45-52 for tool rendering)
2. Copy Hack tool-rendering logic
3. Remove Vision/Video macros
4. Keep v1.0's guard clauses
5. Merge into v2.0 template
6. Deploy to OVMS

### Phase 7b: Re-run Phase 5-6 Baseline
**Goal**: Ensure no regression
```bash
python jinja_tests/run_jinja_phase5.py
# Expected: 5/5 PASS (unchanged)

python jinja_tests/run_jinja_phase6.py
# Expected: 4/4 PASS (unchanged)
```

### Phase 7c: Re-run Phase 6.5 Extended Tests
**Goal**: Verify tool sequencing fixed
```bash
python jinja_tests/test_cline_realistic_code_edit.py
# Expected: PASS (was FAIL in Phase 6.5)

python jinja_tests/test_jinja_error_handling.py
# Expected: 4/4 PASS (was 3/4)

python jinja_tests/test_jinja_looping.py
# Expected: Complete <60 sec (was timeout)
```

### Phase 7d: Additional Validation
- [ ] Multi-turn workflows (read → analyze → write → execute)
- [ ] Error recovery (tool fails → model continues)
- [ ] No tool hallucination (only calls defined tools)

---

## Success Criteria

| Criteria | Phase 6.5 | Phase 7 Target |
|----------|-----------|----------------|
| **Phase 5 Tests (TC1-TC5)** | 5/5 PASS | 5/5 PASS ✓ |
| **Phase 6 Tests (TC6-TC9)** | 4/4 PASS | 4/4 PASS ✓ |
| **Realistic Workflow** | FAIL | PASS ✓ |
| **Error Handling** | 3/4 PASS | 4/4 PASS ✓ |
| **Looping Safety** | TIMEOUT | COMPLETE ✓ |
| **Tool Sequencing** | Broken | Fixed ✓ |

**Pass/Fail**: If all Phase 7 targets met → v2.0 PRODUCTION READY

---

## Files to Modify

### Create
- `chat_template_cline_optimized_v2.jinja` (new version)

### Update
- Deploy v2.0 to OVMS
- Re-run all tests

### Reference
- `Phase6-Test-Audit.md` — Audit findings
- `Phase6.5-Test-Results.md` — Failed test details
- `jinjas/Qwen3-Coder-30B-A3B-Instruct-int4-ov/chat_template.jinja` — Hack template (reference)

---

## Execution Steps (After `/clear`)

1. **Read Hack Template** (tool rendering section)
2. **Analyze v1.0 vs Hack** (identify key changes)
3. **Create v2.0 Template**:
   - Start with v1.0 (base)
   - Replace tool rendering (tojson from Hack)
   - Keep v1.0 guard clauses
   - Remove Vision/Video macros
4. **Deploy v2.0 to OVMS**
5. **Run Phase 5 Tests** (regression check)
6. **Run Phase 6 Tests** (regression check)
7. **Run Phase 6.5 Tests** (validation, should PASS)
8. **Analysis & Decision**:
   - All PASS → v2.0 approved, proceed to Phase 8 (docs)
   - Some FAIL → debug, iterate
   - Major FAIL → rollback to v1.0, reassess

---

## Phase Progression

```
Phase 6: ✅ COMPLETE (baseline tests: 9/9 PASS)
Phase 6.5: ✅ COMPLETE (audit: gaps identified)
Phase 7: ⏳ PENDING (refinement: fix tool sequencing)
  ├─ 7a: Template modification
  ├─ 7b: Regression testing
  ├─ 7c: Extended validation
  └─ 7d: Production sign-off
Phase 8: ⏹️ PENDING (documentation & justification)
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| v2.0 breaks Phase 5 | Low | High | Test immediately (7b) |
| Tool JSON malformed | Very Low | High | tojson handles it |
| Model still confused | Medium | Medium | Iterate prompting |
| Performance degrades | Low | Medium | Monitor OVMS metrics |

---

## Notes

- **Why switch now?**: Phase 6.5 audit proves v1.0 insufficient for real workflows
- **Why Hack template?**: Proven effective on Qwen 3.5 (similar model family), tojson is atomic/reliable
- **Why not go directly to Phase 8?**: Cannot ship without validation; Phase 7 ensures production-ready
- **Timeline**: 2-3 hours total (1h template work, 2h testing/iteration)

---

## Next: `/clear` and Start Phase 7

When ready: 
```
/clear "Phase 7: Template Refinement & Re-Testing"
```

Then execute steps in **Execution Steps** section above.
