ovms.exe ^
  --rest_port 9000 ^
  --source_model OpenVINO/Qwen3-8B-int4-ov ^
  --model_repository_path models ^
  --tool_parser hermes3 ^
  --reasoning_parser qwen3 ^
  --target_device GPU ^
  --cache_size 2 ^
  --task text_generation