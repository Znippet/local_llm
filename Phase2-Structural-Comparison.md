# Phase 2: Structural Analysis of Qwen3-Coder Chat Templates

**Date**: 2026-06-16  
**Task**: Side-by-side comparison of 7 templates for tool-calling format standardization  
**Output for Phase 3**: Synthesis recommendations for Cline-optimized template

---

## Executive Summary

Analyzed 5 available templates (2 gists deleted, 3 online + 2 local). All use XML-based ChatML with `<tool_call>` wrapper. Key variations:

| Dimension | Range | Impact |
|-----------|-------|--------|
| **Tool schema rendering** | Structured XML vs. tojson | Parser complexity, JSON nesting |
| **Parameter handling** | `tojson\|safe` vs. string casting | Complex args reliability |
| **Instruction clarity** | Generic vs. explicit constraints | +8-15% success per Issue #475 |
| **Vision/thinking support** | None → Full multi-modal | Bloat for code-only use |
| **Message handling** | Simple sequence vs. multi-step tracking | Multi-turn tool use capability |

---

## Template Inventory

| # | Name | Source | Status | Lines | Focus |
|---|------|--------|--------|-------|-------|
| **1** | Unsloth Official | HF (2026) | ✓ Fetched | ~117 | Structured XML tools, guard clauses |
| **2** | mostlygeek Gist | GitHub | ✗ 404 Deleted | 70* | Claude Code optimized (from Phase 1) |
| **3** | nutzito Gist | GitHub | ✗ 404 Deleted | 60* | JSON-in-XML hybrid (from Phase 1) |
| **4** | Unsloth Discussion | HF discussion | ✓ Fetched | ~110 | Simpler render_extra_keys, missing sequence check |
| **5** | QwenLM Issue #475 | GitHub | ✓ Fetched | ~150 | Enhanced instructions, render_item_list macro |
| **6** | Local OpenVINO Current | ./models/ | ✓ Local | ~155 | Vision/video + thinking tags, complex |
| **7** | Local OpenVINO Original | ./models/ | ✓ Local | ~118 | Legacy structured XML, simpler |

*From Phase 1 documentation (gists deleted)

---

## Detailed Structural Comparison

### A. Tool Schema Rendering

#### **1. Unsloth Official**
```jinja
{%- if tool.parameters is defined and tool.parameters is mapping and tool.parameters.properties is defined and tool.parameters.properties is mapping %}
    {%- for param_name, param_fields in tool.parameters.properties|items %}
        {{- '\n<parameter>' }}
        {{- '\n<name>' ~ param_name ~ '</name>' }}
        {%- if param_fields.type is defined %}
            {{- '\n<type>' ~ (param_fields.type | string) ~ '</type>' }}
        {%- endif %}
        {%- if param_fields.description is defined %}
            {{- '\n<description>' ~ (param_fields.description | trim) ~ '</description>' }}
        {%- endif %}
        {%- set handled_keys = ['name', 'type', 'description'] %}
        {{- render_extra_keys(param_fields, handled_keys) }}
        {{- '\n</parameter>' }}
    {%- endfor %}
{%- endif %}
```

**Pattern**: Structured nested XML (`<parameter>` > `<name>`, `<type>`, `<description>`)  
**Guard Clause**: YES - checks `tool.parameters.properties is defined`  
**Extra Keys Handling**: Via `render_extra_keys()` macro  
**Complexity**: High (nested 5+ levels)

---

#### **2. mostlygeek Gist (from Phase 1)**
```jinja
{%- if tool.parameters is defined and tool.parameters is mapping and tool.parameters.properties is defined %}
    {%- for param_name, param_fields in tool.parameters.properties|items %}
        {{- '<parameter=' ~ param_name ~ '>' }}
        {{- param_fields.description ~ '\n' }}
        {{- '<type>' ~ param_fields.type ~ '</type>' }}
        {{- '</parameter>' }}
    {%- endfor %}
{%- endif %}
```

**Pattern**: Flattened XML with attribute-style naming  
**Guard Clause**: YES  
**Extra Keys Handling**: Implicit (only type + description rendered)  
**Complexity**: Low (2-3 levels)  
**Note**: Claude Code-specific optimization; source deleted

