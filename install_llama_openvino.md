# llama.cpp + OpenVINO 2026.1 — Installationsanleitung

**Ziel:** llama-server auf Port 8080 mit OpenVINO-Backend für Lunar Lake iGPU installieren.

**Voraussetzungen:**

- Windows 11 Pro
- Visual Studio 2019+ mit C++ Desktop Workload
- CMake >= 3.25
- Ninja 1.13+
- Git
- Python 3.10+

**Gesamtdauer:** ~45 Min (inkl. 30 Min Model-Download)

---

## 0. Voraussetzungen installieren

Falls nicht vorhanden:

```powershell
# C++ Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools

# CMake
winget install Kitware.CMake

# Ninja
winget install Ninja-build.Ninja

# Git (falls nicht vorhanden)
winget install Git.Git
```

**Nach Installation:** PowerShell neustarten damit PATH aktualisiert wird.

---

## 1. OpenVINO 2026.1 SDK herunterladen

```powershell
# Manuell oder via PowerShell:
$url = "https://storage.openvinotoolkit.org/repositories/openvino/packages/2026.1/windows/w_openvino_toolkit_windows_2026.1.0.dev20260221_x86_64.zip"

Invoke-WebRequest -Uri $url -OutFile "C:\LLM\openvino_sdk.zip"

# Entpacken nach C:\LLM\openvino_sdk\
Expand-Archive -Path "C:\LLM\openvino_sdk.zip" -DestinationPath "C:\LLM\" -Force

# ZIP löschen
Remove-Item "C:\LLM\openvino_sdk.zip"

# Verifizieren
Test-Path "C:\LLM\openvino_sdk\setupvars.bat"  # Sollte $True sein
```

---

## 2. vcpkg und OpenCL installieren

```powershell
cd C:\LLM

# Klone vcpkg
git clone https://github.com/Microsoft/vcpkg.git vcpkg

cd vcpkg

# Bootstrap vcpkg (baut vcpkg.exe selbst)
.\bootstrap-vcpkg.bat

# Installiere OpenCL (benötigt für GPU)
.\vcpkg install opencl:x64-windows
```

**Wartezeit:** 5-10 Min

---

## 3. llama.cpp klonen und bauen

```powershell
cd C:\LLM

# Klone llama.cpp
git clone https://github.com/ggml-org/llama.cpp.git

cd llama.cpp

# Lade OpenVINO Umgebung
& "C:\LLM\openvino_sdk\setupvars.bat"

# Konfiguriere Build mit CMake (vcpkg Toolchain!)
cmake -B build\ReleaseOV -G Ninja `
  -DCMAKE_BUILD_TYPE=Release `
  -DGGML_OPENVINO=ON `
  -DLLAMA_CURL=OFF `
  -DCMAKE_TOOLCHAIN_FILE=C:\LLM\vcpkg\scripts\buildsystems\vcpkg.cmake

# Kompiliere
cmake --build build\ReleaseOV --config Release --target llama-server
```

**Wartezeit:** 5-10 Min

**Resultat:** `C:\LLM\llama.cpp\build\ReleaseOV\bin\llama-server.exe`

---

## 4. OpenVINO Runtime DLLs kopieren

```powershell
Copy-Item "C:\LLM\openvino_sdk\runtime\bin\intel64\Release\*.dll" `
          "C:\LLM\llama.cpp\build\ReleaseOV\bin\" -Force
```

Diese DLLs werden neben `llama-server.exe` benötigt, sonst: `error: openvino.dll not found`

---

## 5. GGUF-Modell herunterladen

Benutze huggingface

**Resultat:** `C:\LLM\models\gguf\Qwen3-Coder-30B-A3B-Instruct-IQ4_XS.gguf`

---

## 6. Server starten

```batch
C:\LLM\start_llama_openvino.bat
```

Der Skript:

1. Lädt OpenVINO Umgebung (`setupvars.bat`)
2. Startet `llama-server.exe` auf Port 8080
3. Lädt das GGUF-Modell in iGPU-Memory
4. Erkennt automatisch OpenVINO Device und GPU-Layers

**Erstes Startup:** 2-3 Min (Model Loading + OpenVINO Graph Compilation)

---

## 7. Testen

```bash
# Health Check (sollte 200 sein)
curl http://localhost:8080/health

