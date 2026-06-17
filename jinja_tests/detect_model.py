#!/usr/bin/env python3
"""
Detect which Qwen3 model is currently loaded in OVMS.
Used by test scripts to adapt to 30B or 35B model.
"""

import urllib.request
import json
from pathlib import Path

OVMS_BASE = "http://localhost:9000"

def detect_model():
    """
    Query OVMS to determine which model is loaded.
    Returns: (model_name, is_35b) tuple
    """
    # Try to query OVMS status
    try:
        url = f"{OVMS_BASE}/v3/models"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get('model_index', {})

            # Check for 35B model
            if 'Qwen3.6-35B-A3B-int4-ov' in models:
                return "Qwen3.6-35B-A3B-int4-ov", True

            # Check for 30B model
            if 'Qwen3-Coder-30B-A3B-Instruct-int4-ov' in models:
                return "Qwen3-Coder-30B-A3B-Instruct-int4-ov", False

    except Exception as e:
        print(f"[WARN] Could not detect model from OVMS: {e}")
        print(f"[INFO] Falling back to filesystem check...")

    # Fallback: Check filesystem
    model_dir = Path("C:\\LLM\\models\\OpenVINO")

    if (model_dir / "Qwen3.6-35B-A3B-int4-ov").exists():
        return "Qwen3.6-35B-A3B-int4-ov", True

    if (model_dir / "Qwen3-Coder-30B-A3B-Instruct-int4-ov").exists():
        return "Qwen3-Coder-30B-A3B-Instruct-int4-ov", False

    # Fallback default
    return "Qwen3-Coder-30B-A3B-Instruct-int4-ov", False

if __name__ == "__main__":
    model_name, is_35b = detect_model()
    print(f"Detected model: {model_name}")
    print(f"Is 35B: {is_35b}")
