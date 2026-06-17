#!/usr/bin/env python3
"""
Realistic Cline-like flow test: User → Model → Tool Call → Tool Result → Model Continuation
"""

import json
import urllib.request
import sys

OVMS_BASE = "http://localhost:9000"
MODEL = "Qwen3-Coder-30B-A3B-Instruct-int4-ov"

def post_json(url, data):
    """POST JSON to OVMS."""
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

def get_tools():
    """Available tools."""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read file content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"}
                    },
                    "required": ["path"]
                }
            }
        }
    ]

def simulate_tool_execution(tool_name, args):
    """Simulate tool execution, return result."""
    if tool_name == "read_file":
        path = args.get("path", "")
        # Simulate file content
        if "test.txt" in path:
            return "Hello from test.txt"
        elif "data.json" in path:
            return '{"data": "sample"}'
        else:
            return f"File not found: {path}"
    return "Unknown tool"

def test_cline_flow():
    """Test realistic Cline flow."""
    print("=" * 70)
    print("Cline Flow Test: User → Tool Call → Tool Result → Continuation")
    print("=" * 70)

    # Step 1: User asks model to read file
    print("\n[Step 1] User Request")
    user_message = "Please read /tmp/test_data/test.txt and tell me what it says"
    print(f"  User: {user_message}")

    messages = [{"role": "user", "content": user_message}]

    # Step 2: Get tool call from model
    print("\n[Step 2] Model Response with Tool Call")
    response = post_json(
        f"{OVMS_BASE}/v3/chat/completions",
        {
            "model": MODEL,
            "messages": messages,
            "tools": get_tools(),
            "max_tokens": 512
        }
    )

    if "error" in response:
        print(f"  [FAIL] API error: {response['error']}")
        return False

    tool_calls = response["choices"][0]["message"].get("tool_calls", [])
    if not tool_calls:
        print("  [FAIL] Model didn't call tool")
        return False

    tool_call = tool_calls[0]["function"]
    tool_name = tool_call["name"]
    tool_args = json.loads(tool_call["arguments"])

    print(f"  Model called: {tool_name}({tool_args})")

    # Validate
    if tool_name != "read_file":
        print(f"  [FAIL] Wrong tool: {tool_name}")
        return False

    if "path" not in tool_args:
        print(f"  [FAIL] Missing path parameter")
        return False

    # Step 3: Simulate tool execution
    print("\n[Step 3] Execute Tool")
    tool_result = simulate_tool_execution(tool_name, tool_args)
    print(f"  Tool result: {repr(tool_result[:50])}")

    # Step 4: Model continues with tool result
    print("\n[Step 4] Model Continues with Tool Result")
    messages.append({
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "type": "function",
                "id": tool_calls[0]["id"],
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(tool_args)
                }
            }
        ]
    })
    messages.append({
        "role": "tool",
        "content": tool_result,
        "tool_call_id": tool_calls[0]["id"]
    })

    # Get continuation
    continuation = post_json(
        f"{OVMS_BASE}/v3/chat/completions",
        {
            "model": MODEL,
            "messages": messages,
            "tools": get_tools(),
            "max_tokens": 512
        }
    )

    if "error" in continuation:
        print(f"  [FAIL] Continuation error: {continuation['error']}")
        return False

    final_response = continuation["choices"][0]["message"].get("content", "")
    if not final_response:
        print("  [FAIL] No continuation response")
        return False

    print(f"  Model response: {final_response[:100]}")

    # Step 5: Validate entire flow
    print("\n[Step 5] Validation")
    checks = [
        ("Tool called", tool_name == "read_file"),
        ("Path provided", "path" in tool_args),
        ("Tool result returned", len(tool_result) > 0),
        ("Model continued", len(final_response) > 0),
        ("Response makes sense", "test.txt" in final_response.lower() or "hello" in final_response.lower() or "file" in final_response.lower())
    ]

    all_pass = True
    for check_name, check_result in checks:
        status = "[OK]" if check_result else "[FAIL]"
        print(f"  {status} {check_name}")
        if not check_result:
            all_pass = False

    print("\n" + "=" * 70)
    if all_pass:
        print("RESULT: PASS — Cline flow works correctly")
        return True
    else:
        print("RESULT: FAIL — Some checks failed")
        return False

if __name__ == "__main__":
    success = test_cline_flow()
    sys.exit(0 if success else 1)