# Test Completion
curl -X POST http://localhost:8080/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"qwen3\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello\"}], \"max_tokens\": 100}"
```

---

## 🧹 Cleanup (optional, nach erfolgreichem Start)

Nach dem ersten erfolgreichen Server-Start können diese Verzeichnisse gelöscht werden (sparen ~12 GB):

```powershell
# WICHTIG: Binary erst sichern!
Copy-Item "C:\LLM\llama.cpp\build\ReleaseOV\bin\llama-server.exe" `
          "C:\LLM\bin\llama-server.exe" -Force

# Dann Buildzeug löschen
Remove-Item C:\LLM\vcpkg -Recurse -Force
Remove-Item C:\LLM\llama.cpp -Recurse -Force
```

**ODER einfacher: Nicht löschen.** Build-Ordner (~10 GB) ist kein Problem, und bei Updates brauchst du llama.cpp sowieso wieder.

---

## 🆘 Fehlerbehebung

### CMake: "cl.exe nicht gefunden"

```powershell
# Starte mit vcvars64.bat:
& "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"

# Dann CMake erneut
cmake -B build\ReleaseOV -G Ninja ...
```

### "gguf_init_from_file: failed to open GGUF file"

Modell nicht heruntergeladen:

```powershell
C:\LLM\.venv\Scripts\python C:\LLM\download_gguf.py
```

### "OpenVINO: using device CPU" (statt GPU)

Lunar Lake iGPU wird nicht erkannt:

1. BIOS: Integrated Graphics Memory auf Maximum setzen
2. Oder nutze: `--device CPU` (funktioniert, nur langsamer)

### "Cannot find openvino.dll"

DLLs nicht kopiert:

```powershell
Copy-Item "C:\LLM\openvino_sdk\runtime\bin\intel64\Release\*.dll" `
          "C:\LLM\llama.cpp\build\ReleaseOV\bin\" -Force
```

---

## 📚 Quellen

- [llama.cpp GitHub](https://github.com/ggml-org/llama.cpp)
- [OpenVINO Release](https://github.com/openvinotoolkit/openvino/releases/tag/2026.1.0)
- [Unsloth Qwen3-Coder GGUF](https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF)

This error occurs because the input tensor you are passing to the OpenVINO GPU plugin does not match the dimensions expected by the Llama model. Specifically, the model expects a shape of [1, 2, 4, 128] (total 1024 elements), while the provided tensor is [1, 1, 2, 512] (total 1024 elements). Although the total element count is identical, OpenVINO requires exact dimensional alignment for static inputs.
GitHub
GitHub
+3
Common Root Causes
Static Input Shapes: Many OpenVINO models for Llama are exported with static shapes for performance. If you change batch sizes or sequence lengths without updating the model, this mismatch occurs.
Incorrect Layout: The GPU plugin is sensitive to the data layout (e.g., NCHW vs. NHWC). If the model was optimized for one and you provide another, the dimensions will not align even if the data is correct.
KV Cache Handling: In LLMs, this often happens at index 0 when initializing or updating Key-Value (KV) caches if the "past_key_values" shape was not correctly defined during export.
GitHub
GitHub
+3
How to Fix
Reshape the Model for Dynamic Input:
If you need flexibility in input sizes, use the OpenVINO Model Reshape API to set dynamic dimensions (using -1 or ov::Dimension::dynamic()) before compiling the model.
python

# Example: Allow dynamic sequence length

model.reshape({0: [1, 2, 4, 128]})
Verify Model Inputs via Benchmark Tool:
Use the OpenVINO Benchmark App with the -shape parameter to confirm exactly what the model expects.
bash
benchmark_app -m model.xml -d GPU -shape "[1,2,4,128]"
Check Llama.cpp / GenAI Integration:
If using llama.cpp with the OpenVINO backend, this may be a known bug in how "VIEW" tensors (offsets in memory) are handled. Ensure you are using the latest version or check for relevant patches on the OpenVINO GitHub Issues page.
