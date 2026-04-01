In C:\LLM:

## Selbstgenerieren: Install OpenVINO 2025.4

https://docs.openvino.ai/2026/get-started.html

## Deploying Model Server

https://docs.openvino.ai/2026/model-server/ovms_docs_deploying_server_baremetal.html

### Download

```
curl -L https://github.com/openvinotoolkit/model_server/releases/download/v2026.0/ovms_windows_python_off.zip -o ovms.zip
tar -xf ovms.zip
```

### Run setupvars script to set required environment variables.

```
.\ovms\setupvars.ps1
```

## Visual Studio Code Local Assistant

https://docs.openvino.ai/2026/model-server/ovms_demos_code_completion_vsc.html

### Download Code Chat/Edit Model if necessary and run the Server

```
mkdir .\models
set MOE_USE_MICRO_GEMM_PREFILL=0  # temporary workaround to improve accuracy with long context
ovms --model_repository_path .\models --source_model OpenVINO/Qwen3-Coder-30B-A3B-Instruct-int4-ov --task text_generation --target_device GPU --tool_parser qwen3coder --rest_port 8000 --cache_dir .ovcache --model_name Qwen3-Coder-30B-A3B-Instruct-int4-ov
```

### Set Up Visual Studio Code

Continue Plugin: https://www.continue.dev/

Point Continue plugin to our OpenVINO Model Server instance:

config.yaml:

```
name: Local Assistant
version: 1.0.0
schema: v1
models:
  - name: OVMS Qwen3-Coder-30B-A3B-Instruct-int4-ov
    provider: openai
    model: Qwen3-Coder-30B-A3B-Instruct-int4-ov
    apiKey: unused
    apiBase: http://localhost:8000/v3
    roles:
      - chat
      - edit
      - apply
      - autocomplete
    capabilities:
      - tool_use
    autocompleteOptions:
      maxPromptTokens: 500
      debounceDelay: 124
      modelTimeout: 400
      onlyMyCode: true
      useCache: true
context:
  - provider: code
  - provider: docs
  - provider: diff
  - provider: terminal
  - provider: problems
  - provider: folder
  - provider: codebase
```

## Lösungen für Tooling

Lösungen für OpenCode + OVMS
OVMS-Parser: Nutze tool_parser: qwen3coder in config.json – OVMS extrahiert XML zu JSON (experimental, aber Doku-empfohlen).

Custom Provider: In OpenCode config.json: "response_format": {"type": "json_object"} erzwingen, kombiniert mit OVMS JSON-Mode (add --json_mode true).

Alternative: Hermes3/Qwen2.5-Coder-14B (JSON-nativ) oder Post-Processing-Script (XML→JSON).

```

```
