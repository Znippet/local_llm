# Phase 7: Refinement Execution Plan

**Date**: 2026-06-17  
**Status**: IN PROGRESS  
**Goal**: Address Phase 6.5 audit gaps, create v2.0 template, re-validate

---

## Problems to Fix

From Phase 6.5 Audit:
1. **Tool Sequencing Fails** — read→write sequence breaks
2. **Error Handling Mixed** — inconsistent error responses
3. **Looping Untested** — timeout issues
4. **Edge Cases Missing** — Unicode, long paths, special chars

---

## Phase 7 Workflow

### Step 1: Improved Prompting for v2.0
**Current (v1.0)**:
- Basic format description
- "Do NOT omit <tool_call> tag" reminder
- Generic instruction

**Needed (v2.0)**:
- Explicit tool sequencing examples (read → write → execute)
- When each tool should be called (file ops first, then execute)
- Error handling strategy (how to recover)
- Edge case guidance (unicode handling, path length limits)

### Step 2: Create v2.0 Template
- Copy v1.0 as base
- Enhance system message to clarify tool usage order
- Add tool-specific guidance in <IMPORTANT> section
- Add edge case handling notes

### Step 3: Test v2.0 Systematically
- **3a**: Run Phase 6.5 tests again (realistic code edit, error handling, looping)
- **3b**: Add edge case tests (unicode, long paths, special chars)
- **3c**: Verify no regressions in TC1-TC9 (Phase 5/6 baseline)

### Step 4: Analysis & Documentation
- Compare v1.0 vs v2.0 results
- Document what improved / what regressed
- Create `Phase7-Refinement-Results.md` with findings

### Step 5: Decision
- If v2.0 passes Phase 6.5: Approve for Phase 8
- If v2.0 fails: Iterate or stay with v1.0 + documented limitations

---

## Deliverables

- [ ] `chat_template_cline_optimized_v2.jinja` — Refined template
- [ ] Phase 6.5 test results (v2.0)
- [ ] Edge case test results
- [ ] `Phase7-Refinement-Results.md` — Summary & comparison
- [ ] Decision: Which template for Phase 8?

---

## Success Criteria

**v2.0 Passes Phase 7 if:**
- ✓ Realistic code edit workflow: PASS (read→write sequence works)
- ✓ Error handling: 4/4 PASS (consistent behavior)
- ✓ Looping: Completes in <10 sec per scenario
- ✓ TC1-TC9: No regressions (still 9/9 PASS)
- ✓ Edge cases: 80%+ PASS

**Minimum to proceed to Phase 8:**
- Realistic workflow: PASS (non-negotiable)
- No regressions in TC1-TC9

---

## Timeline

- Step 1-2: Create v2.0 (15 min)
- Step 3a-b: Run all tests (30-45 min)
- Step 4: Analysis (10-15 min)
- Step 5: Decision (5 min)

**Total**: ~60-75 minutes

---

Next: Create v2.0 template with improved prompting
