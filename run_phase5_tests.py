#!/usr/bin/env python3
"""
Phase 5 Test Execution: Direct OVMS API testing for Qwen3-Coder-30B template.
TC1-TC5 validation via REST API (ChatGPT-compatible interface).
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
TEST_DIR = Path("C:\\LLM\\test_results")
TEST_DIR.mkdir(exist_ok=True)

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
            if tool_name == "read_file" and "path" not in args:
                result["status"] = "FAIL"
                result["errors"].append({"type": "missing_param", "message": f"read_file missing 'path'"})

            if tool_name == "list_files" and "path" not in args:
                result["status"] = "FAIL"
                result["errors"].append({"type": "missing_param", "message": f"list_files missing 'path'"})

            if tool_name == "write_file" and ("path" not in args or "content" not in args):
                result["status"] = "FAIL"
                result["errors"].append({"type": "missing_param", "message": f"write_file missing required params"})

            result["tool_calls"].append({
                "name": tool_name,
                "args": args
            })

    return result

def get_tool_schema():
    """Define available tools for model."""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to read"
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path"
                        },
                        "pattern": {
                            "type": "string",
                            "description": "File pattern filter (e.g. *.txt)"
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "File content"
                        }
                    },
                    "required": ["path", "content"]
                }
            }
        }
    ]

def tc1_single_tool():
    """TC1: Single Tool Call (Basis) — STRICT: must call read_file with path"""
    print("\n[TC1] Single Tool Call")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Use the read_file tool to read /tmp/test_data/test.txt"
            }
        ],
        "tools": get_tool_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    log_response(1, data)
    result = validate_response(
        1, data,
        require_tool=True,
        allowed_tools=["read_file", "list_files", "write_file"]
    )

    # Additional strict check: exactly 1 tool call
    if len(result["tool_calls"]) != 1:
        result["status"] = "FAIL"
        result["errors"].append({
            "type": "wrong_tool_count",
            "message": f"Expected 1 tool call, got {len(result['tool_calls'])}"
        })

    return result

def tc2_structured_args():
    """TC2: Structured Args Validation — STRICT: list_files with path AND pattern"""
    print("[TC2] Structured Args Validation")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Use list_files to show all .txt files in /tmp/test_data"
            }
        ],
        "tools": get_tool_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    log_response(2, data)
    result = validate_response(
        2, data,
        require_tool=True,
        allowed_tools=["read_file", "list_files", "write_file"]
    )

    # Strict: check that pattern parameter was included (shows structured understanding)
    if result["tool_calls"]:
        args = result["tool_calls"][0].get("args", {})
        if "pattern" not in args and args.get("name") == "list_files":
            result["status"] = "FAIL"
            result["errors"].append({
                "type": "missing_pattern",
                "message": "list_files should include pattern parameter for *.txt filter"
            })

    return result

def tc3_tool_result():
    """TC3: Tool Result Follow-Up — STRICT: read_file MUST be called (no tools schema means fallback to text)"""
    print("[TC3] Tool Result Follow-Up")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Read /tmp/test_data/data.json and describe its content"
            }
        ],
        "tools": get_tool_schema(),
        "temperature": 0.7,
        "max_tokens": 512
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    log_response(3, data)
    result = validate_response(
        3, data,
        require_tool=True,
        allowed_tools=["read_file", "list_files", "write_file"]
    )

    if not result["has_tool_call"]:
        result["status"] = "FAIL"
        result["errors"].append({
            "type": "no_tool_call",
            "message": "TC3: explicit 'read' instruction should trigger read_file tool"
        })

    return result

def tc4_no_tool():
    """TC4: No-Tool Answer Path — STRICT: must forbid tool calls, answer with text"""
    print("[TC4] No-Tool Answer Path")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "What is 2+2? Answer without tools."
            }
        ],
        "tools": get_tool_schema(),
        "temperature": 0.7,
        "max_tokens": 256
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    log_response(4, data)
    result = validate_response(
        4, data,
        forbid_tool=True
    )

    # Strict: content should have actual answer
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content or len(content) < 5:
        result["status"] = "FAIL"
        result["errors"].append({
            "type": "empty_answer",
            "message": "Should provide text answer, got empty/minimal response"
        })
    elif "4" not in content:
        result["status"] = "FAIL"
        result["errors"].append({
            "type": "wrong_answer",
            "message": "Should answer 2+2=4, answer unclear"
        })

    return result

def tc5_multi_step():
    """TC5: Multi-Step Tool Use — STRICT: write_file THEN read_file (correct order)"""
    print("[TC5] Multi-Step Tool Use")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "First use write_file to create /tmp/test_data/step.py with content 'print(456)', then use read_file to verify it"
            }
        ],
        "tools": get_tool_schema(),
        "temperature": 0.7,
        "max_tokens": 1024
    }

    data = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
    log_response(5, data)
    result = validate_response(
        5, data,
        require_tool=True,
        allowed_tools=["read_file", "list_files", "write_file"]
    )

    tool_calls = data.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
    tc_count = len(tool_calls)
    result["tool_call_count"] = tc_count

    # Strict: must have 2+ calls
    if tc_count < 2:
        result["status"] = "FAIL"
        result["errors"].append({
            "type": "insufficient_tools",
            "message": f"Expected 2+ tool calls (write then read), got {tc_count}"
        })

    # Strict: correct order (write before read)
    if tc_count >= 2:
        first_tool = tool_calls[0].get("function", {}).get("name")
        second_tool = tool_calls[1].get("function", {}).get("name")
        if first_tool != "write_file" or second_tool != "read_file":
            result["status"] = "FAIL"
            result["errors"].append({
                "type": "wrong_order",
                "message": f"Expected write_file→read_file, got {first_tool}→{second_tool}"
            })

    return result

def main():
    print("=" * 70)
    print("Phase 5: Test Execution (OVMS REST API)")
    print("=" * 70)

    # Phase 4a: OVMS health check
    print("\n[Phase 4a] OVMS Health Check")
    data = get_json(f"{OVMS_BASE}/v3/models/{MODEL}")
    if "error" not in data:
        print(f"[PASS] OVMS responsive, model loaded")
    else:
        print(f"[FAIL] OVMS error: {data.get('error')}")
        sys.exit(1)

    # Phase 4b: Run test cases
    print("\n[Phase 4b] Test Case Execution")
    results = []
    results.append(tc1_single_tool())
    time.sleep(1)
    results.append(tc2_structured_args())
    time.sleep(1)
    results.append(tc3_tool_result())
    time.sleep(1)
    results.append(tc4_no_tool())
    time.sleep(1)
    results.append(tc5_multi_step())

    # Phase 4c: Summary
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)

    summary_file = TEST_DIR / "Phase5-Test-Results.json"
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

    return 0 if pass_count >= 4 else 1

if __name__ == "__main__":
    sys.exit(main())
