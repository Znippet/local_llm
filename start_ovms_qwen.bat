ovms --model_repository_path c:\LLM\models ^
  --source_model OpenVINO/Qwen3-Coder-30B-A3B-Instruct-int4-ov ^
  --task text_generation ^
  --target_device AUTO ^
  --tool_parser qwen3coder ^
  --enable_tool_guided_generation true ^
  --rest_port 9000 ^
  --cache_dir .ovcache ^
  --model_name Qwen3-Coder-30B-A3B-Instruct-int4-ov