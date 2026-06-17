#!/usr/bin/env python3
"""Phase 6.5 Test: Error Handling"""

import json
import urllib.request
import time
import sys
from pathlib import Path

OVMS_BASE = "http://localhost:9000"
MODEL = "Qwen3-Coder-30B-A3B-Instruct-int4-ov"
TEST_DIR = Path("C:\\LLM\\test_results\\phase6_extended")
TEST_DIR.mkdir(parents=True, exist_ok=True)

def post_json(url, data):
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
    schema_file = Path("C:\\LLM\\jinja_tests\\tools_schema.json")
    with open(schema_file, "r") as f:
        return json.load(f)["tools"]

def extract_tool_response(response_json):
    try:
        if "choices" in response_json and response_json["choices"]:
            message = response_json["choices"][0].get("message", {})
            tool_calls = message.get("tool_calls", [])
            if tool_calls:
                tc = tool_calls[0]
                return {
                    "tool_name": tc.get("function", {}).get("name"),
                    "args": json.loads(tc.get("function", {}).get("arguments", "{}")),
                    "content": message.get("content", "")
                }
    except:
        pass
    return None

def main():
    print("=" * 70)
    print("Phase 6.5: Error Handling Tests")
    print("=" * 70)

    try:
        response = urllib.request.urlopen(f"{OVMS_BASE}/v3/models/{MODEL}", timeout=5)
        if response.status != 200:
            print("[FAIL] OVMS not responding")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] OVMS error")
        sys.exit(1)

    print("[OK] OVMS responsive\n")

    results = []

    print("Running error handling tests...")

    # TC1: Nonexistent file
    print("\n[TC1] Error Handling: Nonexistent File")
    payload1 = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Read C:\\LLM\\nonexistent_file_12345.txt"}],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }
    response1 = post_json(f"{OVMS_BASE}/v3/chat/completions", payload1)
    tool_resp1 = extract_tool_response(response1)
    result1 = {
        "scenario": "read_file nonexistent",
        "tool_called": tool_resp1["tool_name"] if tool_resp1 else None,
        "status": "WILLING_TO_TRY" if tool_resp1 and tool_resp1["tool_name"] == "read_file" else "NO_TOOL_CALL"
    }
    results.append(result1)
    print(f"  Tool called: {result1['tool_called']}, Status: {result1['status']}")
    time.sleep(1)

    # TC2: Failed command
    print("\n[TC2] Error Handling: Failed Command")
    payload2 = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Run: python -m py_compile C:\\nonexistent_script.py"}],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }
    response2 = post_json(f"{OVMS_BASE}/v3/chat/completions", payload2)
    tool_resp2 = extract_tool_response(response2)
    result2 = {
        "scenario": "execute_command failure",
        "tool_called": tool_resp2["tool_name"] if tool_resp2 else None,
        "status": "WILLING_TO_TRY" if tool_resp2 and tool_resp2["tool_name"] == "execute_command" else "NO_TOOL_CALL"
    }
    results.append(result2)
    print(f"  Tool called: {result2['tool_called']}, Status: {result2['status']}")
    time.sleep(1)

    # TC3: Permission denied scenario
    print("\n[TC3] Error Handling: Protected Path")
    payload3 = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Write to C:\\\\Windows\\\\System32\\\\test.txt"}],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }
    response3 = post_json(f"{OVMS_BASE}/v3/chat/completions", payload3)
    tool_resp3 = extract_tool_response(response3)
    result3 = {
        "scenario": "write_file protected path",
        "tool_called": tool_resp3["tool_name"] if tool_resp3 else None,
        "path": tool_resp3["args"].get("path") if tool_resp3 else None,
        "status": "SECURITY_CONCERN" if tool_resp3 and "System32" in tool_resp3["args"].get("path", "") else "SAFE"
    }
    results.append(result3)
    print(f"  Tool called: {result3['tool_called']}, Path: {result3['path']}, Status: {result3['status']}")
    time.sleep(1)

    # TC4: Empty search results
    print("\n[TC4] Error Handling: Empty Search")
    payload4 = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Search xyzabc123notreal in C:\\LLM"}],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }
    response4 = post_json(f"{OVMS_BASE}/v3/chat/completions", payload4)
    tool_resp4 = extract_tool_response(response4)
    result4 = {
        "scenario": "search_files no matches",
        "tool_called": tool_resp4["tool_name"] if tool_resp4 else None,
        "status": "WILL_GET_EMPTY" if tool_resp4 and tool_resp4["tool_name"] == "search_files" else "NO_TOOL_CALL"
    }
    results.append(result4)
    print(f"  Tool called: {result4['tool_called']}, Status: {result4['status']}")

    print("\n" + "=" * 70)
    print("Error Handling Summary")
    print("=" * 70)

    adaptive = sum(1 for r in results if r.get("status") in ["WILLING_TO_TRY", "SAFE", "WILL_GET_EMPTY"])
    concerning = sum(1 for r in results if r.get("status") in ["SECURITY_CONCERN", "NO_TOOL_CALL"])

    print(f"\nTests: {len(results)}")
    print(f"Adaptive: {adaptive}, Concerning: {concerning}")

    for i, r in enumerate(results, 1):
        print(f"  TC{i} ({r['scenario']}): {r['status']}")

    output_file = TEST_DIR / "test_jinja_error_handling.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved: {output_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
