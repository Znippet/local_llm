# Qwen3-Coder-30B-A3B → Cline Jinja Template Optimization Plan

**Ziel**: Erstelle optimiertes `chat_template.jinja` für Cline mit JSON-in-XML Tool-Calls, parserfreundlich, OVMS-kompatibel

**Start**: 2026-06-16  
**Status**: In Progress

---

## Phasen-Übersicht

### ✅ Phase 1: Template Collection (COMPLETED)
**Deliverables**:
- ✅ 7 templates collected (5 online, 2 local)
- ✅ All sources documented with URLs
- ✅ Structural analysis: all use XML ChatML format
- ✅ Success/failure patterns mapped
- ✅ Risiko-Bewertung pro Template

**Output**: `Phase1-Template-Collection.md`

**Key Findings**:
- Unsloth Official = universally supported baseline
- mostlygeek Gist = Claude Code optimized (applicable to Cline)
- Issue #475 constraints = reliability boost (+8-15%)
- All sources converge on `<tool_call>` wrapper with `<parameter=>` syntax

---

### ✅ Phase 2: Structural Analysis (COMPLETED)
**Aufgabe**: Side-by-side comparison der 7 Templates

**Deliverables**:
- [x] Detailed diff table: parameter handling, tool rendering, instruction format
- [x] Extract core `<tool_call>` formatting per source
- [x] Identify which parts are client-specific vs. universally applicable
- [x] Extract macro logic (render_extra_keys, content rendering, etc.)
- [x] Document vision/reasoning/thinking tag handling

**Method**:
1. Read all 7 template files in full
2. Create side-by-side comparison table
3. Highlight differences in:
   - Tool schema rendering (JSON vs XML structure)
   - Parameter serialization (tojson safe vs string)
   - Instruction formatting (explicit constraints, reasoning position)
   - Message role handling (system, user, assistant, tool)

**Output**: `Phase2-Structural-Comparison.md`

---

### ⏳ Phase 3: Cline-Optimized Template Design (PENDING)
**Aufgabe**: Synthesize optimal template for Cline

**Design Criteria**:
- Minimalist (no unnecessary vision/reasoning features)
- JSON-in-XML tool calls (as hypothesis predicts)
- OpenAI-compatible parser-friendly format
- Multi-step tool-use capable
- OVMS/OpenVINO compatible
- Issue #475 instruction constraints embedded

**Approach**:
1. Start with Unsloth Official as base
2. Apply mostlygeek instruction clarity (Claude Code → Cline)
3. Add Issue #475 explicit constraints ("do NOT omit", reasoning position)
4. Optionally include nutzito JSON-in-XML tool-call format
5. Remove: vision tokens, video handling, complex thinking logic
6. Keep: message role handling, tool-response wrapper, multi-step support

**Decision Gate**:
- JSON-in-XML or pure XML? (Test both if time permits)

**Output**: `chat_template_cline_optimized.jinja`

---

### ⏳ Phase 4: Test Harness & Validation (PENDING)
**Aufgabe**: Create reproducible local test

**Test Cases**:
1. **Single tool call**: Model calls one tool exactly once with correct JSON args
2. **Structured args**: Arguments parse as valid JSON (no malformed strings)
3. **Tool result follow-up**: Model continues coherently after tool response
4. **No-tool answer**: Without tool need, model doesn't generate fake tool calls
5. **Multi-step tool use**: Model chains 2+ tool calls with proper intermediate handling

**Harness Components**:
- [ ] Python script: HTTP POST to local OpenAI-compatible endpoint
- [ ] Test payload: System prompt + user message + tool definition
- [ ] Response parser: Extract `<tool_call>` blocks, validate JSON
- [ ] Bash script: curl version for CI/automation
- [ ] Metrics: success rate, parsing time, hallucination detection

**Output**: 
- `test_harness.py`
- `test_harness.sh`
- `test_results.json`

---

### ⏳ Phase 5: Documentation & Justification (PENDING)
**Aufgabe**: Write comprehensive reasoning document

**Content**:
- [ ] Why JSON-in-XML (or pure XML) for Cline specifically
- [ ] Why Unsloth base + mostlygeek/Issue #475 enhancements
- [ ] Comparison matrix: why chosen template beats alternatives
- [ ] Client compatibility analysis (Cline vs RooCode vs Continue)
- [ ] Known limitations and workarounds
- [ ] Integration instructions for OVMS

**Output**: `Phase5-Justification.md`

---

## Checklist (Master)

- [x] **Phase 1**: Collect all template sources
- [x] **Phase 2**: Structural comparison (7 templates side-by-side)
- [ ] **Phase 3**: Synthesize Cline-optimized template
- [ ] **Phase 4**: Build test harness + validate
- [ ] **Phase 5**: Document reasoning + integration guide

---

## Key Hypotheses to Validate

1. ✓ Confirmed: "Cline profitiert von strukturierten Tool-Calls" (Unsloth, mostlygeek beide work)
2. ? Pending: "JSON-in-XML ist besser als reines XML für Cline-Parser"
3. ? Pending: "Minimalistisches Template > komplexes (vision/thinking)"
4. ✓ Confirmed: "Instruction-Clarity (Issue #475) = +8-15% Zuverlässigkeit"

---

## Decision Log

| Phase | Decision | Rationale | Date |
|-------|----------|-----------|------|
| 1 | Start with Unsloth Official | Universally tested, maintained | 2026-06-16 |
| 1 | Include Issue #475 constraints | Reliability boost, non-invasive | 2026-06-16 |
| - | Decide JSON-in-XML vs XML | Test in Phase 4 | Pending |
| - | Vision tokens: remove or keep? | Decide in Phase 3 | Pending |

---

## Resource References

### Online Sources
- Unsloth Official: https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct/blob/main/chat_template.jinja
- mostlygeek Gist: https://gist.github.com/mostlygeek/6fe263bad8026dca73cb6f5470dfdb0d
- nutzito Gist: https://gist.github.com/nutzito/dc4662f003896e2d8080fbaf1838f557
- Unsloth Discussion: https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF/discussions/10
- QwenLM Issue #475: https://github.com/QwenLM/Qwen3-Coder/issues/475

### Local Paths
- Phase 1 findings: `./Phase1-Template-Collection.md`
- Qwen model (OVMS): `./models/OpenVINO/Qwen3-Coder-30B-A3B-Instruct-int4-ov/`
- Template location: `./models/OpenVINO/.../chat_template.jinja`

---

## Time Estimate

| Phase | Effort | Est. Duration |
|-------|--------|---------------|
| 1 | Data collection | ✅ Complete |
| 2 | Analysis | ~30-45 min |
| 3 | Template synthesis | ~45-60 min |
| 4 | Test harness | ~30-45 min |
| 5 | Documentation | ~20-30 min |
| **Total** | | **~3-4 hours** |

---

## Notes

- Context clearing between phases recommended (save outputs, use plan as reference)
- Phase 4 requires local model endpoint (OpenVINO OVMS or similar)
- Phase 5 can run in parallel with Phase 4 test execution
