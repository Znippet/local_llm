In C:\LLM:

## Selbstgenerieren: Install OpenVINO 2025.4

https://docs.openvino.ai/2025/get-started.html

## Deploying Model Server

https://docs.openvino.ai/2025/model-server/ovms_docs_deploying_server_baremetal.html

### Download

```
curl -L https://github.com/openvinotoolkit/model_server/releases/download/v2025.4.1/ovms_windows_python_off.zip -o ovms.zip
tar -xf ovms.zip
```

### Run setupvars script to set required environment variables.

```
.\ovms\setupvars.ps1
```

## Visual Studio Code Local Assistant

https://docs.openvino.ai/2025/model-server/ovms_demos_code_completion_vsc.html

### Download Code Chat/Edit MOdel

https://huggingface.co/OpenVINO/Qwen3-Coder-30B-A3B-Instruct-int4-ov

Add Jinja (nötig?)

```
curl -L -o models/Qwen3-Coder-30B-A3B-Instruct-int4-ov/chat_template.jinja https://raw.githubusercontent.com/openvinotoolkit/model_server/refs/heads/releases/2025/4/extras/chat_template_examples/chat_template_qwen3coder_instruct.jinja
```

Add a config for the model:

```
.\ovms\ovms.exe --add_to_config --config_path models/myqwencoder.config.json --model_name Qwen3-Coder-30B-A3B-Instruct-int4-ov --model_path models/Qwen3-Coder-30B-A3B-Instruct-int4-ov
```

Remove model/ path from config, it is duplicate.

_Careful_: OVMS will start all LLM's in the config. Add only one per config.

### Set Up Server

Run OpenVINO Model Server with the model in the config

```
.\\ovms\\ovms --rest_port 9000 --config_path ./models/myqwencoder.config.json
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
  - name: OVMS Qwen/Qwen3-Coder-30B-A3B
    provider: openai
    model: Qwen/Qwen3-Coder-30B-A3B-Instruct
    apiKey: unused
    apiBase: http://localhost:8000/v3
    roles:
      - chat
      - edit
      - apply
      - autocomplete
    capabilities:
      - tool_use
    requestOptions:
      extraBodyProperties:
        chat_template_kwargs:
          enable_thinking: false

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
