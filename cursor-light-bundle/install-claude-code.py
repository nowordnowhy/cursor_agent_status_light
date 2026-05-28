#!/usr/bin/env python3
# Install CursorLight for Claude Code on Windows
# Usage: py -3 install-claude-code.py
#
# This script:
#   1. Copies core scripts to %USERPROFILE%\.cursor-light\
#   2. Installs Python bleak dependency
#   3. Generates ~/.claude/settings.json hook config (or prints merge instructions)

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
DEST = HOME / ".cursor-light"
HOOKS_DIR = DEST / "claude-code"
SETTINGS_PATH = HOME / ".claude" / "settings.json"

# Determine source directory (where this script + bundle files live)
SRC = Path(__file__).resolve().parent


def main():
    print(f"==> Source: {SRC}")
    print(f"==> Target: {DEST}")

    DEST.mkdir(parents=True, exist_ok=True)
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)

    # Copy core scripts
    for fname in ["agent-light.sh", "ble_gate.py", "cursor_light_ble_enhanced.py"]:
        src = SRC / fname
        if src.exists():
            shutil.copy2(src, DEST / fname)
            print(f"  -> {fname}")

    # Copy claude-code hook scripts
    claude_src = SRC / "claude-code"
    if claude_src.is_dir():
        for f in claude_src.glob("*.sh"):
            shutil.copy2(f, HOOKS_DIR / f.name)
            print(f"  -> claude-code/{f.name}")

    # Init state/log files
    (DEST / "ble.log").touch(exist_ok=True)
    state_file = DEST / "state.json"
    if not state_file.exists():
        state_file.write_text("{}", encoding="utf-8")

    # Build hook config for settings.json
    base = str(DEST).replace("\\", "/")
    git_bash = shutil.which("bash") or "bash"

    hook_config = {
        "hooks": {
            "UserPromptSubmit": [
                {"command": f"{git_bash} {base}/claude-code/hook-turn-start.sh", "matcher": ""}
            ],
            "beforeToolUse": [
                {"command": f"{git_bash} {base}/claude-code/hook-busy.sh", "matcher": ""},
                {"command": f"{git_bash} {base}/claude-code/hook-await-user.sh", "matcher": "AskUserQuestion"},
            ],
            "Stop": [
                {"command": f"{git_bash} {base}/claude-code/hook-stop.sh", "matcher": ""}
            ],
            "postToolUseFailure": [
                {"command": f"{git_bash} {base}/claude-code/hook-denied.sh", "matcher": ""}
            ],
            "SessionEnd": [
                {"command": f"{git_bash} {base}/claude-code/hook-idle.sh", "matcher": ""}
            ],
        }
    }

    print()
    if SETTINGS_PATH.exists():
        print(f"[!] {SETTINGS_PATH} already exists.")
        print("    Merge the following hooks block manually:")
    else:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(hook_config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] Written {SETTINGS_PATH}")

    print()
    print(json.dumps(hook_config, indent=2, ensure_ascii=False))

    # Install Python deps
    print()
    print("==> Installing bleak (BLE library) ...")
    python = sys.executable or "python"
    subprocess.run([python, "-m", "pip", "install", "--user", "bleak"], check=False)

    # Self-test
    print()
    print("==> BLE self-test (ensure CursorLight is powered on nearby) ...")
    result = subprocess.run(
        [python, str(DEST / "cursor_light_ble_enhanced.py"), "green"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print("BLE test passed.")
    else:
        print("BLE test did not pass. Check Bluetooth permissions and hardware.")
        if result.stderr:
            print(f"  stderr: {result.stderr.strip()}")

    print()
    print("Done. Restart Claude Code to activate hooks.")
    print(f"Log: {DEST / 'ble.log'}")


if __name__ == "__main__":
    main()
