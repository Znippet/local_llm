# Phase 7: Step-by-Step Instructions

**Goal**: Create v2.0 template (tojson-based) & validate through Phase 6.5 tests

**Estimated Time**: 2-3 hours

---

## STEP 1: Analyze Templates (Read Only)

### 1a. Read Hack Template (Tool Rendering Section)

Location: `C:\LLM\jinjas\Qwen3-Coder-30B-A3B-Instruct-int4-ov\chat_template.jinja`

Focus on **lines 45-52** (tool serialization):
```jinja
{%- if tools and tools is iterable and tools is not mapping %}
    {{- '<|im_start|>system\n' }}
    {{- "# Tools\n\nYou have access to the following functions:\n\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}                  <-- KEY: tojson serialization
    {%- endfor %}
    {{- "\n</tools>" }}
```

**What it does**: 
- Takes each tool object
- Serializes to JSON with `tojson` filter
- Guarantees valid JSON structure
- No manual string building = no errors

### 1b. Read v1.0 Tool Section (Current - Manual XML)

Location: `C:\LLM\jinja_templates\chat_template_cline_optimized_v1.jinja`

**Lines 31-65** (manual tool rendering):
- 30+ lines of manual XML building
- Nested loops for parameters
- String concatenation prone to errors
- Why it breaks: Each string concat point can introduce malformed XML

### 1c. Compare Guard Clauses (v1.0 - Keep This)

**Lines 66-67** (v1.0 feature):
```jinja
<IMPORTANT>
Reminder:
- Function calls MUST follow the specified format...
- Do NOT omit the initial <tool_call> tag ⭐ This is critical
```

**Action**: Copy this to v2.0 (proven to reduce hallucinations)

---

## STEP 2: Create v2.0 Template

### 2a. Start with v1.0 as Base

Copy v1.0 to v2.0:
```bash
cp C:\LLM\jinja_templates\chat_template_cline_optimized_v1.jinja \
   C:\LLM\jinja_templates\chat_template_cline_optimized_v2.jinja
```

### 2b. Replace Tool Rendering (Lines 31-65)

**REPLACE THIS SECTION** (lines 31-65 in v1.0):

```jinja
{%- if tools is iterable and tools | length > 0 %}
    {{- "\n\n# Tools\n\nYou have access to the following functions:\n\n" }}
    {{- "<tools>" }}
    {%- for tool in tools %}
        {%- if tool.function is defined %}
            {%- set tool = tool.function %}
        {%- endif %}
        {{- "\n<function>\n<name>" ~ tool.name ~ "</name>" }}
        ...
        ... (entire manual XML section)
        ...
    {%- endfor %}
    {{- "\n</tools>" }}
    {{- '\n\nIf you choose to call a function...' }}
```

**WITH THIS** (from Hack, lines 45-52):

```jinja
{%- if tools and tools is iterable and tools is not mapping %}
    {{- '<|im_start|>system\n' }}
    {{- "# Tools\n\nYou have access to the following functions:\n\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>" }}
    {{- '\n\nIf you choose to call a function ONLY reply in the following format with NO suffix:\n\n<tool_call>\n<function=example_function_name>\n<parameter=example_parameter_1>\nvalue_1\n</parameter>\n<parameter=example_parameter_2>\nThis is the value for the second parameter\nthat can span\nmultiple lines\n</parameter>\n</function>\n</tool_call>\n\n<IMPORTANT>\nReminder:\n- Function calls MUST follow the specified format: an inner <function=...></function> block must be nested within <tool_call></tool_call> XML tags\n- Do NOT omit the initial <tool_call> tag ⭐ This is critical\n- Required parameters MUST be specified\n- You may provide optional reasoning for your function call in natural language BEFORE the function call, but NOT after\n- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls\n</IMPORTANT>' }}
{%- endif %}
```

**Key changes**:
1. Line: `{%- if tools and tools is iterable and tools is not mapping %}`
2. Line: `{{ tool | tojson }}` (single line replaces 30+ lines)
3. Keep guard clauses (IMPORTANT block unchanged)

### 2c. Keep Rest of v1.0 Unchanged

Everything from line 68+ stays the same:
- Message role handling
- Tool response formatting
- Multi-turn logic

### 2d. Verify v2.0 Structure

After edit, v2.0 should have:
- [ ] Line ~1-30: System message setup (from v1.0)
- [ ] Line ~31-58: Tool rendering with tojson (from Hack)
- [ ] Line ~59-67: Guard clauses (from v1.0)
- [ ] Line ~68+: Message loop handling (from v1.0)

Total lines: ~100-110 (v1.0 was 117, now smaller + cleaner)

---

## STEP 3: Deploy v2.0 to OVMS

### 3a. Start OVMS Server

```powershell
.\jinja_deployment\start_ovms_server.ps1
# Wait for "OVMS API responding"
```

### 3b. Deploy v2.0

