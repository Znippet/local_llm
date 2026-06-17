# Qwen3-Coder-30B-A3B → Cline Jinja Template Optimization Plan

**Ziel**: Erstelle optimiertes `chat_template.jinja` für Cline mit JSON-in-XML Tool-Calls, parserfreundlich, OVMS-kompatibel

**Start**: 2026-06-16  
**Phase 5 Complete**: 2026-06-17  
**Phase 6 Complete**: 2026-06-17  
**Phase 6.5 Complete**: 2026-06-17 (Audit)  
**Phase 7 Complete**: 2026-06-17 (Refinement & tojson optimization)  
**Status**: Phase 7 REFINEMENT COMPLETE → Phase 8 CONTINUOUS ENHANCEMENT PENDING

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

### ✅ Phase 3: Cline-Optimized Template Design (COMPLETED)
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

### ✅ Phase 4: Test Strategy Design (COMPLETED)
**Aufgabe**: Create comprehensive test plan for direct Cline CLI validation

**Deliverables**:
- [x] 5 Test Cases (TC1-TC5) fully specified
- [x] Direct Cline CLI approach (`cline --json --auto-approve false`)
- [x] OVMS health-check blocking gate
- [x] Response parser validation logic
- [x] Edge-case handling (Q4, Jinja, XML)
- [x] Execution plan phases (4a Setup, 4b Execution, 4c Edge-Cases)
- [x] Failure mode recovery table

**Output**: `Phase4-Test-Strategy.md`

---

### ✅ Phase 5: Test Execution & Template Refinement (COMPLETED)
**Aufgabe**: Execute Phase 4 tests, analyze failures, refine template

**Execution (Phase 4a/4b/4c)**:
1. **Phase 4a**: Template deploy, OVMS check, Cline verify, test env setup
2. **Phase 4b**: Run TC1-TC5 with logging, capture responses
3. **Phase 4c**: Run edge-case variants (Q4 stress, unicode, long params)

**Analysis & Refinement Loop**:
1. Parse validation results from Phase 4b/4c
2. Identify root causes (Q4 artifacts, Jinja issues, etc.)
3. Adjust `chat_template_cline_optimized.jinja`
4. Redeploy to OVMS
5. Re-run failed test cases
6. Compare before/after metrics

**Deliverables**:
- [x] Test execution logs: `test_output_tc#.json` (5 files)
- [x] Validation results: `Phase5-Test-Results.json`
- [x] Summary report: `Phase5-Test-Results-FINAL.md`
- [x] Template validated: `chat_template_cline_optimized.jinja` (v1 validated, no v2 needed)

**Output**: Phase 5 COMPLETE — 5/5 tests PASS (100%)

---

### ✅ Phase 6: Refinement — Cleanup, Test Extension (COMPLETED)
**Aufgabe**: Reorganize & extend tests, prepare for documentation

**Deliverables**:
- [x] Verzeichnis-Struktur (jinja_templates/, jinja_tests/, jinja_deployment/)
- [x] Tests erweitert: TC6-TC9 (execute_command, search_files, web_search, list_directory_tree)
- [x] `jinja_templates/JINJA-VERSIONS.md` — Template versioning
- [x] `jinja_tests/README-JINJA-TESTS.md` — Test documentation
- [x] `jinja_deployment/deploy_jinja_template.ps1` — Template deployment
- [x] `jinja_deployment/start_ovms_server.ps1` — Server start with PID-tracking
- [x] `jinja_deployment/stop_ovms_server.ps1` — Server stop with PID cleanup
- [x] `jinja_deployment/SERVER-CONTROL.md` — Server management guide
- [x] `README.md` erweitert — Complete Jinja-template documentation
- [x] All TC1-TC9 PASS ✅ (5/5 Phase 5 + 4/4 Phase 6 = 9/9 PASS)

**Output**: Phase 6 complete → Ready for Phase 7 Documentation

---

### ✅ Phase 7: Template Refinement & Re-Testing (COMPLETE)
**Aufgabe**: Improve template robustness, implement tojson-based tool rendering, validate edge-cases

**Key Improvements**:
- ✅ Replaced manual XML (30 lines) with tojson (1 line)
- ✅ Enhanced IMPORTANT section with explicit tool sequencing rules
- ✅ Fixed deploy script parameter bug ([switch] → [bool])
- ✅ Standardized template naming convention

**Test Results**:
- Phase 5: 5/5 PASS (v2.0, no regressions)
- Phase 6: 4/4 PASS (v2.0, no regressions)
- Phase 6.5 Realistic: FAIL (tool sequencing limitation persists)
- Phase 6.5 Error Handling: 3/4 PASS
- Phase 6.5 Looping: Not completed (infrastructure issues)

**Critical Finding**: Tool-sequencing problem is NOT template-related but likely **model capability limitation** (Qwen3-Coder-30B). Both v1.0 and v2.0 fail identical sequencing tests equally.

