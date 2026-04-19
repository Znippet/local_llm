# Start llama-server mit OpenVINO GPU
# Workaround fuer Lunar Lake GPU Warmup Shape-Incompatibility

$env:GGML_OPENVINO_DEVICE = "GPU"
$env:GGML_OPENVINO_STATEFUL_EXECUTION = "1"

Write-Host ""
Write-Host "========== llama-server (OpenVINO GPU) ==========" -ForegroundColor Cyan
Write-Host "Port: 8080"
Write-Host "Model: Qwen3-Coder-30B-A3B-Instruct-IQ4_XS"
Write-Host "Device: GPU (Lunar Lake iGPU)"
Write-Host ""
Write-Host "Startup dauert 1-2 Min (Warmup skipped)..."
Write-Host ""

Write-Host "Environment Variables:" -ForegroundColor Yellow
Write-Host "  GGML_OPENVINO_DEVICE=$($env:GGML_OPENVINO_DEVICE)"
Write-Host "  GGML_OPENVINO_STATEFUL_EXECUTION=$($env:GGML_OPENVINO_STATEFUL_EXECUTION)"
Write-Host ""

& "C:\LLM\openvino_sdk\setupvars.bat" | Out-Null


& "C:\LLM\llama.cpp\build\ReleaseOV\bin\llama-server.exe" `
  --model "C:\LLM\models\gguf\Qwen3-Coder-30B-A3B-Instruct-IQ4_XS.gguf" `
  --port 9000 `
  --ctx-size 2048 `
  --batch-size 128 `
  --ubatch-size 64 `
  --jinja `

