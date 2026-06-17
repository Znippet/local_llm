# OVMS Server Control Scripts

Einfache Verwaltung des OVMS Servers mit sauberen Start/Stop und PID-Tracking.

---

## Scripts

### 1. start_ovms_server.ps1

Startet OVMS Server, schreibt PID zu Datei.

```powershell
.\jinja_deployment\start_ovms_server.ps1
```

**Was es macht**:
- Prüft ob Port 9000 bereits in Benutzung (nicht doppelt starten)
- Startet OVMS mit allen nötigen Parametern
- Schreibt PID zu `.ovms_pid` Datei
- Wartet auf Startup (15 sekunden)
- Validiert API-Endpoint

**Output**:
```
✓ OVMS started (PID: 12345)
  PID saved to: C:\LLM\.ovms_pid

Waiting for server startup (15 seconds)...
✓ OVMS API responding

Ready for testing
```

### 2. stop_ovms_server.ps1

Stoppt OVMS Server via PID-Datei.

```powershell
.\jinja_deployment\stop_ovms_server.ps1
```

**Was es macht**:
- Liest PID aus `.ovms_pid` Datei
- Stoppt Prozess graceful (mit `CloseMainWindow`)
- Falls nötig, force-kill
- Validiert dass Prozess beendet wurde
- Cleanup PID-Datei
- Prüft dass Port 9000 frei ist

**Output**:
```
PID from file: 12345
Stopping OVMS (PID: 12345)...
✓ OVMS stopped successfully
✓ PID file cleaned up
✓ Port 9000 is free
```

---

## Complete Test Run

### Option 1: Automatisch (empfohlen)

Start, Phase5, Phase6, Stop — alles in einem:

```powershell
.\jinja_tests\run_all_tests.ps1
```

**Output**:
```
[1] Starting OVMS Server...
✓ OVMS started (PID: 12345)

[2] Validating OVMS Setup...
✓ All checks passed

[3] Running Phase 5 Tests (TC1-TC5)...
[PASS] TC1: PASS (0 errors)
[PASS] TC2: PASS (0 errors)
...
Total: 5/5 PASS

[4] Running Phase 6 Tests (TC6-TC9)...
[PASS] TC6: PASS (0 errors)
...
Total: 4/4 PASS

[5] Stopping OVMS Server...
✓ OVMS stopped successfully

Results:
  Phase 5 (TC1-TC5):     ✓ PASS
  Phase 6 (TC6-TC9):     ✓ PASS
```

### Option 2: Nur Phase 5 (schneller)

```powershell
.\jinja_tests\run_all_tests.ps1 -SkipPhase6
```

### Option 3: Manuell

Wenn du Server länger laufen lassen willst:

```powershell
# Start
.\jinja_deployment\start_ovms_server.ps1

# Mehrmals Tests laufen
python jinja_tests/run_jinja_phase5.py
python jinja_tests/run_jinja_phase5.py  # 2x
python jinja_tests/run_jinja_phase6.py

# Zum Schluss stoppen
.\jinja_deployment\stop_ovms_server.ps1
```

---

## Troubleshooting

### "API not responding yet"

Normal. Server braucht 15-30 sekunden zum Laden.

```powershell
# Warte 30 sekunden
Start-Sleep -Seconds 30

# Validiere manuell
.\jinja_deployment\validate_ovms_setup.ps1
```

### "OVMS already running"

```powershell
# Stoppe alte Instanz
.\jinja_deployment\stop_ovms_server.ps1

# Start neu
.\jinja_deployment\start_ovms_server.ps1
```

### Port 9000 in use (nicht OVMS)

```powershell
# Find wer Port benutzt
Get-NetTCPConnection -LocalPort 9000

# Kill process (falls nicht OVMS)
Stop-Process -Id <PID> -Force
```

### PID file missing bei Stop

Script fallback:
- Sucht nach OVMS Prozess by name
- Stoppt ihn

```powershell
.\jinja_deployment\stop_ovms_server.ps1
# Works auch ohne .ovms_pid file
```

---

## PID File Location

`.ovms_pid` in Projekt-Root:
```
C:\LLM\.ovms_pid
```

Enthält nur die PID Nummer:
```
12345
```

Automatisch erstellt bei Start, gelöscht bei Stop.

---

## Flow Diagram

```
Manual Start Path:
┌─────────────────────────────────────┐
│ start_ovms_server.ps1               │
│ - Checks Port 9000                  │
│ - Starts OVMS process               │
│ - Writes PID to .ovms_pid           │
│ - Waits for startup                 │
│ - Validates API                     │
└─────────────────────────────────────┘

Manual Stop Path:
┌─────────────────────────────────────┐
│ stop_ovms_server.ps1                │
│ - Reads PID from .ovms_pid          │
│ - Graceful shutdown                 │
│ - Force-kill if needed              │
│ - Validates stopped                 │
│ - Cleans up .ovms_pid               │
└─────────────────────────────────────┘

Automated Full Run:
┌─────────────────────────────────────┐
│ run_all_tests.ps1                   │
├─────────────────────────────────────┤
│ 1. start_ovms_server.ps1            │
│ 2. validate_ovms_setup.ps1          │
│ 3. run_jinja_phase5.py (TC1-TC5)    │
│ 4. run_jinja_phase6.py (TC6-TC9)    │
│ 5. stop_ovms_server.ps1             │
├─────────────────────────────────────┤
│ Output: Test results summary        │
└─────────────────────────────────────┘
```

---

## Common Commands

```powershell
# Start server
.\jinja_deployment\start_ovms_server.ps1

# Stop server
.\jinja_deployment\stop_ovms_server.ps1

# Full test suite (Start → Tests → Stop)
.\jinja_tests\run_all_tests.ps1

# Only Phase 5 (faster)
.\jinja_tests\run_all_tests.ps1 -SkipPhase6

# Manual validation
.\jinja_deployment\validate_ovms_setup.ps1

# Manual Phase 5 test (server must be running)
python jinja_tests\run_jinja_phase5.py

# Manual Phase 6 test
python jinja_tests\run_jinja_phase6.py

# Check server status
Get-Process ovms
Get-Content C:\LLM\.ovms_pid

# Force stop if stuck
Stop-Process -Name ovms -Force
```

---

## Next Steps

1. **Quick Test**:
   ```powershell
   .\jinja_tests\run_all_tests.ps1 -SkipPhase6
   ```

2. **Full Test** (includes Phase 6):
   ```powershell
   .\jinja_tests\run_all_tests.ps1
   ```

3. **Manual Testing** (server stays up):
   ```powershell
   .\jinja_deployment\start_ovms_server.ps1
   # Run tests multiple times
   python jinja_tests\run_jinja_phase5.py
   python jinja_tests\run_jinja_phase6.py
   # When done
   .\jinja_deployment\stop_ovms_server.ps1
   ```

---

## Notes

- **PID Tracking**: Verhindert doppelte Starts, einfacher Stop
- **Graceful Shutdown**: Erst `CloseMainWindow`, dann force-kill falls nötig
- **Automatic Fallback**: Wenn PID-file fehlt, sucht nach OVMS by name
- **Port Validation**: Prüft Port 9000 vor und nach
- **Error Handling**: Alle Fehler gemeldet, nie silent fails
