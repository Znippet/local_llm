# Debug OVMS model loading issue
# Run this to diagnose why responses are empty

Write-Host "=== OVMS Debug Check ===" -ForegroundColor Cyan

# 1. Check OVMS process
Write-Host "`n[1] OVMS Process Status"
$ovms = Get-Process ovms -ErrorAction SilentlyContinue
if ($ovms) {
    Write-Host "✓ OVMS running (PID: $($ovms.Id))" -ForegroundColor Green
} else {
    Write-Host "✗ OVMS not running" -ForegroundColor Red
    Exit 1
}

# 2. Check model files
Write-Host "`n[2] Model Files"
$modelDir = "C:\LLM\models\OpenVINO\Qwen3-Coder-30B-A3B-Instruct-int4-ov"
$files = @(
    "openvino_encoder.xml",
    "openvino_encoder.bin",
    "openvino_decoder.xml",
    "openvino_decoder.bin",
    "openvino_config.json",
    "chat_template.jinja"
)

foreach ($file in $files) {
    $path = Join-Path $modelDir $file
    if (Test-Path $path) {
        $size = (Get-Item $path).Length / 1MB
        Write-Host "✓ $file ($($size.ToString('F1')) MB)" -ForegroundColor Green
    } else {
        Write-Host "✗ $file (missing)" -ForegroundColor Red
    }
}

# 3. Test API endpoint
Write-Host "`n[3] OVMS API Test"
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:9000/v3/models/qwen3-coder-30b-a3b-instruct-int4-ov" -TimeoutSec 5
    if ($resp.StatusCode -eq 200) {
        Write-Host "✓ Model endpoint responsive (HTTP 200)" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Model endpoint error: $_" -ForegroundColor Red
}

# 4. Test chat endpoint (check if it generates content)
Write-Host "`n[4] Content Generation Test"
try {
    $body = @{
        model = "qwen3-coder-30b-a3b-instruct-int4-ov"
        messages = @(@{role="user"; content="Hi"})
        max_tokens = 50
    } | ConvertTo-Json

    $resp = Invoke-WebRequest -Uri "http://localhost:9000/v3/chat/completions" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 30

    $data = $resp.Content | ConvertFrom-Json
    $content = $data.choices[0].message.content

    if ($content -and $content.Length -gt 0) {
        Write-Host "✓ Model generates content: '$($content.Substring(0,[Math]::Min(50,$content.Length)))...'" -ForegroundColor Green
    } else {
        Write-Host "✗ Model response empty (BUG!)" -ForegroundColor Red
        Write-Host "   Full response: $($resp.Content | ConvertFrom-Json | ConvertTo-Json -Depth 1)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ API error: $_" -ForegroundColor Red
}

Write-Host "`n=== End Debug ===" -ForegroundColor Cyan
