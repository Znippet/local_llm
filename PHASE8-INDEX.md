# Phase 8 Research Index & Navigation Guide

## Quick Navigation

### For Orchestrator (Daily Decision-Making)
- **START HERE**: PHASE8-RESEARCH-SUMMARY.txt (10 min read)
- **Decision Tree**: Section 8, page 15 of Phase8-Jinja-Possibilities.md
- **Iteration Checklist**: Section 6, page 13

### For Implementation Team
- **Candidates 1-4**: Section 5.2, pages 9-13 of Phase8-Jinja-Possibilities.md
- **Success Criteria**: Section 6.2, page 14
- **Rollback Protocol**: Section 6.3, page 14

### For Architecture Review
- **Root Cause Analysis**: Section 4, pages 7-8 (Best-Practices)
- **Model Variant Comparison**: Section 3, pages 6-7
- **Template Pattern Analysis**: Sections 1-2, pages 4-6

---

## Key Artifacts & Locations

### Research Documents
- Phase8-Jinja-Possibilities.md — Main research (348 lines, 11KB)
- PHASE8-RESEARCH-SUMMARY.txt — Executive summary (246 lines, 8KB)

### Referenced Phase Docs (Dependencies)
- Phase1-Template-Collection.md — 7 template sources
- Phase7-Refinement-Results-FINAL.md — Root cause evidence
- Phase6.5-Test-Results.md — Tool sequencing gap analysis

---

## 12 Optimization Candidates At A Glance

| Rank | Candidate | ROI | Likelihood | Impact | Effort | Status |
|------|-----------|-----|-----------|--------|--------|--------|
| 1A | 35B Model Swap | 1300 | 65% | 40% | 2h | PRIORITY |
| 1B | Few-Shot Examples | 675 | 45% | 30% | 1h | HIGH |
| 1D | Hard Constraints | 437 | 50% | 35% | 3h | MEDIUM |
| 1C | Temperature Tune | 350 | 35% | 20% | 1h | MEDIUM |
| 2B | Role Framing | 375 | 25% | 15% | 0.5h | FALLBACK |
| 2C | Context Window | 267 | 40% | 20% | 2h | FALLBACK |
| 2A | Client-Side (Out) | 1068 | 95% | 45% | 4h | GUARANTEED |

---

## Success Criteria Summary

**All iterations must maintain:**
- Phase 5: 5/5 PASS (baseline file operations)
- Phase 6: 4/4 PASS (extended tools)

**Primary optimization target:**
- Phase 6.5: 0/3 PASS → Target 2-3/3 PASS (tool sequencing)

**"Win Condition"**: Any iteration improving Phase 6.5 from 0→2+ without regression

---

## Iteration Execution Template

**For each iteration (use this checklist):**

`
[ ] Day N: SELECT Candidate X
[ ] RESEARCH: Read relevant docs (15 min)
[ ] IMPLEMENT: Modify template/config (30-60 min)
[ ] DEPLOY: Push to OVMS (5 min)
[ ] TEST: Run Phase 5-6 regression (45 min)
[ ] TEST: Run Phase 6.5 extended (30 min)
[ ] ANALYZE: Document pass/fail (15 min)
[ ] DECIDE:
    - PASS: Apply cumulatively, proceed to next candidate
    - FAIL: Revert, try next candidate
    - REGRESSION: ROLLBACK to v2.0, escalate
`

---

## Critical Findings Summary

### Finding 1: Root Cause Identified
**The tool-sequencing problem is NOT a template issue.**

Evidence:
- v1.0 (30+ line Structured XML) and v2.0 (1 line tojson) = identical failures
- Phase 7: Enhanced prompting = 0% improvement
- Both fail on read→write→execute sequencing

Conclusion: **Model training data gap, not instruction clarity**

### Finding 2: Explicit Negative Instructions Work
Pattern from Issue #475:
- "Do NOT omit the initial <tool_call> tag ⭐"
- Reduces error rate 15-20% → 2-5%
- Already deployed in v1.0 & v2.0

Generalization: Negative instructions (what NOT to do) > Positive instructions (what to do)

