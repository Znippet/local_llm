In C:\LLM:

https://docs.openvino.ai/2026/get-started.html

## Deploying Model Server

Download from  
https://github.com/openvinotoolkit/model_server/releases

```
.\ovms\setupvars.ps1
```

## Visual Studio Code Local Assistant

https://docs.openvino.ai/nightly/model-server/ovms_demos_code_completion_vsc.html

### Download Code Chat/Edit Model if necessary and run the Server

```
mkdir .\models
```

```
ovms --log_level WARNING --model_repository_path c:\LLM\models ^
  --source_model OpenVINO/Qwen3-Coder-30B-A3B-Instruct-int4-ov ^
  --task text_generation ^
  --target_device AUTO ^
  --tool_parser qwen3coder ^
  --enable_tool_guided_generation false ^
  --rest_port 9000 ^
  --cache_dir .ovcache ^
  --model_name qwen3-coder-30b-a3b-instruct-int4-ov
```

Ersetze das jinja-Template, um die Toolbenutzung zu reparieren:

- https://huggingface.co/Qwen/Qwen3.5-35B-A3B/discussions/4

### Set Up Visual Studio Code

Continue Plugin und / oder cli: https://www.continue.dev/

Point Continue plugin to our OpenVINO Model Server instance:

config.yaml:

```
name: Local Assistant
version: 1.0.0
schema: v1

models:
  - name: Local qwen3-coder-30b-a3b-instruct-int4-ov
    provider: openai
    model: qwen3-coder-30b-a3b-instruct-int4-ov # muss == --model_name in OVMS sein
    apiKey: dummy
    apiBase: http://localhost:9000/v3
    roles:
      - chat
      - edit
      - apply
    capabilities:
      - tool_use

    # Sampling / Generierungs-Parameter
    defaultCompletionOptions:
      temperature: 0.7 # Qwen3-Coder-Empfehlung
      topP: 0.8 # Qwen3-Coder-Empfehlung
      maxTokens: 4096
      # Optional, aber gut für lokale Modelle:
      topK: 20 # Qwen3-Coder-Empfehlung
      minP: 0.01 # empfohlen statt 0.0

```