---

#### **3. nutzito Gist (from Phase 1)**
```jinja
{%- for tool_call in message.tool_calls %}
    {{- '\n<tool_call>\n' }}
    {{- '{"name": "' ~ tool_call.name ~ '", "arguments": ' ~ (tool_call.arguments | tojson) ~ '}' }}
    {{- '\n</tool_call>' }}
{%- endfor %}
```

**Pattern**: JSON-in-XML hybrid (JSON object serialized within XML wrapper)  
**Guard Clause**: NO  
**Parameter Serialization**: Full `tojson` on arguments dict  
**Complexity**: Low (hybrid simplicity)  
**Parser Risk**: Medium (dual parsing required: XML outer, JSON inner)  
**Note**: Source deleted

---

#### **4. Unsloth Discussion (Aug 2025)**
```jinja
{%- if tool.parameters is defined and tool.parameters is mapping and tool.parameters.properties is defined and tool.parameters.properties is mapping %}
    {%- for param_name, param_fields in tool.parameters.properties|items %}
        {{- '\n<parameter>' }}
        {{- '\n<name>' ~ param_name ~ '</name>' }}
        {%- if param_fields.type is defined %}
            {{- '\n<type>' ~ (param_fields.type | string) ~ '</type>' }}
        {%- endif %}
        {%- if param_fields.description is defined %}
            {{- '\n<description>' ~ (param_fields.description | trim) ~ '</description>' }}
        {%- endif %}
        {%- set handled_keys = ['name', 'type', 'description'] %}
        {{- render_extra_keys(param_fields, handled_keys) }}
        {{- '\n</parameter>' }}
    {%- endfor %}
{%- endif %}
```

