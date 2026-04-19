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
ovms --model_repository_path .\models --source_model OpenVINO/Qwen3-Coder-30B-A3B-Instruct-int4-ov --task text_generation --target_device GPU --tool_parser qwen3coder --rest_port 9000 --cache_dir .ovcache --model_name Qwen3-Coder-30B-A3B-Instruct-int4-ov --enable_tool_guided_generation true
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
  - name: Qwen3-Coder-30B-A3B-Instruct-int4-ov
    provider: openai
    model: Qwen3-Coder-30B-A3B-Instruct-int4-ov
    apiKey: dummy
    apiBase: http://localhost:9000/v3
    roles:
      - chat
      - edit
      - apply
    capabilities:
      - tool_use

context:
  - provider: code
  - provider: docs
  - provider: diff
  - provider: terminal
  - provider: problems
  - provider: folder
  - provider: codebase
```
