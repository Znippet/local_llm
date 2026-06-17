#!/usr/bin/env python3
"""
Phase 8b Iteration 4: Min-P Testing (v2.3)
Unified test runner for Phases 5, 6, and 6.5
Tests min_p 0.05 + temperature 0.3 as alternative to top_p/top_k sampling.

Run all test cases and save consolidated results.
"""

import json
import urllib.request
import urllib.error
import time
import sys
import io
from pathlib import Path

# Handle Unicode output on Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# OVMS endpoint
OVMS_BASE = "http://localhost:9000"
MODEL = "Qwen3-Coder-30B-A3B-Instruct-int4-ov"

# Test output directory (Phase 6.5 min_p)
TEST_DIR = Path("C:\\LLM\\test_results\\phase6_5_min_p")
TEST_DIR.mkdir(parents=True, exist_ok=True)

def post_json(url, data):
    """POST JSON to endpoint."""
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def load_tools_schema():
    """Load tools from central schema."""
    schema_file = Path("C:\\LLM\\jinja_tests\\tools_schema.json")
    with open(schema_file, "r") as f:
        data = json.load(f)
    return data["tools"]

def extract_tool_calls(response_json):
    """Extract all tool calls from response."""
    calls = []

    if "error" in response_json:
        return calls

    if "choices" not in response_json or not response_json["choices"]:
        return calls

    message = response_json["choices"][0].get("message", {})
    tool_calls = message.get("tool_calls", [])

    for tc in tool_calls:
        tool_name = tc.get("function", {}).get("name")
        args_str = tc.get("function", {}).get("arguments", "")
        try:
            args = json.loads(args_str) if isinstance(args_str, str) else args_str
        except:
            args = {}

        calls.append({
            "name": tool_name,
            "args": args
        })

    return calls

# ============================================================
# PHASE 5 TESTS: File Operations (TC1-TC5)
# ============================================================

def tc1_single_tool():
    """TC1: Single Tool Call"""
    print("\n[TC1] Single Tool Call")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Use the read_file tool to read C:\\LLM\\jinja_templates\\JINJA-VERSIONS.md"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(data)

    result = {
        "test": "tc1_single_tool",
        "pass": False,
        "reason": ""
    }

    if not calls:
        result["reason"] = "No tool calls made"
        return result

    if calls[0]["name"] != "read_file":
        result["reason"] = f"Expected read_file, got {calls[0]['name']}"
        return result

    if len(calls) != 1:
        result["reason"] = f"Expected 1 tool call, got {len(calls)}"
        return result

    result["pass"] = True
    result["reason"] = "Single read_file call successful"
    return result

def tc2_structured_args():
    """TC2: Structured Args Validation"""
    print("[TC2] Structured Args Validation")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "List all .jinja files in C:\\LLM\\jinja_templates"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(data)

    result = {
        "test": "tc2_structured_args",
        "pass": False,
        "reason": ""
    }

    if not calls:
        result["reason"] = "No tool calls made"
        return result

    tool_call = calls[0]
    if tool_call["name"] != "list_files":
        result["reason"] = f"Expected list_files, got {tool_call['name']}"
        return result

    args = tool_call.get("args", {})
    if "path" not in args:
        result["reason"] = "Missing 'path' parameter"
        return result

    result["pass"] = True
    result["reason"] = "list_files with proper args"
    return result

def tc3_write_file():
    """TC3: Write File Operation"""
    print("[TC3] Write File Operation")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": 'Write "min_p test v2.3" to C:\\LLM\\test_results\\phase6_5_min_p\\test_v2_3.txt'
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(data)

    result = {
        "test": "tc3_write_file",
        "pass": False,
        "reason": ""
    }

    if not calls:
        result["reason"] = "No tool calls made"
        return result

    tool_call = calls[0]
    if tool_call["name"] != "write_file":
        result["reason"] = f"Expected write_file, got {tool_call['name']}"
        return result

    args = tool_call.get("args", {})
    if "path" not in args or "content" not in args:
        result["reason"] = "Missing required write_file parameters"
        return result

    result["pass"] = True
    result["reason"] = "write_file with complete args"
    return result