### Finding 3: Template Pattern Choice Doesn't Matter
- Pattern A (Structured XML, 30+ lines)
- Pattern B (tojson, 1 line)
- **Performance: IDENTICAL**

Implication: Choose for maintainability, not correctness

### Finding 4: Model Scaling Likely Solution
- 30B: 70% tool-sequencing reliable (tested, fails)
- 35B: 17% more parameters (available, untested)
- 70B: 2.3x parameters (available, untested)

Hypothesis: Larger models trained on more complex tool examples

---

## Phase 8 Timeline Estimate

- **Iteration 1 (35B swap)**: 2-3 hours
- **Iteration 2 (Few-shot)**: 1-1.5 hours
- **Iteration 3 (Temperature)**: 1 hour
- **Iteration 4 (Hard constraints)**: 3-4 hours
- **Consolidation (v3.0)**: 2 hours

**Total**: ~9-11 hours spread over 5-7 working days

---

## References & Deep Dives

### Template Sources (Phase 1)
1. Unsloth Official (HF) — Industry standard
2. mostlygeek Gist — Claude Code optimized
3. nuzkito Gist — JSON-in-XML variant
4. Unsloth Discussion #10 — GGUF-proven
5. QwenLM Issue #475 — Native Qwen knowledge
6. Local OpenVINO Current — Over-engineered
7. Local OpenVINO Original — Legacy

### Design Patterns (Section 2)
- **Pattern A**: Structured XML (v1.0)
- **Pattern B**: JSON serialization/tojson (v2.0)
- **Pattern C**: JSON-in-XML hybrid (rejected)

### Best-Practices Patterns (Section 4)
1. ✓ Explicit negative instructions (+8-15%)
2. ✗ Tool sequencing constraints (0%)
3. 🔄 Few-shot examples (untested, theory sound)
4. 🔄 Role-based prompting (untested, theory sound)
5. 🔄 Temperature tuning (untested, medium likelihood)

---

## Known Limitations

**Out-of-scope for Phase 8 template research:**
- GGUF/llama.cpp specific optimizations
- Vision/multi-modal features (not needed)
- Custom Qwen training (requires GPU infrastructure)
- Prompt engineering for other LLMs (Qwen-specific)

**Known constraints:**
- Context >30k: Reliability degradation
- Q4 quantization: No special handling needed
- ChatML format: No negotiation (all Qwen models use it)

---

## Decision Tree (Quick Reference)

`
[START] v2.0 baseline passing? → YES
  ↓
[TRY] Candidate 1: 35B swap
  → PASS 2+/3: KEEP + next
  → FAIL: REVERT + skip to Candidate 6
  → REGRESSION: ROLLBACK
  ↓
[TRY] Candidate 2: Few-shot
  → PASS: KEEP
  → FAIL: REVERT
  ↓
[TRY] Candidate 3: Temperature
  → PASS: KEEP
  → FAIL: SKIP
  ↓
[TRY] Candidate 4: Hard constraints
  → PASS: KEEP
  → FAIL: SKIP
  ↓
[IF TIER 1 ALL FAIL] Candidate 6: Client-side
  → Available: Implement
  → Out-of-scope: Document workaround
  ↓
[CONSOLIDATE] v3.0 final
  → Merge successful changes
  → Full test suite (12 scenarios)
  → Phase 9 ready
`

---

## Contact & Escalation

If iteration fails:
1. Document exact failure in Phase8-Iteration-N-Results.md
2. Check rollback protocol (Section 6.3)
3. Proceed to next candidate per decision tree
4. If major regression: Escalate to orchestrator

---

## Research Quality Metrics

**Depth**:
- 7 template sources analyzed
- 5 design patterns evaluated
- 4 model variants researched
- 12 optimization candidates identified

**Evidence**:
- Phase 1-7 empirical results
- GitHub issue analysis (Issue #475)
- HuggingFace patterns (mostlygeek, Unsloth)
- Local model verification

**Actionability**:
- 12 candidates with success criteria
- Implementation steps documented
- Rollback protocol defined
- Clear decision tree

---

Last Updated: 2026-06-17
Status: RESEARCH COMPLETE, READY FOR ITERATION 1