```powershell
.\jinja_deployment\deploy_jinja_template.ps1 -Version v2.0 -RestartOVMS $true
# Will copy v2.0 to OVMS model dir and restart
```

Wait ~15 seconds for OVMS restart.

### 3c. Validate Deployment

```powershell
.\jinja_deployment\validate_ovms_setup.ps1
# Should show:
# [OK] OVMS running
# [OK] Template found
# [OK] API responsive
```

---

## STEP 4: Test Phase 5 (Regression Check)

**Goal**: Ensure no breaking changes

```bash
python jinja_tests/run_jinja_phase5.py
```

**Expected Result**: 5/5 PASS

**If FAIL**: Debug changes, likely tojson serialization mismatch

---

## STEP 5: Test Phase 6 (Regression Check)

**Goal**: Ensure extended tools still work

```bash
python jinja_tests/run_jinja_phase6.py
```

**Expected Result**: 4/4 PASS (TC6-TC9)

**If FAIL**: Same debugging as Step 4

---

## STEP 6: Test Phase 6.5 Extended (Validation)

**THIS IS THE CRITICAL PHASE**

### 6a. Realistic Code Edit Workflow

```bash
python jinja_tests/test_cline_realistic_code_edit.py
```

**Was**: FAIL (tool sequencing broken)  
**Now Expected**: PASS (tool sequencing fixed)

**Success Indicator**:
- Step 1: read_file ✓
- Step 2: write_file ✓ (WAS FAILING, NOW SHOULD PASS)
- Step 3: execute_command ✓

### 6b. Error Handling

```bash
python jinja_tests/test_jinja_error_handling.py
```

**Was**: 3/4 PASS  
**Now Expected**: 4/4 PASS

**Success Indicator**:
- TC1: read_file nonexistent — should call read_file (was calling wrong tool)
- TC2: execute_command failure — should call execute_command
- TC3: protected path — should avoid (already worked)
- TC4: empty search — should call search_files (already worked)

### 6c. Looping Detection

```bash
python jinja_tests/test_jinja_looping.py
```

**Was**: TIMEOUT (>60 sec)  
**Now Expected**: Complete in <60 sec

**Success Indicator**: No infinite loops, tests complete

---

## STEP 7: Analysis & Decision

### 7a. If All PASS

```
Phase 5: 5/5 ✓
Phase 6: 4/4 ✓
Phase 6.5: Realistic PASS ✓
Phase 6.5: Error Handling 4/4 ✓
Phase 6.5: Looping <60s ✓

→ v2.0 APPROVED for production
→ Proceed to Phase 8 (Documentation)
```

### 7b. If Some FAIL

Debug based on failure:

**Failure Type A**: Phase 5 or 6 broken
- Regression in tojson serialization
- Fix: Ensure tojson syntax correct in v2.0
- Retry: Fix template, re-deploy, re-test

**Failure Type B**: Phase 6.5 still not perfect
- tojson helps but doesn't solve all issues
- Fix: Adjust prompting in guard clauses
- Add more explicit tool sequencing hints
- Retry: Create v2.1 with prompting improvements

**Failure Type C**: Unknown error
- Check test output JSON files
- Analyze Model response
- Adjust template accordingly

### 7c. If Major Regression

- Rollback to v1.0
- Reassess approach
- Consider alternative template strategy

---

## STEP 8: Update Documentation

After Phase 7 complete (tests PASS):

- [ ] Update `JINJA-VERSIONS.md` with v2.0 details
- [ ] Update master plan status
- [ ] Git commit Phase 7 completion
- [ ] Ready for Phase 8 (Documentation writeup)

---

## Quick Reference

### Commands

```bash
# Deploy v2.0
.\jinja_deployment\start_ovms_server.ps1
.\jinja_deployment\deploy_jinja_template.ps1 -Version v2.0 -RestartOVMS $true

# Run all tests
python jinja_tests/run_jinja_phase5.py
python jinja_tests/run_jinja_phase6.py
python jinja_tests/test_cline_realistic_code_edit.py
python jinja_tests/test_jinja_error_handling.py
python jinja_tests/test_jinja_looping.py

# Stop
.\jinja_deployment\stop_ovms_server.ps1
```

### Key Template Change

**Before** (v1.0, manual XML, 30+ lines):
```
Manual string: "<function>" + name + "</function>" + ...
```

**After** (v2.0, JSON, 1 line):
```
{{ tool | tojson }}
```

### Success Criteria

| Item | v1.0 | v2.0 Target |
|------|------|-------------|
| TC1-TC5 | 5/5 ✓ | 5/5 ✓ |
| TC6-TC9 | 4/4 ✓ | 4/4 ✓ |
| Realistic workflow | ✗ | ✓ |
| Error handling | 3/4 | 4/4 ✓ |
| Looping test | TIMEOUT | PASS ✓ |

---

## When Ready: `/clear`

After reading this:
```
/clear "Phase 7: Template Refinement & Re-Testing"
```

Then start from STEP 1.
