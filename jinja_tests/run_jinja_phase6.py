#!/usr/bin/env python3
"""
Phase 6 Test Execution: Extended Cline Tools for Qwen3-Coder-30B template.
TC6-TC9 validation: execute_command, search_files, web_search, list_directory_tree.
Uses built-in urllib (no external dependencies).
"""

import json
import urllib.request
import urllib.error
import time
import sys
from pathlib import Path

# OVMS endpoint
OVMS_BASE = "http://localhost:9000"
MODEL = "qwen3-coder-30b-a3b-instruct-int4-ov"

# Test output directory
TEST_DIR = Path("C:\\LLM\\test_results\\phase6_extended_tools")
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

def get_json(url):
    """GET JSON from endpoint."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        return {"error": str(e)}

def log_response(tc_num, response_json):
    """Log raw API response."""
    log_file = TEST_DIR / f"test_output_tc{tc_num}.json"
    with open(log_file, "w", encoding='utf-8') as f:
        json.dump(response_json, f, indent=2)
    print(f"  [OK] Logged: {log_file.name}")
    return log_file

def load_tools_schema():
    """Load tools from central schema file."""
    schema_file = Path("C:\\LLM\\jinja_tests\\tools_schema.json")
    with open(schema_file, "r") as f:
        data = json.load(f)
    return data["tools"]

def validate_response(tc_num, response_json, require_tool=False, forbid_tool=False, allowed_tools=None):
    """Strict validation: tool calls, JSON, required params."""
    result = {
        "tc": tc_num,
        "status": "PASS",
        "errors": [],
        "tool_calls": [],
        "has_tool_call": False
    }

    # API errors
    if "error" in response_json:
        result["status"] = "FAIL"
        result["errors"].append({"type": "api_error", "message": str(response_json.get("error"))})
        return result

    # Response structure
    if "choices" not in response_json or not response_json["choices"]:
        result["status"] = "FAIL"
        result["errors"].append({"type": "no_choices", "message": "Empty response"})
        return result

    message = response_json["choices"][0].get("message", {})
    tool_calls = message.get("tool_calls", [])

    # ===== STRICT VALIDATION =====

    # 1. Tool calls present/absent per requirement
    if require_tool and not tool_calls:
        result["status"] = "FAIL"
        result["errors"].append({"type": "no_tool_call", "message": "Required tool call missing"})
        return result

    if forbid_tool and tool_calls:
        result["status"] = "FAIL"
        result["errors"].append({"type": "unexpected_tool_call", "message": f"Tool call not allowed, got {len(tool_calls)}"})
        return result

    # 2. Validate each tool call
    if tool_calls:
        result["has_tool_call"] = True
        for idx, tc in enumerate(tool_calls):
            tool_name = tc.get("function", {}).get("name")
            args_str = tc.get("function", {}).get("arguments", "")

            # 2a. Tool name in allowed list
            if allowed_tools and tool_name not in allowed_tools:
                result["status"] = "FAIL"
                result["errors"].append({
                    "type": "invalid_tool",
                    "message": f"Tool '{tool_name}' not in allowed: {allowed_tools}"
                })

            # 2b. Arguments must be valid JSON
            try:
                args = json.loads(args_str) if isinstance(args_str, str) else args_str
                if not isinstance(args, dict):
                    raise ValueError("Args not dict")
            except (json.JSONDecodeError, ValueError) as e:
                result["status"] = "FAIL"
                result["errors"].append({
                    "type": "invalid_json_args",
                    "message": f"Tool {tool_name}: args not valid JSON: {str(e)[:50]}"
                })
                continue

            # 2c. Validate required params for known tools
            if tool_name == "execute_command" and "command" not in args:
                result["status"] = "FAIL"
                result["errors"].append({"type": "missing_param", "message": f"execute_command missing 'command'"})

            if tool_name == "search_files" and ("pattern" not in args or "path" not in args):
                result["status"] = "FAIL"
                result["errors"].append({"type": "missing_param", "message": f"search_files missing 'pattern' or 'path'"})

            if tool_name == "web_search" and "query" not in args:
                result["status"] = "FAIL"
                result["errors"].append({"type": "missing_param", "message": f"web_search missing 'query'"})

            if tool_name == "list_directory_tree" and "path" not in args:
                result["status"] = "FAIL"
                result["errors"].append({"type": "missing_param", "message": f"list_directory_tree missing 'path'"})

            result["tool_calls"].append({
                "name": tool_name,
                "args": args
            })

    return result

def tc6_execute_command():
    """TC6: Execute Command — STRICT: must call execute_command with command"""
    print("\n[TC6] Execute Command")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Use execute_command to run 'echo hello' and show the output"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    log_response(6, data)
    result = validate_response(
        6, data,
        require_tool=True,
        allowed_tools=["execute_command", "search_files", "web_search", "list_directory_tree"]
    )

    # Strict: exactly 1 tool call
    if len(result["tool_calls"]) != 1:
        result["status"] = "FAIL"
        result["errors"].append({
            "type": "wrong_tool_count",
            "message": f"Expected 1 tool call, got {len(result['tool_calls'])}"
        })

    # Verify tool name
    if result["tool_calls"] and result["tool_calls"][0]["name"] != "execute_command":
        result["status"] = "FAIL"
        result["errors"].append({
            "type": "wrong_tool_name",
            "message": f"Expected execute_command, got {result['tool_calls'][0]['name']}"
        })

    return result

def tc7_search_files():
    """TC7: Search Files — STRICT: search_files with pattern AND path"""
    print("[TC7] Search Files")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Use search_files to find 'TODO' comments in C:\\\\LLM directory"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    log_response(7, data)
    result = validate_response(
        7, data,
        require_tool=True,
        allowed_tools=["execute_command", "search_files", "web_search", "list_directory_tree"]
    )

    # Verify tool name
    if result["tool_calls"] and result["tool_calls"][0]["name"] != "search_files":
        result["status"] = "FAIL"
        result["errors"].append({
            "type": "wrong_tool_name",
            "message": f"Expected search_files, got {result['tool_calls'][0]['name']}"
        })

    # Check required params
    if result["tool_calls"]:
        args = result["tool_calls"][0].get("args", {})
        if "pattern" not in args or "path" not in args:
            result["status"] = "FAIL"
            result["errors"].append({
                "type": "missing_params",
                "message": f"search_files must have 'pattern' and 'path', got {list(args.keys())}"
            })

    return result

def tc8_web_search():
    """TC8: Web Search — STRICT: web_search with query"""
    print("[TC8] Web Search")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Use web_search to find information about Qwen3-Coder documentation"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    log_response(8, data)
    result = validate_response(
        8, data,
        require_tool=True,
        allowed_tools=["execute_command", "search_files", "web_search", "list_directory_tree"]
    )

    # Verify tool name
    if result["tool_calls"] and result["tool_calls"][0]["name"] != "web_search":
        result["status"] = "FAIL"
        result["errors"].append({
            "type": "wrong_tool_name",
            "message": f"Expected web_search, got {result['tool_calls'][0]['name']}"
        })

    # Check required params
    if result["tool_calls"]:
        args = result["tool_calls"][0].get("args", {})
        if "query" not in args:
            result["status"] = "FAIL"
            result["errors"].append({
                "type": "missing_param",
                "message": f"web_search must have 'query', got {list(args.keys())}"
            })

    return result

def tc9_list_directory_tree():
    """TC9: List Directory Tree — STRICT: list_directory_tree with path"""
    print("[TC9] List Directory Tree")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Use list_directory_tree to show the structure of C:\\\\LLM with max_depth 2"
            }
        ],
        "tools": load_tools_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    log_response(9, data)
    result = validate_response(
        9, data,
        require_tool=True,
        allowed_tools=["execute_command", "search_files", "web_search", "list_directory_tree"]
    )

    # Verify tool name
    if result["tool_calls"] and result["tool_calls"][0]["name"] != "list_directory_tree":
        result["status"] = "FAIL"
        result["errors"].append({
            "type": "wrong_tool_name",
            "message": f"Expected list_directory_tree, got {result['tool_calls'][0]['name']}"
        })

    # Check required params
    if result["tool_calls"]:
        args = result["tool_calls"][0].get("args", {})
        if "path" not in args:
            result["status"] = "FAIL"
            result["errors"].append({
                "type": "missing_param",
                "message": f"list_directory_tree must have 'path', got {list(args.keys())}"
            })

    return result

def main():
    print("=" * 70)
    print("Phase 6: Extended Cline Tools Test Execution (OVMS REST API)")
    print("=" * 70)

    # Phase 6a: OVMS health check
    print("\n[Phase 6a] OVMS Health Check")
    data = get_json(f"{OVMS_BASE}/v3/models/{MODEL}")
    if "error" not in data:
        print(f"[PASS] OVMS responsive, model loaded")
    else:
        print(f"[FAIL] OVMS error: {data.get('error')}")
        sys.exit(1)

    # Phase 6b: Run test cases
    print("\n[Phase 6b] Test Case Execution (TC6-TC9)")
    results = []
    results.append(tc6_execute_command())
    time.sleep(1)
    results.append(tc7_search_files())
    time.sleep(1)
    results.append(tc8_web_search())
    time.sleep(1)
    results.append(tc9_list_directory_tree())

    # Phase 6c: Summary
    print("\n" + "=" * 70)
    print("Test Results Summary (Phase 6)")
    print("=" * 70)

    summary_file = TEST_DIR / "Phase6-Test-Results.json"
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2)

    for r in results:
        tc = r.get("tc", "?")
        status = r.get("status", "UNKNOWN")
        errors = len(r.get("errors", []))
        tag = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"{tag} TC{tc}: {status} ({errors} errors)")
        for err in r.get("errors", []):
            print(f"    - {err.get('type')}: {err.get('message', '')}")

    pass_count = sum(1 for r in results if r.get("status") == "PASS")
    total = len(results)
    print(f"\nTotal: {pass_count}/{total} PASS")
    print(f"Results saved: {summary_file}")

    return 0 if pass_count >= 3 else 1

if __name__ == "__main__":
    sys.exit(main())
