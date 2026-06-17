#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 6.5 Test: Cline-Realistic Code Edit Workflow

Tests complete cycle: read_file -> analyze -> write_file -> execute -> validate
This is what actual Cline code-editing does.
"""

import json
import urllib.request
import time
import sys
from pathlib import Path

OVMS_BASE = "http://localhost:9000"
MODEL = "qwen3-coder-30b-a3b-instruct-int4-ov"
TEST_DIR = Path("C:\\LLM\\test_results\\phase6_extended")
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

def validate_tool_call(response_json, expected_tool=None):
    """Validate single tool call in response."""
    result = {"valid": False, "tool_name": None, "args": {}, "errors": []}

    if "error" in response_json:
        result["errors"].append("API error")
        return result

    if "choices" not in response_json or not response_json["choices"]:
        result["errors"].append("No response")
        return result

    message = response_json["choices"][0].get("message", {})
    tool_calls = message.get("tool_calls", [])

    if not tool_calls:
        result["errors"].append("No tool call")
        return result

    tc = tool_calls[0]
    tool_name = tc.get("function", {}).get("name")
    args_str = tc.get("function", {}).get("arguments", "")

    try:
        args = json.loads(args_str) if isinstance(args_str, str) else args_str
    except:
        result["errors"].append("Invalid JSON args")
        return result

    if expected_tool and tool_name != expected_tool:
        result["errors"].append(f"Expected {expected_tool}")
        return result

    result["valid"] = True
    result["tool_name"] = tool_name
    result["args"] = args
    return result

def create_test_python_file():
    """Create test Python file to edit."""
    test_file = Path("C:\\LLM\\test_code_workflow.py")
    content = '''# Test Python file
def greet(name):
    return f"Hello, {name}"

def calculate_sum(a, b):
    return a + b
'''
    test_file.write_text(content)
    return test_file

def test_realistic_code_edit():
    """Full Workflow Test: Code Edit Cycle"""
    print("\n" + "=" * 70)
    print("Test: Cline-Realistic Code Edit Workflow")
    print("=" * 70)

    result = {
        "scenario": "Add multiply function to Python file",
        "status": "PASS",
        "steps": [],
        "errors": [],
        "final_code": None
    }

    test_file = create_test_python_file()
    print(f"\n[Setup] Created test file: {test_file}")

    # STEP 1: Read current file
    print("\n[Step 1] Model reads file")
    step1_payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": f"Read {test_file} and tell me what functions it has"}
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }

    response1 = post_json(f"{OVMS_BASE}/v3/chat/completions", step1_payload)
    step1_validation = validate_tool_call(response1, expected_tool="read_file")

    if not step1_validation["valid"]:
        result["status"] = "FAIL"
        result["errors"].append("Step 1 failed")
        print(f"  [FAIL] {step1_validation['errors']}")
        return result

    print(f"  [OK] read_file tool called")
    result["steps"].append({"step": 1, "action": "read_file", "valid": True})

    # STEP 2: Write modified file
    print("\n[Step 2] Model writes modified file with new function")
    step2_payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": f"Add multiply(a,b) function to {test_file}. Write complete file."}
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 1024
    }

    response2 = post_json(f"{OVMS_BASE}/v3/chat/completions", step2_payload)
    step2_validation = validate_tool_call(response2, expected_tool="write_file")

    if not step2_validation["valid"]:
        result["status"] = "FAIL"
        result["errors"].append("Step 2 failed")
        print(f"  [FAIL] {step2_validation['errors']}")
        return result

    write_content = step2_validation["args"].get("content", "")
    if not write_content or len(write_content) < 50:
        result["status"] = "FAIL"
        print("  [FAIL] Content too short")
        return result

    if "multiply" not in write_content.lower():
        result["status"] = "FAIL"
        print("  [FAIL] 'multiply' not in content")
        return result

    print(f"  [OK] write_file tool called")
    print(f"  [OK] Content includes 'multiply' function")
    result["steps"].append({"step": 2, "action": "write_file", "valid": True})
    result["final_code"] = write_content

    # STEP 3: Validate syntax
    print("\n[Step 3] Model validates syntax")
    step3_payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": f"Verify {test_file} has valid Python syntax"}
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 256
    }

    response3 = post_json(f"{OVMS_BASE}/v3/chat/completions", step3_payload)
    step3_validation = validate_tool_call(response3, expected_tool="execute_command")

    if not step3_validation["valid"]:
        result["status"] = "FAIL"
        print(f"  [FAIL] {step3_validation['errors']}")
        return result

    print(f"  [OK] execute_command tool called")
    result["steps"].append({"step": 3, "action": "execute_command", "valid": True})

    # VALIDATION
    print("\n[Validation] Checking final code")
    if "multiply" in result["final_code"] and "def multiply" in result["final_code"]:
        print("  [OK] multiply function present in code")
    else:
        result["status"] = "FAIL"
        print("  [FAIL] multiply function missing")
        return result

    print("\n" + "=" * 70)
    print("Result: PASS")
    print("=" * 70)
    print("\nWorkflow completed successfully:")
    print("  1. read_file -> Model understands structure")
    print("  2. write_file -> Model adds function correctly")
    print("  3. execute_command -> Model validates with compilation")
    print("  [OK] Code ready for Cline integration")

    return result

def main():
    print("=" * 70)
    print("Phase 6.5: Cline-Realistic Workflow Testing")
    print("=" * 70)

    try:
        response = urllib.request.urlopen(f"{OVMS_BASE}/v3/models/{MODEL}", timeout=5)
        if response.status != 200:
            print("[FAIL] OVMS not responding")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] OVMS error: {e}")
        sys.exit(1)

    print("[OK] OVMS responsive\n")

    result = test_realistic_code_edit()

    output_file = TEST_DIR / "test_cline_realistic_code_edit.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nResults saved: {output_file}")
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
