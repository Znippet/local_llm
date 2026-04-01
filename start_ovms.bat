set MOE_USE_MICRO_GEMM_PREFILL=0  # temporary workaround to improve accuracy with long context
ovms --model_repository_path .\models --source_model OpenVINO/Qwen3-Coder-30B-A3B-Instruct-int4-ov --task text_generation --target_device GPU --tool_parser qwen3coder --rest_port 8000 --cache_dir .ovcache --model_name Qwen3-Coder-30B-A3B-Instruct-int4-ov
