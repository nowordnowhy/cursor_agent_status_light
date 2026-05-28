# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

CursorLight is a BLE-powered desktop traffic light that visualizes AI coding state (thinking, executing, success, failure, awaiting user). An ESP32-C3 SuperMini drives a repurposed toy traffic light via PWM on IO2 (green), IO3 (yellow), IO4 (red) — common anode, so LOW = on. The ESP32 advertises as `CursorLight` over BLE and accepts mode strings written to a GATT characteristic.

Supports both **Cursor** and **Claude Code** via their respective hook systems. The same core scripts (`agent-light.sh`, `ble_gate.py`, `cursor_light_ble_enhanced.py`) serve both IDEs; only the hook wrapper scripts and configuration differ.

## Architecture

```
Cursor IDE (hooks.json)  /  Claude Code (settings.json)
  → hook-*.sh (thin wrappers: capture stdin → HOOK_INPUT, delegate to agent-light.sh)
    → agent-light.sh (core state machine, dual Cursor/Claude Code stdin format)
      → ble_gate.py (debounce/dedup gateway with file-based locking via state.json / state.lock)
        → cursor_light_ble_enhanced.py (bleak BLE client, writes mode to GATT characteristic)
          → ESP32-C3 firmware (LED animations via PWM)
```

`agent-light.sh` detects the IDE source via `HOOK_SOURCE` env var:
- `HOOK_SOURCE=claude-code` → Claude Code stdin JSON format (simplified: no Plan/Build logic)
- unset (default) → Cursor stdin JSON format (full Plan mode awareness)

**Hook entry points — Cursor** (install to `~/.cursor/hooks/cursor-light/`):
- `hook-turn-start.sh` — beforeSubmitPrompt
- `hook-thinking.sh` — preToolUse (thinking phase)
- `hook-busy.sh` — preToolUse (tool execution)
- `hook-await-user.sh` — preToolUse (AskQuestion matcher)
- `hook-stop.sh` — stop event
- `hook-idle.sh` — sessionEnd
- `hook-denied.sh` — postToolUseFailure
- `hook-plan-detect.sh` — afterAgentResponse (detects plan-awaiting-output patterns)
- `hook-plan-file.sh` — afterFileEdit (checks if a plan file is being written)
- `hook-plan-created.sh` — postToolUse (CreatePlan matcher)

**Hook entry points — Claude Code** (install to `~/.cursor-light/claude-code/`):
- `hook-turn-start.sh` — UserPromptSubmit → thinking
- `hook-busy.sh` — beforeToolUse → busy
- `hook-await-user.sh` — beforeToolUse (AskUserQuestion matcher) → alarm
- `hook-stop.sh` — Stop (completed → success, error/aborted → error)
- `hook-idle.sh` — SessionEnd → green
- `hook-denied.sh` — postToolUseFailure → error

**Supported light modes** (12 total): `demo`, `thinking`, `ai`, `busy`, `success`, `error`, `alarm`, `traffic`, `off`, `red`, `yellow`, `green`.

The ESP32 firmware has an auto-timeout: any mode (except `off`) reverts to `traffic` after 5 minutes; `traffic` reverts to `off` after 10 minutes.

## Commands

```bash
# Manual BLE control — macOS (requires: pip install bleak)
python3 cursor_light_ble_enhanced.py <mode>

# Manual BLE control — Windows
py -3 cursor_light_ble_enhanced.py <mode>

# Install for Cursor (from extracted bundle)
bash install-cursor-light.sh

# Install for Claude Code — macOS
bash install-claude-code.sh

# Install for Claude Code — Windows (PowerShell + Python)
py -3 install-claude-code.py

# Debug hook execution — Cursor (macOS)
tail -f ~/.cursor/hooks/cursor-light/ble.log

# Debug hook execution — Claude Code (macOS / Windows Git Bash)
tail -f ~/.cursor-light/ble.log

# Debug hook execution — Windows PowerShell
Get-Content "$env:USERPROFILE\.cursor-light\ble.log" -Wait

# Generate PDF migration guide (requires: pip install fpdf)
python3 generate-pdf-guide.py
```

The Arduino firmware (`.ino` file) is compiled and uploaded via Arduino IDE — target board: ESP32-C3 SuperMini. On macOS the serial port is `/dev/cu.usbmodem*`, on Windows `COM3`/`COM5` etc. If upload fails at `Connecting...`, hold BOOT → click Upload → release BOOT once writing begins.

## Platform notes

- All hook scripts are **bash**. On Windows, run them via Git Bash (`.ps1` alternatives don't exist yet).
- **File locking**: `ble_gate.py` uses `msvcrt` on Windows and `fcntl` on macOS/Linux. `agent-light.sh` inline Python scripts (Cursor path only) still depend on `fcntl`; these are not called in the Claude Code path.
- State is persisted in `state.json` at the install path (`~/.cursor-light/` for Claude Code, `~/.cursor/hooks/cursor-light/` for Cursor). If the light behaves erratically, deleting `state.json` and `state.lock` resets the debounce state.
- macOS: if BLE fails with "Bluetooth device is turned off" despite BT being on, grant Bluetooth permission to Terminal/iTerm/Cursor in **System Settings → Privacy & Security → Bluetooth**.
- **Windows settings.json paths**: Use forward slashes (`C:/Users/...`) for hook commands — Git Bash expects this format.
- **Claude Code vs Cursor**: The Claude Code hook path uses a simplified state machine — no Plan/Build detection. All tool failures map to `error`. The Cursor path retains full Plan mode awareness (CreatePlan → alarm, Build → busy, etc.).

## Key files

| File | Purpose |
|---|---|
| `ESP32_C3_ToyBoard_CommonAnode_BLE_Enhanced_CursorLight.ino` | Arduino firmware — BLE GATT server, PWM LED animations, 12 modes |
| `cursor-light-bundle.zip` | Deployable bundle: all hook scripts (Cursor + Claude Code), Python BLE tools, install scripts |
| `cursor-light-bundle/cursor-light-bundle/agent-light.sh` | Core state machine — routes IDE hook events to light modes, dual Cursor/Claude Code format |
| `cursor-light-bundle/cursor-light-bundle/ble_gate.py` | Debounce/dedup gateway with file-based locking |
| `cursor-light-bundle/cursor-light-bundle/claude-code/` | Claude Code hook wrapper scripts + settings.json.snippet |
| `README.md` | Bilingual (CN/EN) docs: hardware BOM, wiring, firmware flashing, hook installation |

When modifying the bundle, edit files in `cursor-light-bundle/cursor-light-bundle/` then re-zip.

**BLE identifiers** (hardcoded across firmware and Python):
- Device name: `CursorLight`
- Service UUID: `b8b7e001-7a6b-4f4f-9a8b-11c0ffee0001`
- Characteristic UUID: `b8b7e002-7a6b-4f4f-9a8b-11c0ffee0001`