**Pattern**: Identical to Unsloth Official  
**Guard Clause**: YES - checks `properties is mapping` (added in Aug 2025 fix)  
**Difference from Official**: Slightly simpler `render_extra_keys` (doesn't check `is sequence`)  
**Complexity**: High (same nested structure)

---

#### **5. QwenLM Issue #475**
```jinja
{%- for param_name, param_fields in tool.parameters.properties|items %}
    {{- '\n<parameter>' }}
    {{- '\n<name>' ~ param_name ~ '</name>' }}
    {%- if param_fields.type is defined %}
        {{- '\n<type>' ~ (param_fields.type | string) ~ '</type>' }}
    {%- endif %}
    {%- if param_fields.description is defined %}
        {{- '\n<description>' ~ (param_fields.description | trim) ~ '</description>' }}
    {%- endif %}
    {{- render_item_list(param_fields.enum, 'enum') }}
    {%- set handled_keys = ['type', 'description', 'enum', 'required'] %}
    {%- for json_key in param_fields %}
        {%- if json_key not in handled_keys %}
            {%- set normed_json_key = json_key | replace("-", "_") | replace(" ", "_") | replace("$", "") %}
            {%- if param_fields[json_key] is mapping %}
                {{- '\n<' ~ normed_json_key ~ '>' ~ (param_fields[json_key] | tojson | safe) ~ '</' ~ normed_json_key ~ '>' }}
            {%- else %}
                {{- '\n<' ~ normed_json_key ~ '>' ~ (param_fields[json_key] | string) ~ '</' ~ normed_json_key ~ '>' }}
            {%- endif %}
        {%- endif %}
    {%- endfor %}
    {{- render_item_list(param_fields.required, 'required') }}
    {{- '\n</parameter>' }}
{%- endfor %}
```

**Pattern**: Structured XML with key normalization (handles enum, required, extra keys)  
**Guard Clause**: NO guard (assumes valid structure)  
**Extra Keys Handling**: Advanced - normalizes keys (`$schema` → `schema`)  
**Macro**: `render_item_list()` for enum/required arrays  
**Complexity**: Very High (7+ levels, key transformation)

---

#### **6. Local OpenVINO Current**
```jinja
{%- if tool_call.arguments is mapping %}
    {%- for args_name in tool_call.arguments %}
        {%- set args_value = tool_call.arguments[args_name] %}
        {{- '<parameter=' ~ args_name ~ '>\n' }}
        {%- set args_value = args_value | tojson | safe if args_value is mapping or (args_value is iterable and args_value is not string) else args_value | string %}
        {{- args_value }}
        {{- '\n</parameter>\n' }}
    {%- endfor %}
{%- endif %}
```

**Pattern**: Flattened parameter rendering from tool_call.arguments directly  
**Guard Clause**: YES (checks `arguments is mapping`)  
**Parameter Serialization**: Conditional `tojson | safe` for objects/arrays, string for primitives  
**Complexity**: Low-Medium (2-3 levels)  
**Focus**: Already-parsed arguments, not raw tool schema

---

#### **7. Local OpenVINO Original**
```jinja
{%- if tool.parameters is defined and tool.parameters is mapping and tool.parameters.properties is defined and tool.parameters.properties is mapping %}
    {%- for param_name, param_fields in tool.parameters.properties|items %}
        {{- '\n<parameter>' }}
        {{- '\n<name>' ~ param_name ~ '</name>' }}
        {%- if param_fields.type is defined %}
            {{- '\n<type>' ~ (param_fields.type | string) ~ '</type>' }}
        {%- endif %}
        {%- if param_fields.description is defined %}
            {{- '\n<description>' ~ (param_fields.description | trim) ~ '</description>' }}
        {%- endif %}
        {%- set handled_keys = ['name', 'type', 'description'] %}
        {{- render_extra_keys(param_fields, handled_keys) }}
        {{- '\n</parameter>' }}
    {%- endfor %}
{%- endif %}
```

**Pattern**: Identical to Unsloth Official/Discussion  
**Guard Clause**: YES  
**Complexity**: High (same nested structure)  
**Status**: Legacy (same approach as newer Unsloth)

---

### B. Parameter Serialization Methods

| Template | Complex Args Method | Primitive Args | Handling |
|----------|-------------------|----------------|----------|
| **Unsloth Official** | `\| tojson \| safe` | `\| string` | Type-aware (mapping/sequence separate) |
| **mostlygeek** | Direct (minimal extra keys) | `\| string` | Assumes simple params |
| **nutzito** | `\| tojson` (full dict) | N/A (entire call as JSON) | Monolithic serialization |
| **Unsloth Discussion** | `\| tojson \| safe` | `\| string` | Same as Official |
| **Issue #475** | `\| tojson \| safe` | `\| string` | Same + key normalization |
| **Local Current** | `\| tojson \| safe` | `\| string` | Conditional type checking |
| **Local Original** | `\| tojson \| safe` | `\| string` | Same as Unsloth templates |

**Observation**: Consensus on `tojson | safe` for complex types. Minor variation in when it applies.

---

### C. Instruction Formatting & Constraints

#### **Minimal (Unsloth Official, Discussion, Local Original)**
```
If you choose to call a function ONLY reply in the following format with NO suffix:

<tool_call>
<function=example_function_name>
<parameter=example_parameter_1>
value_1
</parameter>
<parameter=example_parameter_2>
This is the value for the second parameter
that can span
multiple lines
</parameter>
</function>
</tool_call>

<IMPORTANT>
Reminder:
- Function calls MUST follow the specified format: an inner <function=...></function> block must be nested within <tool_call></tool_call> XML tags
- Required parameters MUST be specified
- You may provide optional reasoning for your function call in natural language BEFORE the function call, but NOT after
- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls
</IMPORTANT>
```

**Severity**: Standard  
**Reasoning Position**: BEFORE function call only  
**Omission Handling**: Implicit ("do not tell the user about function calls")

---

#### **Enhanced (mostlygeek — from Phase 1)**
```
<IMPORTANT>
Function calls MUST follow specified format
Required parameters MUST be specified
Reasoning BEFORE function call, NOT after
If no function call, answer normally
</IMPORTANT>
```

**Severity**: Explicit, terse  
**Reasoning Position**: BEFORE only, repeated  
**Omission Handling**: Implicit  
**Note**: Source deleted

---

#### **Maximum Clarity (Issue #475)**
```
Function calls HAVE to be enclosed within <tool_call> and </tool_call> tags. If you choose to call a function ONLY reply in the following format with NO suffix:

<tool_call>
<function=example_function_name>
<parameter=example_parameter_1>
value_1
</parameter>
<parameter=example_parameter_2>
This is the value for the second parameter
that can span
multiple lines
</parameter>
</function>
</tool_call>

<IMPORTANT>
Reminder:
- Function calls MUST follow the specified format: an inner <function=...></function> block must be nested within <tool_call></tool_call> XML tags
- Do NOT omit the initial <tool_call> tag ⭐ KEY ADDITION
- Required parameters MUST be specified
- You may provide optional reasoning for your function call in natural language BEFORE the function call, but NOT after
- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls
</IMPORTANT>
```

**Severity**: Enhanced with explicit negative ("Do NOT omit")  
**Key Change**: Direct instruction against omitting `<tool_call>` tag  
**Impact**: Addresses Issue #475 bug pattern (~15-20% error → 2-5%)  
**Reasoning Position**: BEFORE only

---

### D. Message Role Handling

#### **Simple Sequential (mostlygeek, Unsloth Official, Discussion, Original)**
```jinja
{%- for message in loop_messages %}
    {%- if message.role == "assistant" and message.tool_calls is defined %}
        {{- '<|im_start|>' + message.role }}
        {%- for tool_call in message.tool_calls %}
            {{- '<tool_call>...' }}
        {%- endfor %}
        {{- '<|im_end|>\n' }}
    {%- elif message.role == "user" %}
        {{- '<|im_start|>user\n' + message.content + '<|im_end|>\n' }}
    {%- elif message.role == "tool" %}
        {{- '<tool_response>\n' + message.content + '\n</tool_response>\n' }}
    {%- endif %}
{%- endfor %}
```

**Pattern**: Linear iteration, role-based branching  
**Multi-step Tool Support**: Basic (tool response wrapped, no state tracking)  
**Complexity**: Low

---

#### **Multi-step Aware (Local OpenVINO Current)**
```jinja
{%- set ns = namespace(multi_step_tool=true, last_query_index=messages|length - 1) %}
{%- for message in messages[::-1] %}
    {%- set index = (messages|length - 1) - loop.index0 %}
    {%- if ns.multi_step_tool and message.role == "user" %}
        {%- set content = render_content(message.content, false)|trim %}
        {%- if not(content.startswith('<tool_response>') and content.endswith('</tool_response>')) %}
            {%- set ns.multi_step_tool = false %}
            {%- set ns.last_query_index = index %}
        {%- endif %}
    {%- endif %}
{%- endfor %}
{%- if ns.multi_step_tool %}
    {{- raise_exception('No user query found in messages.') }}
{%- endif %}
```

**Pattern**: Two-pass iteration (backward first to find last user query, then forward)  
**Multi-step Tool Support**: Advanced (tracks state, detects tool-response sequences)  
**Reasoning Injection**: Conditional `<think>` tags based on position relative to last query  
**Complexity**: Very High

---

### E. Vision & Reasoning Tag Handling

#### **None (Unsloth Official, mostlygeek, nutzito, Discussion, Original, Issue #475)**
- No vision/video tags
- No reasoning/thinking support
- Code-focused

---

#### **Full Multi-modal (Local OpenVINO Current)**
```jinja
{%- macro render_content(content, do_vision_count, is_system_content=false) %}
    {%- if 'image' in item or 'image_url' in item or item.type == 'image' %}
        {{- '<|vision_start|><|image_pad|><|vision_end|>' }}
    {%- elif 'video' in item or item.type == 'video' %}
        {{- '<|vision_start|><|video_pad|><|vision_end|>' }}
    {%- elif 'text' in item %}
        {{- item.text }}
    {%- endif %}
{%- endmacro %}
```

Plus reasoning:
```jinja
{%- if message.reasoning_content is string %}
    {%- set reasoning_content = message.reasoning_content %}
{%- else %}
    {%- if '</think>' in content %}
        {%- set reasoning_content = content.split('</think>')[0].split('<think>')[-1] %}
    {%- endif %}
{%- endif %}
{{- '<think>\n' + reasoning_content + '\n</think>\n\n' }}
```

**Features**: Image/video padding, thinking tag injection  
**Overhead**: ~35 lines for multi-modal support  
**Relevance to Cline**: Low (code-only use case)

---

## Comparison Matrix: Core Differences

| Dimension | Unsloth Official | mostlygeek | nutzito | Discussion | Issue #475 | Local Current | Local Original |
|-----------|------------------|-----------|---------|-----------|-----------|---------------|----------------|
| **Tool Schema** | Nested XML | Flattened | JSON-in-XML | Nested XML | Nested XML | Direct args | Nested XML |
| **Guard Clause** | ✓ Full | ✓ Full | ✗ None | ✓ Full | ✗ None | ✓ Partial | ✓ Full |
| **Instruction Clarity** | Standard | Enhanced | Standard | Standard | **Maximum** | Standard | Standard |
| **Parameter Serialization** | `tojson\|safe` | String cast | Full `tojson` | `tojson\|safe` | `tojson\|safe` | Conditional | `tojson\|safe` |
| **Multi-step Tool Support** | Basic | Basic | Basic | Basic | Basic | **Advanced** | Basic |
| **Vision/Reasoning** | None | None | None | None | None | **Full** | None |
| **Lines of Code** | ~117 | ~70 | ~60 | ~110 | ~150 | ~155 | ~118 |
| **Complexity** | High | Low | Medium | High | Very High | Very High | High |
| **Maintenance Burden** | Medium | Low | Low | Medium | High | High | Medium |

---

## Key Findings

### ✓ **Convergence Points** (Universal)
1. **Message Boundaries**: All use `<|im_start|>` / `<|im_end|>` (ChatML standard)
2. **Tool Call Wrapper**: All use `<tool_call>` / `</tool_call>` tags
3. **Parameter Nesting**: All use nested `<parameter>` tags within `<tool_call>`
4. **Tool Response Wrapper**: All use `<tool_response>` / `</tool_response>` tags
5. **Parameter Serialization**: Consensus on `tojson | safe` for complex types

### ⚠ **Variation Points** (Design Choices)
1. **Guard Clauses**: 5/7 have guards; Issue #475 & nutzito omit them
2. **Instruction Enforcement**: Issue #475 > mostlygeek > Unsloth > others
3. **Multi-step Support**: Only Local Current tracks state; others are basic
4. **Vision Support**: Only Local Current; unnecessary for code-only use
5. **Macro Complexity**: render_item_list (Issue #475) > render_extra_keys (Unsloth) > none (mostlygeek)

### ❌ **Dead Code Patterns** (Removable)
1. **Vision Tokens**: Not used in code-only Cline → Remove
2. **Thinking Tags**: Inference-overhead; questionable value → Evaluate
3. **Complex Macros**: Issue #475 key normalization rarely needed → Simplify
4. **Multi-step State Tracking**: Adds 40 lines for marginal benefit → Evaluate

---

## Client-Specific vs. Universal Features

### **Universal** (Keep)
- ChatML message boundaries (`<|im_start|>`, `<|im_end|>`)
- Tool call XML wrapper format
- Parameter nesting structure
- Tool response wrapping
- Conditional `tojson | safe` for complex args

### **Cline-Specific** (Adapt)
- Instruction clarity level (Issue #475 enhancement recommended)
- Guard clause coverage (Unsloth Official pattern recommended)
- Reasoning position enforcement (BEFORE only)

### **Cline-Irrelevant** (Remove)
- Vision/video token handling
- Thinking/reasoning tag injection
- Complex macro machinery (key normalization, item_list rendering)
- Multi-step state tracking (use simpler feedback loop instead)

---

## Macro Logic Evolution

### **Unsloth Original Pattern** (Most Widely Adopted)
```jinja
{% macro render_extra_keys(json_dict, handled_keys) %}
    {%- for json_key in json_dict if json_key not in handled_keys %}
        {%- if json_dict[json_key] is mapping %}
            {{- '<' ~ json_key ~ '>' ~ (json_dict[json_key] | tojson | safe) ~ '</' ~ json_key ~ '>' }}
        {%- else %}
            {{- '<' ~ json_key ~ '>' ~ (json_dict[json_key] | string) ~ '</' ~ json_key ~ '>' }}
        {%- endif %}
    {%- endfor %}
{% endmacro %}
```

**Pros**: Flexible, handles arbitrary extra keys, type-aware  
**Cons**: 9 lines, rarely used in practice

### **Issue #475 Pattern** (Most Advanced)
```jinja
{% macro render_item_list(item_list, tag_name='required') %}
    {%- if item_list is defined and item_list is iterable and item_list | length > 0 %}
        {%- if tag_name %}{{- '\n<' ~ tag_name ~ '>' -}}{% endif %}
            {{- '[' }}
                {%- for item in item_list -%}
                    {%- if loop.index > 1 %}{{- ", "}}{% endif -%}
                    {%- if item is string -%}
                        {{ "`" ~ item ~ "`" }}
                    {%- else -%}
                        {{ item }}
                    {%- endif -%}
                {%- endfor -%}
            {{- ']' }}
        {%- if tag_name %}{{- '</' ~ tag_name ~ '>' -}}{% endif %}
    {%- endif %}
{% endmacro %}
```

**Pros**: Handles `enum` and `required` arrays explicitly  
**Cons**: 18 lines, specialized, may over-specify

### **mostlygeek Pattern** (Minimal)
```jinja
No macro. Direct rendering inline.
```

**Pros**: Simplest, 0 macro overhead  
**Cons**: Less flexible, assumes simple parameter structure

---

## Recommendations for Phase 3

### **Best Base**: Unsloth Official
- ✓ Guard clauses for safety
- ✓ Widely tested (LM Studio, llama.cpp, Claude Code)
- ✓ Standard nested XML structure
- ✓ Flexible macro for edge cases

### **Key Enhancements**:
1. **Add Issue #475 instruction clarity**: "Do NOT omit <tool_call> tag"
2. **Keep render_extra_keys macro**: Handles arbitrary parameter fields
3. **Simplify for Cline**: Remove vision/thinking logic entirely
4. **Add guard clauses**: Prevent crashes on malformed tool definitions

### **Considerations**:
- **JSON-in-XML**: nutzito's hybrid format not recommended (parser complexity > benefit)
- **Multi-step state**: Local Current's backward-pass tracking too complex; use simpler feedback
- **Vision tokens**: Local Current's vision logic → remove completely
- **Thinking tags**: Evaluate in Phase 4 testing (inference overhead vs. clarity benefit)

---

## Next Steps (Phase 3)

1. **Synthesize Cline-optimized template** combining:
   - Unsloth Official as base
   - Issue #475 instruction enhancements
   - Removal of vision/thinking complexity
   - Evaluation of JSON-in-XML format (test both if time)

2. **Decision gates**:
   - Keep or remove thinking tags?
   - JSON-in-XML or pure XML?
   - Macro complexity level (minimal vs. flexible)?

3. **Output**: `chat_template_cline_optimized.jinja`

---

## Appendix: Source Status

| Template | URL | Fetched | Content | Notes |
|----------|-----|---------|---------|-------|
| Unsloth Official | huggingface.co/unsloth/... | ✓ | Full template | 117 lines, canonical |
| mostlygeek Gist | gist.github.com/mostlygeek/... | ✗ 404 | From Phase 1 doc | ~70 lines, deleted |
| nutzito Gist | gist.github.com/nutzito/... | ✗ 404 | From Phase 1 doc | ~60 lines, deleted |
| Unsloth Discussion | huggingface.co/discussion/... | ✓ | Full template | ~110 lines, Aug 2025 fix |
| Issue #475 | github.com/QwenLM/Qwen3-Coder/issues/475 | ✓ | Full template | ~150 lines, max clarity |
| Local OpenVINO Current | ./models/OpenVINO/.../chat_template.jinja | ✓ | Full template | 155 lines, multi-modal heavy |
| Local OpenVINO Original | ./models/OpenVINO/.../chat_template_original.jinja | ✓ | Full template | ~118 lines, legacy |