**Deliverables**:
- [x] `chat_template_cline_optimized_v2.0.jinja` (tojson + enhanced prompting)
- [x] `Phase7-Refinement-Results-FINAL.md` (comprehensive analysis)
- [x] Deploy script fixes

**Output**: v2.0 ready for Phase 8 with documented limitations (single-tool operations reliable, multi-step sequences unreliable)

---

### ⏳ Phase 8: Continuous Template Enhancement — Multi-Agent Orchestration Loop
**Ziel**: Kontinuierliche Optimierung des Jinja-Templates durch strukturiertes Multi-Agent-System mit einem Orchestrator & langlebigem Researcher

**Architektur**:
```
Orchestrator (main thread, persistent)
    │
    ├─ 1. LONG-RUNNING Researcher (SendMessage, persistent agent)
    │      Läuft über die gesamte Phase 8
    │      Kann jederzeit neue Analyseanfragen erhalten
    │      Hält Kontext über alle Iterationen
    │      Output: Iterative Updates zu `Phase8-Jinja-Possibilities.md`
    │
    └─ 2. Sequential Loop (Orchestrator koordiniert):
         └─ For each checklist item:
              ├─ Orchestrator fragt Researcher: "Checke ob diese Änderung X mit Y compatible ist"
              ├─ Researcher antwortet mit Analyse/Tipps
              │
              ├─ New Subagent: Programmer (Fresh context, ephemeral)
              │    Implementiert Jinja-Änderung
              │    Führt TC1-TC9 aus
              │    Dokumentiert Fort-/Rückschritte
              │    Output: `Phase8-Iteration-N-Report.md`
              │
              └─ Orchestrator:
                   Liest Programmer-Report
                   Fragt Researcher: "Warum hat Iteration N so performt? Welche Patterns sieht du?"
                   Researcher gibt Pattern-Analyse zurück
                   Orchestrator schreibt `Phase8-Lessons-Learned-N.md`
                   Passt Checkliste an für Iteration N+1
```

**Workflow** (Sequenziell, Researcher warm halten):

**Phase 8a: Research Initialization** (Researcher Agent startet, bleibt warm)
1. Orchestrator: `Agent(type: explore, prompt: "Initial Jinja research...")`
   - Researcher erhält Task:
     - Analysiere alle 7 Template-Variationen (Phase 1)
     - Qwen 30B A3B vs. 35B vs. weitere Varianten
     - Online Best-Practices (Hugging Face, GitHub Issues, LLM Communities)
     - Performance Patterns (context, latency, quality)
   - Output: `Phase8-Jinja-Possibilities.md` + Priorisierte Checkliste (Likelihood/Impact Matrix)
   - **Agent-ID merken**: Für SendMessage-Loop

2. Orchestrator: Speichert Checkliste in `Phase8-Checklist.md`

**Phase 8b: Iterative Enhancement** (Sequential Loop, Researcher via SendMessage warm halten)
```
for each checklist_item in Phase8-Checklist.md:
  
  1. Orchestrator: SendMessage(to: researcher_id)
     "Ich starte Iteration N mit Änderung X.
      Checkliste-Context: (previous iterations summary)
      Tipps bevor ich den Programmer starte?"
  
  2. Researcher: antwortet via SendMessage (hält Kontext)
     - Pre-flight Checks
     - Compatibility Warnings
     - Suggested Test Focus
     - Speichert Update zu Phase8-Jinja-Possibilities.md
  
  3. Orchestrator: liest Researcher-Response
     → startet Fresh Programmer Agent
     Input: 
       - Current template
       - Checklist item N
       - Researcher Pre-Flight Tips
       - Phase8-Lessons-Learned-[1..N-1].md (kumulative Learnings)
  
  4. Programmer Agent: (ephemeral, fresh context)
     - Implementiert Jinja-Änderung
     - Führt TC1-TC9 aus
     - Schreibt Phase8-Iteration-N-Report.md
     - Terminiert (Kontext wird freigegeben)
  
  5. Orchestrator: liest Iteration-N-Report
     → SendMessage(to: researcher_id)
     "Iteration N Complete. Results:
      (metrics, pass/fail, diagnostics)
      Patterns? Prognose für N+1?"
  
  6. Researcher: antwortet via SendMessage (warmer Kontext!)
     - Pattern Recognition über alle bisherigen Iterationen
     - Root-Cause Analysis (warum +/- Ergebnisse)
     - Prediction für nächste Iteration
     - Speichert Update zu Phase8-Jinja-Possibilities.md
  
  7. Orchestrator: schreibt Phase8-Lessons-Learned-N.md
     (basierend auf Researcher-Pattern-Analyse)
     - Extrahiert ✅ Was funktioniert
     - Dokumentiert ❌ Was regressed
     - Passt Checkliste für N+1 an
```

