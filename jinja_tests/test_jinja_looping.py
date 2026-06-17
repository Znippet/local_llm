#!/usr/bin/env python3
"""Phase 6.5 Test: Looping Detection"""

import json
import urllib.request
import time
import sys
from pathlib import Path
from collections import defaultdict

OVMS_BASE = "http://localhost:9000"
MODEL = "qwen3-coder-30b-a3b-instruct-int4-ov"
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

def extract_tool_calls(response_json):
    tool_calls = []
    try:
        if "choices" in response_json and response_json["choices"]:
            message = response_json["choices"][0].get("message", {})
            tcs = message.get("tool_calls", [])
            for tc in tcs:
                tool_name = tc.get("function", {}).get("name")
                args_str = tc.get("function", {}).get("arguments", "")
                try:
                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
                except:
                    args = {}
                tool_calls.append({"name": tool_name, "args": args})
    except:
        pass
    return tool_calls

def simulate_multiturn_conversation(user_prompt, max_turns=10):
    result = {
        "user_prompt": user_prompt,
        "turns": [],
        "tool_call_history": [],
        "loop_detected": False,
        "loop_reason": None
    }

    messages = [{"role": "user", "content": user_prompt}]
    tool_call_counter = defaultdict(int)
    last_tools = []

    for turn_num in range(max_turns):
        payload = {
            "model": MODEL,
            "messages": messages,
            "tools": load_tools_schema(),
            "temperature": 0.7,
            "max_tokens": 256
        }

        response = post_json(f"{OVMS_BASE}/v3/chat/completions", payload)
        if "error" in response:
            result["turns"].append({"turn": turn_num, "error": response["error"]})
            break

        tool_calls = extract_tool_calls(response)
        result["turns"].append({"turn": turn_num, "tool_calls": tool_calls})

        if not tool_calls:
            break

        # Track patterns
        for tc in tool_calls:
            sig = f"{tc['name']}({json.dumps(tc['args'], sort_keys=True)})"
            tool_call_counter[sig] += 1
            result["tool_call_history"].append(sig)

        # Loop detection
        for sig, count in tool_call_counter.items():
            if count >= 4:
                result["loop_detected"] = True
                result["loop_reason"] = f"Repeated {count} times"
                return result

        current_sigs = [f"{tc['name']}({json.dumps(tc['args'], sort_keys=True)})" for tc in tool_calls]
        if current_sigs == last_tools and turn_num > 1:
            result["loop_detected"] = True
            result["loop_reason"] = "Identical consecutive turns"
            return result

        last_tools = current_sigs

        if turn_num >= 8:
            result["loop_detected"] = True
            result["loop_reason"] = f"Long conversation ({turn_num} turns)"
            return result

        assistant_msg = response.get("choices", [{}])[0].get("message", {})
        messages.append(assistant_msg)

        for tc in tool_calls:
            messages.append({
                "role": "tool",
                "tool_call_id": f"mock_{turn_num}",
                "content": f"Mock result for {tc['name']}"
            })

    return result

def main():
    print("=" * 70)
    print("Phase 6.5: Looping Detection Tests")
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

    print("Running looping detection tests...")
    print("\n[TC1] Looping in search_files")
    r1 = simulate_multiturn_conversation("Find all Python files. Keep searching until 100 files found.")
    results.append(r1)
    print(f"  Turns: {len(r1['turns'])}, Loop: {r1['loop_detected']}")
    time.sleep(1)

    print("\n[TC2] Looping in execute_command")
    r2 = simulate_multiturn_conversation("Run echo test command repeatedly to verify")
    results.append(r2)
    print(f"  Turns: {len(r2['turns'])}, Loop: {r2['loop_detected']}")
    time.sleep(1)

    print("\n[TC3] Normal multi-turn (should NOT loop)")
    r3 = simulate_multiturn_conversation("(1) read file, (2) add comment, (3) verify")
    results.append(r3)
    print(f"  Turns: {len(r3['turns'])}, Loop: {r3['loop_detected']}")

    print("\n" + "=" * 70)
    print("Looping Detection Summary")
    print("=" * 70)

    loops = sum(1 for r in results if r.get("loop_detected"))
    print(f"\nTests: {len(results)}")
    print(f"Loops detected: {loops}")

    output_file = TEST_DIR / "test_jinja_looping.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved: {output_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
