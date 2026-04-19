# Setup: llama.cpp + OpenVINO + vcpkg (PowerShell)
# Offizielle Methode mit vcvars64.bat (Microsoft-empfohlen)
# Stefan Dohren - April 2026

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========== SETUP: llama.cpp + OpenVINO (vcpkg) ==========" -ForegroundColor Cyan
Write-Host ""

# ============ [1/5] Voraussetzungen ============
Write-Host "[1/5] Pruefe Voraussetzungen..." -ForegroundColor Yellow

$cmake = Get-Command cmake -ErrorAction SilentlyContinue
$ninja = Get-Command ninja -ErrorAction SilentlyContinue

if (-not $cmake) { Write-Host "FEHLER: CMake nicht gefunden" -ForegroundColor Red; exit 1 }
if (-not $ninja) { Write-Host "FEHLER: Ninja nicht gefunden" -ForegroundColor Red; exit 1 }

Write-Host "   OK CMake, Ninja" -ForegroundColor Green

# ============ [2/5] OpenVINO SDK ============
Write-Host ""
Write-Host "[2/5] OpenVINO SDK..." -ForegroundColor Yellow

if (-not (Test-Path "C:\LLM\openvino_sdk")) {
    Write-Host "   FEHLER: OpenVINO SDK nicht gefunden" -ForegroundColor Red
    exit 1
}

Write-Host "   OK OpenVINO SDK existiert" -ForegroundColor Green

# ============ [3/5] vcvars64.bat finden ============
Write-Host ""
Write-Host "[3/5] Finde vcvars64.bat..." -ForegroundColor Yellow

$vcvarsPath = $null

$vcvarsPossiblePaths = @(
    "C:\Program Files\Microsoft Visual Studio\2022\*\VC\Auxiliary\Build\vcvars64.bat",
    "C:\Program Files\Microsoft Visual Studio\2019\*\VC\Auxiliary\Build\vcvars64.bat",
    "C:\Program Files\Microsoft Visual Studio\18\*\VC\Auxiliary\Build\vcvars64.bat",
    "C:\Program Files (x86)\Microsoft Visual Studio\2022\*\VC\Auxiliary\Build\vcvars64.bat",
    "C:\Program Files (x86)\Microsoft Visual Studio\2019\*\VC\Auxiliary\Build\vcvars64.bat"
)

foreach ($pattern in $vcvarsPossiblePaths) {
    $found = Get-Item $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $vcvarsPath = $found.FullName
        Write-Host "   Gefunden: $vcvarsPath" -ForegroundColor Green
        break
    }
}

if (-not $vcvarsPath) {
    Write-Host "   FEHLER: vcvars64.bat nicht gefunden" -ForegroundColor Red
    exit 1
}