**Phase 8c: Consolidation**
- Finaler SendMessage to Researcher:
  "Alle Iterationen Complete. Synthesize deine Learnings:
   - Generelle Patterns für Qwen3-Coder Jinja-Templates?
   - Was hätte anders gelaufen, wenn du am Start mehr gewusst hättest?
   - Recommendations für zukünftige Optimierungen?"
- Researcher: Schreibt `Phase8-Researcher-Summary.md`
- Orchestrator: Aggregiert zu `Phase8-Enhancement-Summary.md`
- Final template: `chat_template_cline_optimized-vN.jinja` (validated)
- Decision table: Which changes stuck? Which regressed? Why?

**Design Principles**:
1. **Small Orchestrator Context**: Only reads/writes small MD files, no code review, no implementation
2. **Fresh Programmer Agents**: Each gets full capacity for focus, no accumulated context bloat
3. **Explicit Handoff**: Each iteration → one MD summary that guides the next
4. **Incremental Validation**: No "phase complete" until metrics plateau or regressions exceed budget
5. **Reversibility**: All iterations tracked; easy to revert to v1 if needed

**Deliverables**:
- [ ] `Phase8-Jinja-Possibilities.md` — Research findings + checklist
- [ ] `Phase8-Iteration-[1..N]-Report.md` — Each programmer's work
- [ ] `Phase8-Lessons-Learned-[1..N].md` — Orchestrator analysis per iteration
- [ ] `Phase8-Enhancement-Summary.md` — Final consolidated report
- [ ] `chat_template_cline_optimized-vN.jinja` — Final validated template
- [ ] `Phase8-Decision-Matrix.md` — Which changes stuck, rationale

**Success Criteria**:
- At least 1 measurable improvement (e.g., +5% TC pass rate, reduced artifact count, latency -10ms)
- Or: Confirm v1 is optimal (no improvements found after N iterations)
- Zero regressions from v1 baseline in final template

**Output**: Phase 8 complete → Production-ready, multi-model validated template with full audit trail

---

## Checklist (Master)

- [x] **Phase 1**: Collect all template sources
- [x] **Phase 2**: Structural comparison (7 templates side-by-side)
- [x] **Phase 3**: Synthesize Cline-optimized template
- [x] **Phase 4**: Test strategy design (direct Cline CLI approach)
- [x] **Phase 5**: Test execution & template refinement (5/5 PASS)
- [x] **Phase 6**: Refinement — Cleanup, Test Extension (9/9 PASS)
- [x] **Phase 6.5**: Audit & Gap Analysis (COMPLETE)
- [x] **Phase 7**: Template Refinement & Re-Testing (COMPLETE — tojson + prompting, model limitation identified)
- [ ] **Phase 8**: Continuous Enhancement — Multi-Agent Orchestration Loop (READY TO START)

---

## Key Hypotheses to Validate

1. ✓ Confirmed: "Cline profitiert von strukturierten Tool-Calls" (Unsloth, mostlygeek beide work)
2. ✓ Confirmed: "OpenAI Format ist besser als reines XML" (OVMS konvertiert zu OpenAI, Model arbeitet damit besser)
3. ✓ Confirmed: "Minimalistisches Template > komplexes (vision/thinking)" (Template arbeitet, keine Bloat nötig)
4. ✓ Confirmed: "Instruction-Clarity (Issue #475) = +8-15% Zuverlässigkeit" (Tool-Definition in Prompt essentiell)

---

## Decision Log

| Phase | Decision | Rationale | Date |
|-------|----------|-----------|------|
| 1 | Start with Unsloth Official | Universally tested, maintained | 2026-06-16 |
| 1 | Include Issue #475 constraints | Reliability boost, non-invasive | 2026-06-16 |
| 3 | Base = Unsloth Official | Guard clauses, widely tested, clean | 2026-06-16 |
| 3 | Add Issue #475 enhancement | "Do NOT omit <tool_call>" critical fix | 2026-06-16 |
| 3 | Pure XML (not JSON-in-XML) | Simpler parser, no dual parsing overhead | 2026-06-16 |
| 3 | Keep render_extra_keys macro | Flexible, type-aware, proven | 2026-06-16 |
| 3 | Simple message handling | No multi-step state tracking (client-side) | 2026-06-16 |
| - | JSON-in-XML variant testing | Test in Phase 4 if time permits | Pending |
| - | Guard clause necessity validation | Measure crash rate in Phase 4 | Pending |

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
| 4 | Test strategy design | ✅ Complete |
| 5 | Test execution (Phase 4a/4b/4c) + refinement | ~90-120 min |
| 6 | Documentation + justification | ~30-45 min |
| **Total** | | **~4-5 hours** |

---

## Notes

- Context clearing between phases recommended (save outputs, use plan as reference)
- Phase 4 requires local model endpoint (OpenVINO OVMS or similar)
- Phase 5 can run in parallel with Phase 4 test execution
