ovms --model_repository_path c:\LLM\models ^
  --source_model OpenVINO/Qwen3.6-35B-A3B-int4-ov ^
  --task text_generation ^
  --target_device AUTO ^
  --rest_port 9000 ^
  --cache_dir .ovcache ^
  --model_name qwen3.6-35b-a3b-int4-ov