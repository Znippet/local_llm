#!/usr/bin/env python3
"""
Phase 6.5 Test: Validate Few-Shot Examples Improve Tool Sequencing
Tests whether v2.1 few-shot examples help model understand multi-step workflows.
"""

import json
import urllib.request
import time
import sys
from pathlib import Path

OVMS_BASE = "http://localhost:9000"
MODEL = "Qwen3-Coder-30B-A3B-Instruct-int4-ov"
TEST_DIR = Path("C:\\LLM\\test_results\\phase6_5_few_shot")
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

def test_search_and_read():
    """Test FEW-SHOT 2: Search → Read Pattern (from v2.1 example)"""
    print("\n[TEST 1] Search and Read Pattern")
    print("  Task: Find TODO comments then read one")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Find files with TODO comments in C:\\LLM, then read the first one you find"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
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

    # Validate: should have search_files first, then read_file
    if len(calls) >= 1 and calls[0]["name"] == "search_files":
        result["reason"] = "[OK] search_files called first"
        if len(calls) >= 2 and calls[1]["name"] == "read_file":
            result["reason"] += ", [OK] read_file called second"
            result["pass"] = True
        else:
            result["reason"] += ", but read_file not called second (model stopped after search)"
    else:
        result["reason"] = f"[FAIL] First tool not search_files (got {calls[0]['name'] if calls else 'none'})"

    return result

def test_list_and_execute():
    """Test FEW-SHOT 3: List Dir and Execute Pattern (from v2.1 example)"""
    print("\n[TEST 2] List Directory and Execute Pattern")
    print("  Task: List tests directory, then execute pytest")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Check the structure of C:\\LLM\\test_results directory and then list what's in it using command line"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
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

    # Validate: should have list_directory_tree first, then execute_command
    if len(calls) >= 1 and calls[0]["name"] == "list_directory_tree":
        result["reason"] = "[OK] list_directory_tree called first"
        if len(calls) >= 2 and calls[1]["name"] == "execute_command":
            result["reason"] += ", [OK] execute_command called second"
            result["pass"] = True
        else:
            result["reason"] += ", but execute_command not called second"
    else:
        result["reason"] = f"[FAIL] First tool not list_directory_tree (got {calls[0]['name'] if calls else 'none'})"

    return result

def test_read_and_write():
    """Test FEW-SHOT 1: Read and Write Pattern (from v2.1 example)"""
    print("\n[TEST 3] Read and Write Pattern")
    print("  Task: Understand file then write it back modified")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Examine C:\\LLM\\jinja_templates\\chat_template_cline_optimized_v2.1.jinja to understand its structure, then show me how you would modify it to add comments"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 768
    }

    response = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    calls = extract_tool_calls(response)

    result = {
        "test": "read_and_write",
        "expected_sequence": ["read_file"],  # At minimum, should read first
        "actual_sequence": [c["name"] for c in calls],
        "calls": calls,
        "pass": False,
        "reason": ""
    }

    # For this test, we mainly want to verify read_file is called (write is optional in this context)
    if len(calls) >= 1 and calls[0]["name"] == "read_file":
        result["reason"] = "[OK] read_file called first (following few-shot example)"
        result["pass"] = True
    else:
        result["reason"] = f"[FAIL] First tool not read_file (got {calls[0]['name'] if calls else 'none'})"

    return result

def main():
    print("=" * 70)
    print("Phase 6.5: Few-Shot Example Validation")
    print("=" * 70)
    print("\nTest: Do few-shot examples in v2.1 improve multi-step sequencing?")
    print("(These tests validate the 3 concrete examples added to the template)")

    # Health check
    try:
        response = urllib.request.urlopen(f"{OVMS_BASE}/v3/models/{MODEL}", timeout=5)
        if response.status != 200:
            print("[FAIL] OVMS not responding")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] OVMS error: {e}")
        sys.exit(1)

    print("[OK] OVMS responsive\n")

    # Run tests
    results = []

    print("\nRunning Few-Shot Tests...")
    print("=" * 70)

    result1 = test_search_and_read()
    results.append(result1)
    time.sleep(1)

    result2 = test_list_and_execute()
    results.append(result2)
    time.sleep(1)

    result3 = test_read_and_write()
    results.append(result3)

    # Summary
    print("\n" + "=" * 70)
    print("Few-Shot Sequencing Test Results")
    print("=" * 70)

    pass_count = sum(1 for r in results if r["pass"])
    total = len(results)

    for result in results:
        status = "[PASS]" if result["pass"] else "[FAIL]"
        print(f"\n{status} {result['test']}")
        print(f"  Expected: {' -> '.join(result['expected_sequence'])}")
        print(f"  Actual:   {' -> '.join(result['actual_sequence'])}")
        print(f"  Reason:   {result['reason']}")

    print("\n" + "=" * 70)
    print(f"Total: {pass_count}/{total} PASS")
    print("=" * 70)

    # Save results
    output_file = TEST_DIR / "Phase6-5-Few-Shot-Results.json"
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump({
            "test_name": "Phase 6.5: Few-Shot Example Validation",
            "pass_count": pass_count,
            "total_count": total,
            "results": results
        }, f, indent=2)

    print(f"\nResults saved: {output_file}")

    if pass_count >= 1:
        print(f"\n[OK] Success: At least 1/3 tests PASS (improved from 0/3 baseline)")

    return 0 if pass_count >= 1 else 1

if __name__ == "__main__":
    sys.exit(main())