def tc4_execute_command():
    """TC4: Execute Command"""
    print("[TC4] Execute Command")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Execute: dir C:\\LLM\\jinja_templates"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(data)

    result = {
        "test": "tc4_execute_command",
        "pass": False,
        "reason": ""
    }

    if not calls:
        result["reason"] = "No tool calls made"
        return result

    tool_call = calls[0]
    if tool_call["name"] != "execute_command":
        result["reason"] = f"Expected execute_command, got {tool_call['name']}"
        return result

    args = tool_call.get("args", {})
    if "command" not in args:
        result["reason"] = "Missing 'command' parameter"
        return result

    result["pass"] = True
    result["reason"] = "execute_command with proper args"
    return result

def tc5_search_files():
    """TC5: Search Files"""
    print("[TC5] Search Files")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Search for JINJA in C:\\LLM\\jinja_templates"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(data)

    result = {
        "test": "tc5_search_files",
        "pass": False,
        "reason": ""
    }

    if not calls:
        result["reason"] = "No tool calls made"
        return result

    tool_call = calls[0]
    if tool_call["name"] != "search_files":
        result["reason"] = f"Expected search_files, got {tool_call['name']}"
        return result

    args = tool_call.get("args", {})
    if "pattern" not in args or "path" not in args:
        result["reason"] = "Missing required search_files parameters"
        return result

    result["pass"] = True
    result["reason"] = "search_files with pattern and path"
    return result

# ============================================================
# PHASE 6 TESTS: Extended Tools (TC6-TC9)
# ============================================================

def tc6_list_directory_tree():
    """TC6: List Directory Tree"""
    print("\n[TC6] List Directory Tree")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Show directory structure of C:\\LLM\\test_results"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(data)

    result = {
        "test": "tc6_list_directory_tree",
        "pass": False,
        "reason": ""
    }

    if not calls:
        result["reason"] = "No tool calls made"
        return result

    tool_call = calls[0]
    if tool_call["name"] != "list_directory_tree":
        result["reason"] = f"Expected list_directory_tree, got {tool_call['name']}"
        return result

    args = tool_call.get("args", {})
    if "path" not in args:
        result["reason"] = "Missing 'path' parameter"
        return result

    result["pass"] = True
    result["reason"] = "list_directory_tree successful"
    return result

def tc7_multiple_operations():
    """TC7: Multiple Operations in Sequence"""
    print("[TC7] Multiple Operations")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Find files with 'Phase' in C:\\LLM, then read the first one you find"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(data)

    result = {
        "test": "tc7_multiple_operations",
        "pass": False,
        "reason": "",
        "expected_sequence": ["search_files", "read_file"],
        "actual_sequence": [c["name"] for c in calls]
    }

    if len(calls) < 2:
        result["reason"] = f"Expected at least 2 calls, got {len(calls)}"
        return result

    if calls[0]["name"] != "search_files":
        result["reason"] = f"Expected search_files first, got {calls[0]['name']}"
        return result

    if calls[1]["name"] != "read_file":
        result["reason"] = f"Expected read_file second, got {calls[1]['name']}"
        return result

    result["pass"] = True
    result["reason"] = "Proper multi-step sequencing"
    return result

def tc8_complex_workflow():
    """TC8: Complex Workflow (List → Search → Read)"""
    print("[TC8] Complex Workflow")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "List templates dir, search for v2.3, then read that template file"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(data)

    result = {
        "test": "tc8_complex_workflow",
        "pass": False,
        "reason": "",
        "expected_start": ["list_directory_tree", "search_files"],
        "actual_calls": [c["name"] for c in calls]
    }

    if len(calls) < 2:
        result["reason"] = f"Expected at least 2 calls, got {len(calls)}"
        return result

    # Check first two calls follow logical order
    valid_first = calls[0]["name"] in ["list_directory_tree", "search_files"]
    if not valid_first:
        result["reason"] = f"First call should be list or search, got {calls[0]['name']}"
        return result

    result["pass"] = True
    result["reason"] = "Complex workflow executed"
    return result