Write-Host "   Lade MSVC Umgebung..." -ForegroundColor Cyan
& cmd /c "call `"$vcvarsPath`" && set" | `
    ForEach-Object {
        if ($_ -match "^(.+?)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }

Write-Host "   OK MSVC Compiler bereit" -ForegroundColor Green

# ============ [4/5] vcpkg + OpenCL ============
Write-Host ""
Write-Host "[4/5] vcpkg und OpenCL installieren..." -ForegroundColor Yellow

if (-not (Test-Path "C:\LLM\vcpkg")) {
    Write-Host "   Klone vcpkg zu C:\LLM\vcpkg..." -ForegroundColor Cyan
    Set-Location C:\LLM
    & git clone https://github.com/Microsoft/vcpkg.git vcpkg

    if ($LASTEXITCODE -ne 0) {
        Write-Host "   FEHLER: vcpkg clone fehlgeschlagen" -ForegroundColor Red
        exit 1
    }
}

# Bootstrap vcpkg
if (-not (Test-Path "C:\LLM\vcpkg\vcpkg.exe")) {
    Write-Host "   Bootstrap vcpkg..." -ForegroundColor Cyan
    Set-Location C:\LLM\vcpkg
    & .\bootstrap-vcpkg.bat

    if ($LASTEXITCODE -ne 0) {
        Write-Host "   FEHLER: vcpkg bootstrap fehlgeschlagen" -ForegroundColor Red
        exit 1
    }
}

Write-Host "   OK vcpkg existiert" -ForegroundColor Green

# Installiere OpenCL
if (-not (Test-Path "C:\LLM\vcpkg\installed\x64-windows\lib\opencl.lib")) {
    Write-Host "   Installiere OpenCL via vcpkg (5-10 Min)..." -ForegroundColor Cyan
    Set-Location C:\LLM\vcpkg
    & .\vcpkg install opencl:x64-windows

    if ($LASTEXITCODE -ne 0) {
        Write-Host "   WARNUNG: OpenCL Installation fehlgeschlagen" -ForegroundColor Yellow
    }
}

Write-Host "   OK OpenCL installt" -ForegroundColor Green

# ============ [5/5] llama.cpp Build ============
Write-Host ""
Write-Host "[5/5] Baue llama.cpp mit OpenVINO..." -ForegroundColor Yellow

if (-not (Test-Path "C:\LLM\llama.cpp\build\ReleaseOV\bin\llama-server.exe")) {
    Set-Location C:\LLM\llama.cpp

    Write-Host "   Lade OpenVINO-Umgebung..." -ForegroundColor Cyan
    & cmd /c "call `"C:\LLM\openvino_sdk\setupvars.bat`" && set" | `
        ForEach-Object {
            if ($_ -match "^(.+?)=(.*)$") {
                [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
            }
        }

    Write-Host "   CMake konfiguriere mit vcpkg Toolchain..." -ForegroundColor Cyan
    & cmake -B build\ReleaseOV -G Ninja `
        -DCMAKE_BUILD_TYPE=Release `
        -DGGML_OPENVINO=ON `
        -DLLAMA_CURL=OFF `
        -DCMAKE_TOOLCHAIN_FILE=C:\LLM\vcpkg\scripts\buildsystems\vcpkg.cmake

    if ($LASTEXITCODE -ne 0) {
        Write-Host "   FEHLER: CMake-Konfiguration fehlgeschlagen" -ForegroundColor Red
        exit 1
    }

    Write-Host "   Kompiliere (5-10 Min)..." -ForegroundColor Cyan
    & cmake --build build\ReleaseOV --config Release --target llama-server

    if ($LASTEXITCODE -ne 0) {
        Write-Host "   FEHLER: Kompilation fehlgeschlagen" -ForegroundColor Red
        exit 1
    }

    Write-Host "   OK llama-server.exe kompiliert" -ForegroundColor Green
} else {
    Write-Host "   OK llama-server.exe existiert" -ForegroundColor Green
}

# ============ [6/5] DLLs + GGUF ============
Write-Host ""
Write-Host "[6/5] OpenVINO-DLLs und GGUF..." -ForegroundColor Yellow

$dllSource = "C:\LLM\openvino_sdk\runtime\bin\intel64\Release"
$dllDest = "C:\LLM\llama.cpp\build\ReleaseOV\bin"

if (Test-Path $dllSource) {
    Get-ChildItem $dllSource -Filter "*.dll" | Copy-Item -Destination $dllDest -Force
    Write-Host "   OK DLLs kopiert" -ForegroundColor Green
}

$ggufPath = "C:\LLM\models\gguf\Qwen3-Coder-30B-A3B-Instruct-IQ4_XS.gguf"
if (-not (Test-Path $ggufPath)) {
    Write-Host "   Installiere huggingface-hub..." -ForegroundColor Cyan
    & C:\LLM\.venv\Scripts\python -m pip install huggingface-hub -q

    Write-Host "   Lade GGUF herunter (16.4 GB - 30 Min)..." -ForegroundColor Cyan
    & C:\LLM\.venv\Scripts\huggingface-cli download `
        unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF `
        Qwen3-Coder-30B-A3B-Instruct-IQ4_XS.gguf `
        --local-dir C:\LLM\models\gguf\

    if ($LASTEXITCODE -ne 0) {
        Write-Host "   WARNUNG: GGUF Download fehlgeschlagen" -ForegroundColor Yellow
    } else {
        Write-Host "   OK GGUF heruntergeladen" -ForegroundColor Green
    }
} else {
    Write-Host "   OK GGUF existiert" -ForegroundColor Green
}

# ============ Zusammenfassung ============
Write-Host ""
Write-Host "========== SETUP ERFOLGREICH ==========" -ForegroundColor Green
Write-Host ""
Write-Host "Naechste Schritte:" -ForegroundColor Cyan
Write-Host "   1. Starte Server: C:\LLM\start_llama_openvino.bat"
Write-Host "   2. Warte 2-3 Min Model-Loading"
Write-Host "   3. Test: curl http://localhost:8080/health"
Write-Host ""

Read-Host "Druecke Enter zum Beenden"
