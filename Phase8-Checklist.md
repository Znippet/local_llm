# Phase 8: Continuous Enhancement Loop — Iteration Checklist

**Start Date**: 2026-06-17  
**Phase 8 Status**: ACTIVE (Phase 8a COMPLETE, Phase 8b STARTING)

---

## Iteration Tracking

### **Iteration 1: Model Swap (30B → 35B)** [❌ COMPLETED - NOT COMPATIBLE]

- [x] Pre-flight: Research 35B availability + compatibility
- [x] Deploy Qwen3-Coder-35B-A3B to OVMS (FAILED: Qwen3.6-35B is multi-modal, incompatible)
- [x] Restore 30B model (SUCCESS: no regressions)
- [x] Document results → `Phase8-Iteration-1-Report.md`
- [x] Decision: REVERT + pivot to Candidate 2 (Few-Shot Examples)

**Result**: Qwen3-Coder-35B doesn't exist; only Qwen3.6-35B (multi-modal). Architecture mismatch prevents deployment.  
**Decision**: Skip model-swapping strategy, proceed to template-only optimizations (Tier 1B-D)  
**ROI**: N/A (candidate failed)  
**Lessons**: Model family variants critical; can't assume drop-in compatibility

---

### **Iteration 2: Few-Shot Examples** [✅ COMPLETED - KEEP v2.1]

- [x] Pre-flight: Design few-shot examples for tool sequencing
- [x] Implement in template system prompt (3 examples: Read→Write, Search→Read, List→Execute)
- [x] Test Phase 5-6 regression (5/5 + 4/4 PASS - no regression)
- [x] Test Phase 6.5 tool-sequencing (0/3 baseline → **2/3 PASS**)
- [x] Document results → `Phase8-Iteration-2-Report.md`
- [x] Decision: **KEEP v2.1** (66.7% sequencing success)

**Result**: Few-shot examples improve multi-step tool chaining. Measurable +66.7% on Phase 6.5.  
**ROI**: 675 (confirmed effective)  
**Status**: Ready for Iteration 3 (cumulative improvements)

---

### **Iteration 3: Temperature Tuning** [⏳ IN PROGRESS]

- [ ] Pre-flight: Determine optimal temperature (0.3 vs 0.7)
- [ ] Create v2.2 template with temperature meta
- [ ] Adjust OVMS config (sampling params)
- [ ] Test Phase 5-6 regression (expect 5/5 + 4/4)
- [ ] Test Phase 6.5 (target: compound with v2.1, ≥2/3 maintain or improve)
- [ ] Document results → `Phase8-Iteration-3-Report.md`

**Dependency**: Iter 2 PASS ✓  
**ROI**: 350  
**Hypothesis**: Lower temperature = more deterministic tool-call structure

---

### **Iteration 4: Hard Constraints** [⏳ PENDING Iter 1-3 PASS]

- [ ] Pre-flight: Design constraint encoding logic
- [ ] Implement in template
- [ ] Test Phase 5-6 + Phase 6.5
- [ ] Document results → `Phase8-Iteration-4-Report.md`

**Dependency**: Iter 1 PASS  
**ROI**: 437 (high complexity)

---

## Fallback Options (If Tier 1 Blocked)

- [ ] **Candidate 6**: Client-Side Orchestration (ROI 1068, out-of-scope but guaranteed success)
- [ ] **Candidate 5**: Role-Based Framing (ROI 375)
- [ ] **Candidate 2C**: Context Window Optimization (ROI 267)

---

## Success Criteria (Per Iteration)

| Phase | Target | Must Maintain |
|-------|--------|---------------|
| Phase 5 | 5/5 PASS | Yes (regression prevention) |
| Phase 6 | 4/4 PASS | Yes (regression prevention) |
| Phase 6.5 | 0→2-3/3 PASS | Primary goal |

---

## Template Versioning

- **v1.0**: Original Unsloth + Issue #475 (Phase 5-6: 9/9 PASS, Phase 6.5: 0/3 FAIL)
- **v2.0**: Current (tojson + enhanced prompting, Phase 5-6: 9/9 PASS, Phase 6.5: 0/3 FAIL)
- **v3.0**: Target (Iter 1-4 cumulative improvements, Phase 6.5: 2-3/3 PASS)

---

## Model Versions

- **30B-A3B**: Current (Phase 7 tested, limitations identified)
- **35B-A3B**: Iteration 1 candidate
- **70B-A3B**: Future if 35B insufficient

---

## Next Immediate Action

→ **Start Phase 8b Iteration 1: Model Swap (30B → 35B)**

Orchestrator: Dispatch Programmer Agent to:
1. Locate & deploy Qwen3-Coder-35B-A3B-Instruct from local storage
2. Update OVMS model path
3. Run full test suite (Phase 5 + 6 + 6.5)
4. Document results

**Estimated Duration**: 2-3 hours  
**Status**: READY TO START