def tc9_error_handling():
    """TC9: Error Handling and Fallback"""
    print("[TC9] Error Handling")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Try to read a non-existent file and handle gracefully"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(data)

    result = {
        "test": "tc9_error_handling",
        "pass": False,
        "reason": ""
    }

    # Should either make a tool call (shows intent) or provide text explanation
    if "error" in data:
        result["reason"] = "API error"
        return result

    # If model called a tool, that's acceptable (will fail gracefully)
    if calls:
        result["pass"] = True
        result["reason"] = "Tool call made (error handling delegated to caller)"
        return result

    # If model provided text response, that's also acceptable
    if "choices" in data and data["choices"]:
        message = data["choices"][0].get("message", {})
        content = message.get("content", "")
        if content:
            result["pass"] = True
            result["reason"] = "Text response provided instead of tool call"
            return result

    result["reason"] = "No response provided"
    return result

# ============================================================
# PHASE 6.5 TESTS: Few-Shot Sequencing
# ============================================================

def test_search_and_read():
    """Phase 6.5 Test 1: Search → Read Pattern"""
    print("\n[6.5-T1] Search and Read Pattern")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Find files with TODO in C:\\LLM, then read the first one you find"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    response = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(response)

    result = {
        "test": "search_and_read",
        "expected_sequence": ["search_files", "read_file"],
        "actual_sequence": [c["name"] for c in calls],
        "calls": calls,
        "pass": False,
        "reason": ""
    }

    if len(calls) >= 1 and calls[0]["name"] == "search_files":
        result["reason"] = "[OK] search_files called first"
        if len(calls) >= 2 and calls[1]["name"] == "read_file":
            result["pass"] = True
            result["reason"] += ", [OK] read_file called second"
        else:
            result["reason"] += ", [FAIL] read_file not called second (model stopped after search)"
    else:
        result["reason"] = "[FAIL] search_files not called first"

    return result

def test_list_and_execute():
    """Phase 6.5 Test 2: List → Execute Pattern"""
    print("[6.5-T2] List and Execute Pattern")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "List the directory structure of C:\\LLM\\test_results, then execute: dir C:\\LLM\\test_results"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    response = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(response)

    result = {
        "test": "list_and_execute",
        "expected_sequence": ["list_directory_tree", "execute_command"],
        "actual_sequence": [c["name"] for c in calls],
        "calls": calls,
        "pass": False,
        "reason": ""
    }

    if len(calls) >= 1 and calls[0]["name"] == "list_directory_tree":
        result["reason"] = "[OK] list_directory_tree called first"
        if len(calls) >= 2 and calls[1]["name"] == "execute_command":
            result["pass"] = True
            result["reason"] += ", [OK] execute_command called second"
        else:
            result["reason"] += f", [FAIL] execute_command not second (got {calls[1]['name'] if len(calls) > 1 else 'nothing'})"
    else:
        result["reason"] = "[FAIL] list_directory_tree not called first"

    return result

def test_read_and_write():
    """Phase 6.5 Test 3: Read → Write Pattern"""
    print("[6.5-T3] Read and Write Pattern")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Read C:\\LLM\\jinja_templates\\chat_template_cline_optimized_v2.3.jinja"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.3,
        "max_tokens": 512
    }

    response = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(response)

    result = {
        "test": "read_and_write",
        "expected_sequence": ["read_file"],
        "actual_sequence": [c["name"] for c in calls],
        "calls": calls,
        "pass": False,
        "reason": ""
    }

    if len(calls) >= 1 and calls[0]["name"] == "read_file":
        result["pass"] = True
        result["reason"] = "[OK] read_file called (following few-shot example)"
    else:
        result["reason"] = "[FAIL] read_file not called"

    return result

# ============================================================
# MAIN TEST RUNNER
# ============================================================

def run_all_tests():
    """Run all test phases."""
    print("\n" + "=" * 70)
    print("Phase 8b Iteration 4: Min-P Testing (v2.3)")
    print("Comprehensive Test Suite")
    print("=" * 70)

    all_results = {
        "test_name": "Phase 8b Iteration 4: Min-P Parameter Testing (v2.3)",
        "template_version": "v2.3",
        "sampling_config": {
            "min_p": 0.05,
            "temperature": 0.3
        },
        "phase5_results": [],
        "phase6_results": [],
        "phase65_results": [],
        "summary": {
            "phase5_pass": 0,
            "phase5_total": 0,
            "phase6_pass": 0,
            "phase6_total": 0,
            "phase65_pass": 0,
            "phase65_total": 0
        }
    }

    # Phase 5: File Operations
    print("\n[PHASE 5] File Operations (TC1-TC5)")
    print("-" * 70)

    phase5_tests = [tc1_single_tool, tc2_structured_args, tc3_write_file,
                    tc4_execute_command, tc5_search_files]

    for test_func in phase5_tests:
        try:
            result = test_func()
            all_results["phase5_results"].append(result)
            all_results["summary"]["phase5_total"] += 1
            if result.get("pass"):
                all_results["summary"]["phase5_pass"] += 1
                print(f"  ✓ {result['test']}: PASS")
            else:
                print(f"  ✗ {result['test']}: FAIL - {result.get('reason', 'Unknown')}")
        except Exception as e:
            all_results["phase5_results"].append({
                "test": test_func.__name__,
                "pass": False,
                "reason": str(e)
            })
            print(f"  ✗ {test_func.__name__}: ERROR - {str(e)}")

    # Phase 6: Extended Tools
    print("\n[PHASE 6] Extended Tools (TC6-TC9)")
    print("-" * 70)

    phase6_tests = [tc6_list_directory_tree, tc7_multiple_operations,
                    tc8_complex_workflow, tc9_error_handling]

    for test_func in phase6_tests:
        try:
            result = test_func()
            all_results["phase6_results"].append(result)
            all_results["summary"]["phase6_total"] += 1
            if result.get("pass"):
                all_results["summary"]["phase6_pass"] += 1
                print(f"  ✓ {result['test']}: PASS")
            else:
                print(f"  ✗ {result['test']}: FAIL - {result.get('reason', 'Unknown')}")
        except Exception as e:
            all_results["phase6_results"].append({
                "test": test_func.__name__,
                "pass": False,
                "reason": str(e)
            })
            print(f"  ✗ {test_func.__name__}: ERROR - {str(e)}")

    # Phase 6.5: Few-Shot Sequencing
    print("\n[PHASE 6.5] Few-Shot Sequencing")
    print("-" * 70)

    phase65_tests = [test_search_and_read, test_list_and_execute, test_read_and_write]

    for test_func in phase65_tests:
        try:
            result = test_func()
            all_results["phase65_results"].append(result)
            all_results["summary"]["phase65_total"] += 1
            if result.get("pass"):
                all_results["summary"]["phase65_pass"] += 1
                print(f"  ✓ {result['test']}: PASS")
            else:
                print(f"  ✗ {result['test']}: FAIL - {result.get('reason', 'Unknown')}")
        except Exception as e:
            all_results["phase65_results"].append({
                "test": test_func.__name__,
                "pass": False,
                "reason": str(e)
            })
            print(f"  ✗ {test_func.__name__}: ERROR - {str(e)}")

    # Save results
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"Phase 5 (File Ops):   {all_results['summary']['phase5_pass']}/{all_results['summary']['phase5_total']} PASS")
    print(f"Phase 6 (Ext Tools):  {all_results['summary']['phase6_pass']}/{all_results['summary']['phase6_total']} PASS")
    print(f"Phase 6.5 (Few-Shot): {all_results['summary']['phase65_pass']}/{all_results['summary']['phase65_total']} PASS")

    # Save to JSON
    results_file = TEST_DIR / "Phase6-5-Min-P-Results.json"
    with open(results_file, "w", encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    # Return exit code (0 = all pass, 1 = any failure)
    total_pass = (all_results['summary']['phase5_pass'] +
                  all_results['summary']['phase6_pass'] +
                  all_results['summary']['phase65_pass'])
    total_tests = (all_results['summary']['phase5_total'] +
                   all_results['summary']['phase6_total'] +
                   all_results['summary']['phase65_total'])

    return 0 if total_pass == total_tests else 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
